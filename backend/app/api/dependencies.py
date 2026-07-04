"""Shared API dependencies.

Two graphs are compiled and cached: the per-activity **ingest** graph and the
on-demand **summary/analysis** graph. Their langgraph/Groq imports stay lazy, so
the app and read-only endpoints start and serve without those installed — only
``POST /activity`` and ``POST /summary`` need them.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from fastapi import Depends, Header, HTTPException
from sqlmodel import Session

from app.auth import decode_access_token
from app.database.session import engine, get_session
from app.graph.state import LifeGraphState
from app.intelligence.errors import IntelligenceError
from app.models.account import AuthUser
from app.repositories.user_repository import UserRepository

__all__ = [
    "get_session",
    "session_factory",
    "get_current_user",
    "get_activity_graph",
    "get_summary_graph",
    "get_graph",
    "get_summary_graph_dep",
    "result_to_state",
]


def get_current_user(
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_session),
) -> AuthUser:
    """Resolve the authenticated user from the ``Authorization: Bearer`` token.

    Raises **401** when the token is missing, malformed, expired, or its account
    no longer exists. This is the gate that makes every data endpoint per-user.
    """
    unauthorized = HTTPException(
        status_code=401,
        detail="not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not authorization or not authorization.lower().startswith("bearer "):
        raise unauthorized
    user_id = decode_access_token(authorization[7:].strip())
    if user_id is None:
        raise unauthorized
    user = UserRepository(session).get_by_id(user_id)
    if user is None:
        raise unauthorized
    return user


def session_factory() -> Session:
    """Create a new database session (used by the graph's Persist node)."""
    return Session(engine)


def result_to_state(result: Any) -> LifeGraphState:
    """Coerce a graph invocation result into a LifeGraphState."""
    if isinstance(result, LifeGraphState):
        return result
    return LifeGraphState.model_validate(result)


@lru_cache
def get_activity_graph() -> Any:
    """Build and cache the per-activity ingest graph."""
    from app.graph.builder import build_activity_graph
    from app.intelligence.groq_client import GroqClient

    return build_activity_graph(
        llm_client=GroqClient(), session_factory=session_factory, checkpointer=None
    )


@lru_cache
def get_summary_graph() -> Any:
    """Build and cache the on-demand summary/analysis graph."""
    from app.graph.builder import build_summary_graph
    from app.intelligence.groq_client import GroqClient

    return build_summary_graph(
        llm_client=GroqClient(), session_factory=session_factory, checkpointer=None
    )


def _resolve(builder: Any) -> Any:
    try:
        return builder()
    except (IntelligenceError, ImportError) as exc:
        raise HTTPException(status_code=503, detail=f"reasoning engine unavailable: {exc}") from exc


def get_graph() -> Any:
    """FastAPI dependency: the activity graph, or 503 if unavailable."""
    return _resolve(get_activity_graph)


def get_summary_graph_dep() -> Any:
    """FastAPI dependency: the summary graph, or 503 if unavailable."""
    return _resolve(get_summary_graph)
