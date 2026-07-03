"""GET /timeline — the day's chronological activity."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.api.dependencies import get_session
from app.repositories.timeline_repository import TimelineRepository
from app.schemas.timeline import TimelineResponse

router = APIRouter(tags=["timeline"])


@router.get("/timeline", response_model=TimelineResponse)
def get_timeline(
    day: date | None = Query(default=None, alias="date"),
    session: Session = Depends(get_session),
) -> TimelineResponse:
    target = day or date.today()
    timeline = TimelineRepository(session).get_by_date(target)
    return (
        TimelineResponse.from_domain(timeline)
        if timeline is not None
        else TimelineResponse.empty(target)
    )
