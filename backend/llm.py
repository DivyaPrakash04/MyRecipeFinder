import os
import cohere

_co_client = None

def _get_client() -> cohere.Client:
    global _co_client
    if _co_client is not None:
        return _co_client
    # Support both env var names
    api_key = os.getenv("COHERE_API_KEY") or os.getenv("CO_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing Cohere API key. Set COHERE_API_KEY (preferred) or CO_API_KEY in backend/.env."
        )
    _co_client = cohere.Client(api_key)
    return _co_client


def generate_reply(system_instructions: str, history: list[dict], user_message: str, extra_context: dict | None = None) -> str:
    """
    Cohere chat helper.
    history: list of {"role": "user"|"assistant", "content": str}
    extra_context: optional dict (e.g., health profile or selected recipe)
    """
    co = _get_client()

    # Prefer Responses API if available (newer SDKs)
    if hasattr(co, "responses") and hasattr(co.responses, "create"):
        messages: list[dict] = []
        preamble_parts = []
        if system_instructions:
            preamble_parts.append(system_instructions)
        if extra_context:
            preamble_parts.append(f"User health profile/context: {extra_context}")
        # Some responses implementations accept a leading system message
        if preamble_parts:
            messages.append({"role": "system", "content": "\n\n".join(preamble_parts)})

        for m in history[-12:]:
            role = "user" if m.get("role") == "user" else "assistant"
            messages.append({"role": role, "content": m.get("content", "")})
        messages.append({"role": "user", "content": user_message})

        resp = co.responses.create(
            model=os.getenv("LLM_MODEL", "command-r-plus"),
            messages=messages,
            temperature=0.3,
        )
        # Try the common fields first
        text = getattr(resp, "output_text", None) or getattr(resp, "text", None)
        if text:
            return str(text).strip()
        return str(resp).strip()

    # Fallback: legacy Chat API uses message + chat_history + preamble
    preamble = ""
    if system_instructions:
        preamble += system_instructions
    if extra_context:
        preamble += ("\n\n" if preamble else "") + f"User health profile/context: {extra_context}"

    # Convert history to Cohere chat history schema
    chat_history = []
    for m in history[-12:]:
        role = m.get("role")
        text = m.get("content", "")
        if role == "user":
            chat_history.append({"role": "USER", "message": text})
        else:
            chat_history.append({"role": "CHATBOT", "message": text})

    resp = co.chat(
        model=os.getenv("LLM_MODEL", "command-r-plus"),
        message=user_message,
        chat_history=chat_history if chat_history else None,
        preamble=preamble or None,
        temperature=0.3,
    )
    # Legacy chat returns .text
    if hasattr(resp, "text") and resp.text:
        return resp.text.strip()
    return str(resp).strip()
