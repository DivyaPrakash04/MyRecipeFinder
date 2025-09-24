import os
from typing import List, Dict
from tavily import TavilyClient
from db import SessionLocal
from models import RecipeCache

tc = TavilyClient(api_key=os.getenv("TAVILY_API_KEY")) if os.getenv("TAVILY_API_KEY") else None

def search_recipes_tavily(query: str, dietary_context: str = "") -> List[Dict]:
    """
    Use Tavily to search the web for recipes, then return normalized items.
    Falls back to returning empty if Tavily not configured.
    
    Args:
        query: The search query
        dietary_context: Optional dietary context to include in the search
    """
    # Combine query with dietary context if provided
    if dietary_context:
        query = f"{query} {dietary_context}"
    if not tc:
        return []

    # Check cache first
    db = SessionLocal()
    try:
        cached = (
            db.query(RecipeCache)
            .filter(RecipeCache.query == query)
            .order_by(RecipeCache.created_at.desc())
            .limit(20)
            .all()
        )
        if cached:
            return [
                {"title": r.title, "sourceUrl": r.url, "summary": r.summary, "image": r.image}
                for r in cached
            ]
    finally:
        db.close()

    # Search Tavily
    search = tc.search(query=query, max_results=8)
    hits = search.get("results", [])
    items: List[Dict] = []
    for h in hits:
        items.append({
            "title": h.get("title"),
            "sourceUrl": h.get("url"),
            "summary": h.get("content") or h.get("snippet"),
            "image": None,
        })

    # Save to cache
    db = SessionLocal()
    try:
        for it in items:
            rec = RecipeCache(
                query=query,
                title=it.get("title") or "",
                url=it.get("sourceUrl") or "",
                summary=it.get("summary") or "",
                image=it.get("image"),
            )
            try:
                db.add(rec)
                db.commit()
            except Exception:
                db.rollback()
        return items
    finally:
        db.close()
