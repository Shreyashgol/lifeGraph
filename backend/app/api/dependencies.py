"""Shared API dependencies.

The compiled graph is expensive to build, so it is created once and cached. Its
langgraph/Groq imports stay lazy here, so the app (and read-only endpoints)
start and serve without those installed — only ``POST /activity`` needs them.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from fastapi import HTTPException
from sqlmodel import Session

from app.database.session import engine, get_session
from app.intelligence.errors import IntelligenceError

__all__ = ["get_session", "session_factory", "get_compiled_graph", "get_graph"]


def session_factory() -> Session:
    """Create a new database session (used by the graph's Persist node)."""
    return Session(engine)


@lru_cache
def get_compiled_graph() -> Any:
    """Build and cache the compiled reasoning graph."""
    from app.graph.builder import build_graph
    from app.intelligence.groq_client import GroqClient

    return build_graph(
        llm_client=GroqClient(),
        session_factory=session_factory,
        checkpointer=None,
    )


def get_graph() -> Any:
    """FastAPI dependency: the compiled graph, or 503 if unavailable.

    Overridable in tests. Missing GROQ_API_KEY or an uninstalled reasoning
    dependency surfaces as a clean 503 rather than a 500.
    """
    try:
        return get_compiled_graph()
    except (IntelligenceError, ImportError) as exc:
        raise HTTPException(status_code=503, detail=f"reasoning engine unavailable: {exc}")
