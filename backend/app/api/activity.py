"""POST /activity — log an activity and run the reasoning graph."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.dependencies import get_graph, get_session, result_to_state
from app.graph.state import LifeGraphState
from app.repositories.memory_repository import MemoryRepository
from app.repositories.timeline_repository import TimelineRepository
from app.repositories.user_repository import UserRepository
from app.schemas.activity import ActivityResponse, ActivityView, LogActivityRequest

router = APIRouter(tags=["activity"])


@router.post("/activity", response_model=ActivityResponse)
async def log_activity(
    payload: LogActivityRequest,
    session: Session = Depends(get_session),
    graph: Any = Depends(get_graph),
) -> ActivityResponse:
    """Understand an activity, evolve memory/timeline, and return the result."""
    user = UserRepository(session).get_first()
    memories = MemoryRepository(session).list_active()
    timestamp = payload.timestamp or datetime.now(UTC)
    timeline = TimelineRepository(session).get_by_date(timestamp.date())

    initial = LifeGraphState(
        current_activity=payload.activity,
        user_profile=user,
        memories=memories,
        timeline=timeline,
    )

    result = await graph.ainvoke(initial)
    state = result_to_state(result)
    activity = state.structured_activity

    return ActivityResponse(
        activity=ActivityView.from_domain(activity) if activity is not None else None,
        timeline_updated=state.timeline is not None,
        errors=state.errors,
    )
