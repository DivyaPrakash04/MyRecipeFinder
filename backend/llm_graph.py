import os
import time
import logging
from typing import Optional, List, Dict, Any, Sequence
from typing_extensions import TypedDict, Annotated

from langgraph.graph import StateGraph, END
from langchain_cohere import ChatCohere

from recipes import search_recipes_tavily
from db import SessionLocal
from models import Message


class GraphState(TypedDict, total=False):
    query: Annotated[str, lambda x, y: y]
    history: Annotated[List[Dict[str, str]], lambda x, y: y]
    context: Annotated[Dict[str, Any], lambda x, y: y]
    needs_search: Annotated[bool, lambda x, y: y]
    route_taken: Annotated[str, lambda x, y: y]
    search_results: Annotated[List[Dict[str, Any]], lambda x, y: y]
    answer: Annotated[str, lambda x, y: y]


logger = logging.getLogger("llm_graph")


def _should_search(state: GraphState) -> GraphState:
    t0 = time.perf_counter()
    q = (state.get("query") or "").lower()
    # Heuristic routing: search if the user asks for latest/web-backed info
    trigger_words = [
        "latest",
        "recent",
        "news",
        "study",
        "research",
        "trending",
        "new",
        "202",
        "google",
        "web",
        "online",
        "search",
    ]
    state["needs_search"] = any(w in q for w in trigger_words)
    state["route_taken"] = "search" if state["needs_search"] else "generate"
    logger.info("route decision: %s (needs_search=%s) query='%s' dt=%.3fms",
                state["route_taken"], state["needs_search"], q[:120], (time.perf_counter()-t0)*1000)
    return state


def _do_search(state: GraphState) -> GraphState:
    t0 = time.perf_counter()
    # Build a dietary context string from provided context for better search
    ctx = state.get("context") or {}
    diet = ctx.get("diet") or ""
    allergens = ctx.get("allergens") or ""
    goals = ctx.get("goals") or ""
    dietary_context = ", ".join([p for p in [diet, allergens, goals] if p])

    # Perform Tavily web search via our recipes module (already handles API key + caching)
    query = state.get("query") or ""
    results = search_recipes_tavily(query=query, dietary_context=dietary_context)
    state["search_results"] = results or []
    logger.info("search results: %d dt=%.3fms", len(state["search_results"]), (time.perf_counter()-t0)*1000)
    return state


def _generate(state: GraphState) -> GraphState:
    t0 = time.perf_counter()
    # Initialize Cohere chat via LangChain integration (reads COHERE_API_KEY from env)
    llm = ChatCohere(model=os.getenv("LLM_MODEL", "command-r"), temperature=0.3)

    # System instructions + context
    ctx = state.get("context") or {}
    selected_recipe = ctx.get("selectedRecipe") or {}
    health_profile = {
        "diet": ctx.get("diet"),
        "allergens": ctx.get("allergens"),
        "goals": ctx.get("goals"),
    }

    system_instructions = (
        "You are a helpful health-focused cooking assistant. Personalize suggestions for wellness, "
        "clear nutrition, and practical, quick steps. When relevant, provide ingredient substitutions, "
        "prep tips, and portion guidance. Keep sodium and added sugars in check if the user indicates."
    )

    search_snippets = ""
    if state.get("search_results"):
        parts = []
        for r in state["search_results"][:5]:
            title = r.get("title") or "Result"
            url = r.get("url") or ""
            snippet = r.get("snippet") or r.get("content") or ""
            parts.append(f"- {title}: {snippet}\n  {url}")
        search_snippets = "\n\nRecent findings (web):\n" + "\n".join(parts)

    selected_snippet = ""
    if selected_recipe:
        selected_snippet = (
            "\n\nSelected recipe context (from UI):\n"
            f"Title: {selected_recipe.get('title','')}\n"
            f"Ingredients: {', '.join(selected_recipe.get('ingredients', [])) if isinstance(selected_recipe.get('ingredients'), list) else selected_recipe.get('ingredients','')}\n"
            f"Summary: {selected_recipe.get('summary','')}\n"
        )

    profile_snippet = (
        "\n\nUser health profile:\n"
        f"Diet: {health_profile.get('diet') or ''}\n"
        f"Allergens: {health_profile.get('allergens') or ''}\n"
        f"Goals: {health_profile.get('goals') or ''}\n"
    )

    # Include brief history for continuity
    hist = state.get("history") or []
    history_snippet_lines: List[str] = []
    for m in hist[-10:]:
        role = m.get("role", "user").upper()
        content = (m.get("content") or "").strip()
        if content:
            history_snippet_lines.append(f"{role}: {content}")
    history_snippet = "\n".join(history_snippet_lines)

    user_query = state.get("query") or ""

    prompt = f"""
{system_instructions}
{profile_snippet}{selected_snippet}{search_snippets}

Prior conversation (latest first):
{history_snippet}

User request:
{user_query}

Provide a concise, actionable response with step-by-step guidance when appropriate. Cite links if used.
""".strip()

    resp = llm.invoke(prompt)
    # lc messages often return an AIMessage with .content as string
    answer = getattr(resp, "content", None) or str(resp)
    answer = (answer or "").strip()

    # Max output guard (characters); configurable via env
    try:
        max_chars = int(os.getenv("LLM_MAX_CHARS", "2500"))
    except ValueError:
        max_chars = 2500
    if len(answer) > max_chars:
        answer = answer[:max_chars].rstrip() + "\n\n...(trimmed)"

    dt = (time.perf_counter()-t0)*1000
    logger.info("generate done dt=%.3fms answer_chars=%d", dt, len(answer))
    state["answer"] = answer
    return state


# Build the graph once at import time for performance
_graph = StateGraph(GraphState)
_graph.add_node("route", _should_search)
_graph.add_node("search", _do_search)
_graph.add_node("generate", _generate)

# Edges: route -> search or generate
_graph.add_edge("route", "search")
_graph.add_edge("route", "generate")
_graph.add_edge("search", "generate")
_graph.add_edge("generate", END)

# Conditional routing function

def _router(state: GraphState) -> str:
    return "search" if state.get("needs_search") else "generate"

_graph.add_conditional_edges("route", _router)

# Set entry point so `route` is reachable
_graph.set_entry_point("route")

_compiled = _graph.compile()


def run_graph(session_id: str, user_message: str, selected_context: Optional[Dict[str, Any]] = None) -> str:
    """Entry point used by app.py when use_graph is true.
    selected_context is the object our UI sends for a selected recipe and/or health profile.
    """
    # Pull last 10 messages from DB for continuity
    history: List[Dict[str, str]] = []
    db = SessionLocal()
    try:
        msgs = (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
            .all()
        )
        for m in msgs[-10:]:
            history.append({"role": m.role, "content": m.content})
    finally:
        db.close()

    # Initialize all fields with default values
    initial: GraphState = {
        "query": user_message,
        "history": history,
        "context": selected_context or {},
        "needs_search": False,
        "route_taken": "",
        "search_results": [],
        "answer": ""
    }
    final = _compiled.invoke(initial)
    return final.get("answer", "")
