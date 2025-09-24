import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import Response, stream_with_context
from dotenv import load_dotenv

from db import init_db, SessionLocal
from models import ChatSession, Message, UserProfile
from llm import generate_reply
from recipes import search_recipes_tavily

# If you later enable LangGraph, import run_graph and switch via use_graph flag
from llm_graph import run_graph

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").split(",")}})

# Initialize DB tables on startup
init_db()


def _startup_checks():
    """Log friendly startup warnings for missing keys/settings."""
    cohere_key_present = bool(os.getenv("COHERE_API_KEY") or os.getenv("CO_API_KEY"))
    if not cohere_key_present:
        app.logger.warning(
            "Cohere API key is not set. Set COHERE_API_KEY (preferred) or CO_API_KEY in backend/.env. "
            "Chat responses will fail until this is configured."
        )

    if not os.getenv("TAVILY_API_KEY"):
        app.logger.warning(
            "TAVILY_API_KEY is not set. /api/recipes/search will return empty results until configured."
        )

    if not os.getenv("DATABASE_URL"):
        app.logger.info(
            "DATABASE_URL not set; defaulting to SQLite at ./app.db for local development."
        )


_startup_checks()


@app.get("/health")
def health():
    return jsonify({"ok": True})


@app.post("/api/sessions")
def create_session():
    db = SessionLocal()
    try:
        s = ChatSession()
        db.add(s)
        db.commit()
        db.refresh(s)
        return jsonify({"session_id": s.id})
    finally:
        db.close()


@app.get("/api/chat/history")
def get_history():
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400
    db = SessionLocal()
    try:
        msgs = (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
            .all()
        )
        return jsonify([
            {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
            for m in msgs
        ])
    finally:
        db.close()


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    user_msg = (data.get("message") or "").strip()
    context = data.get("context")  # optional dict
    use_graph = bool(data.get("use_graph", True))

    if not session_id:
        return jsonify({"error": "session_id is required"}), 400
    if not user_msg:
        return jsonify({"error": "message is required"}), 400

    db = SessionLocal()
    try:
        sess = db.query(ChatSession).get(session_id)
        if not sess:
            return jsonify({"error": "invalid session_id"}), 404

        # persist user message
        db.add(Message(session_id=session_id, role="user", content=user_msg))
        db.commit()

        # Load history for context
        history = (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
            .all()
        )
        history_messages = [{"role": m.role, "content": m.content} for m in history]

        system_instructions = (
            "You are a helpful nutrition-aware cooking assistant. Prefer healthier substitutions, "
            "and structure recipes as ingredients then numbered steps. If a user health profile or "
            "selected recipe context is provided, use it."
        )

        # Guardrails: required keys
        if not (os.getenv("COHERE_API_KEY") or os.getenv("CO_API_KEY")):
            return jsonify({
                "error": "Missing Cohere API key. Set COHERE_API_KEY (preferred) or CO_API_KEY in backend/.env."
            }), 400
        if use_graph and not os.getenv("TAVILY_API_KEY"):
            return jsonify({
                "error": "Missing TAVILY_API_KEY. Set it in backend/.env or set use_graph=false to skip web search."
            }), 400

        # Use LangGraph orchestration when requested; fall back to direct LLM on errors
        if use_graph:
            try:
                reply = run_graph(session_id=session_id, user_message=user_msg, selected_context=context)
            except Exception as e:
                app.logger.exception("LangGraph pipeline failed, falling back to direct LLM: %s", e)
                reply = generate_reply(system_instructions, history_messages, user_msg, context)
        else:
            reply = generate_reply(system_instructions, history_messages, user_msg, context)

        # persist assistant reply (LangGraph would persist inside the graph instead)
        db.add(Message(session_id=session_id, role="assistant", content=reply))
        db.commit()

        return jsonify({"reply": reply})
    finally:
        db.close()


@app.get("/api/chat/stream")
def chat_stream():
    """Server-Sent Events streaming for chat responses.
    Consumes query params: session_id, message, use_graph (optional), context (optional JSON string)
    """
    session_id = request.args.get("session_id")
    user_msg = request.args.get("message", "").strip()
    use_graph = request.args.get("use_graph", "true").lower() == "true"
    ctx_raw = request.args.get("context", "")
    context = {}
    if ctx_raw:
        try:
            context = json.loads(ctx_raw)
        except Exception:
            context = {}

    if not session_id or not user_msg:
        return jsonify({"error": "Missing session_id or message"}), 400

    # Guardrails: required keys
    if not (os.getenv("COHERE_API_KEY") or os.getenv("CO_API_KEY")):
        return jsonify({
            "error": "Missing Cohere API key. Set COHERE_API_KEY (preferred) or CO_API_KEY in backend/.env."
        }), 400
    if use_graph and not os.getenv("TAVILY_API_KEY"):
        return jsonify({
            "error": "Missing TAVILY_API_KEY. Set it in backend/.env or set use_graph=false to skip web search."
        }), 400

    def generate_stream():
        db = SessionLocal()
        try:
            # persist user message
            db.add(Message(session_id=session_id, role="user", content=user_msg))
            db.commit()

            # load brief history
            history = (
                db.query(Message)
                .filter(Message.session_id == session_id)
                .order_by(Message.created_at.asc())
                .all()
            )
            history_messages = [{"role": m.role, "content": m.content} for m in history]

            system_instructions = (
                "You are a helpful nutrition-aware cooking assistant. Prefer healthier substitutions, "
                "and structure recipes as ingredients then numbered steps. If a user health profile or "
                "selected recipe context is provided, use it."
            )

            # get full reply (reusing existing logic for correctness), then chunk it
            try:
                if use_graph:
                    from llm_graph import run_graph
                    reply = run_graph(session_id=session_id, user_message=user_msg, selected_context=context)
                else:
                    reply = generate_reply(system_instructions, history_messages, user_msg, context)
            except Exception as e:
                yield f"data: ERROR: {str(e)}\n\n"
                return

            # persist assistant reply
            db.add(Message(session_id=session_id, role="assistant", content=reply))
            db.commit()

            # Stream in chunks
            chunk_size = 200
            for i in range(0, len(reply), chunk_size):
                chunk = reply[i:i+chunk_size]
                yield f"data: {chunk}\n\n"
            # signal end
            yield "event: end\ndata: done\n\n"
        finally:
            db.close()

    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return Response(stream_with_context(generate_stream()), headers=headers)


@app.get("/api/recipes/search")
def recipes_search():
    q = request.args.get("q", "")
    diet = request.args.get("diet", "")
    ingredients = request.args.get("ingredients", "")
    if not q and not ingredients:
        return jsonify({"error": "Provide q or ingredients"}), 400
    parts = [q]
    if diet:
        parts.append(f"diet:{diet}")
    if ingredients:
        parts.append(f"ingredients:{ingredients}")
    composed = " ".join([p for p in parts if p])
    results = search_recipes_tavily(composed)
    return jsonify(results)


@app.get("/api/profile")
def get_profile():
    db = SessionLocal()
    try:
        p = db.query(UserProfile).first()
        if not p:
            return jsonify({"diet": "", "allergens": "", "goals": ""})
        return jsonify({"diet": p.diet, "allergens": p.allergens, "goals": p.goals})
    finally:
        db.close()


@app.post("/api/profile")
def save_profile():
    data = request.get_json(silent=True) or {}
    diet = data.get("diet", "")
    allergens = data.get("allergens", "")
    goals = data.get("goals", "")
    db = SessionLocal()
    try:
        p = db.query(UserProfile).first()
        if not p:
            p = UserProfile(diet=diet, allergens=allergens, goals=goals)
            db.add(p)
        else:
            p.diet = diet
            p.allergens = allergens
            p.goals = goals
        db.commit()
        return jsonify({"ok": True})
    finally:
        db.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "4000")), debug=True)
