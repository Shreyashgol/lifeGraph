"""POST /activity — log an activity and run the reasoning graph."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.dependencies import get_graph, get_session
from app.graph.state import LifeGraphState
from app.repositories.memory_repository import MemoryRepository
from app.repositories.timeline_repository import TimelineRepository
from app.repositories.user_repository import UserRepository
from app.schemas.activity import ActivityResponse, ActivityView, LogActivityRequest

router = APIRouter(tags=["activity"])


def _as_state(result: Any) -> LifeGraphState:
    """Coerce a graph invocation result into a LifeGraphState."""
    if isinstance(result, LifeGraphState):
        return result
    return LifeGraphState.model_validate(result)


@router.post("/activity", response_model=ActivityResponse)
async def log_activity(
    payload: LogActivityRequest,
    session: Session = Depends(get_session),
    graph: Any = Depends(get_graph),
) -> ActivityResponse:
    """Understand an activity, evolve memory/timeline, and return the result."""
    user = UserRepository(session).get_first()
    memories = MemoryRepository(session).list_active()
    timestamp = payload.timestamp or datetime.now(timezone.utc)
    timeline = TimelineRepository(session).get_by_date(timestamp.date())

    initial = LifeGraphState(
        current_activity=payload.activity,
        user_profile=user,
        memories=memories,
        timeline=timeline,
    )

    result = await graph.ainvoke(initial)
    state = _as_state(result)
    activity = state.structured_activity

    return ActivityResponse(
        activity=ActivityView.from_domain(activity) if activity is not None else None,
        timeline_updated=state.timeline is not None,
        errors=state.errors,
    )
