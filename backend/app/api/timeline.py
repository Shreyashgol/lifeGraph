"""GET /timeline — the day's chronological activity."""

from __future__ import annotations

from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.api.dependencies import get_current_user, get_session
from app.models.account import AuthUser
from app.repositories.timeline_repository import TimelineRepository
from app.schemas.timeline import TimelineResponse

router = APIRouter(tags=["timeline"])


@router.get("/timeline", response_model=TimelineResponse)
def get_timeline(
    day: date | None = Query(default=None, alias="date"),
    session: Session = Depends(get_session),
    current_user: AuthUser = Depends(get_current_user),
) -> TimelineResponse:
    # Activities are timestamped in UTC and keyed by their UTC date, so "today"
    # defaults to the UTC date to stay consistent (and not appear empty).
    target = day or datetime.now(UTC).date()
    timeline = TimelineRepository(session, str(current_user.id)).get_by_date(target)
    return (
        TimelineResponse.from_domain(timeline)
        if timeline is not None
        else TimelineResponse.empty(target)
    )
