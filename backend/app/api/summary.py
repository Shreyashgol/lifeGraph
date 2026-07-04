"""Summary endpoints.

``POST /summary`` runs the on-demand analysis graph (behaviour → insight →
recommendation → summary → reflection) over a day's timeline and persists the
result. ``GET /summary`` reads the most recent (or a given day's) summary.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.api.dependencies import (
    get_current_user,
    get_session,
    get_summary_graph_dep,
    result_to_state,
)
from app.graph.state import LifeGraphState
from app.models.account import AuthUser
from app.repositories.memory_repository import MemoryRepository
from app.repositories.summary_repository import SummaryRepository
from app.repositories.timeline_repository import TimelineRepository
from app.repositories.user_repository import UserRepository
from app.schemas.summary import SummaryCalendarResponse, SummaryResponse

router = APIRouter(tags=["summary"])

# Substrings that identify a provider rate-limit / quota failure captured in the
# graph's ``errors``. Groq's 429 payload always carries at least one of these.
_RATE_LIMIT_MARKERS = ("rate_limit", "rate limit", "429", "too many requests")


def _is_rate_limited(errors: list[str]) -> bool:
    """True when the graph failed because the AI provider rate-limited us."""
    joined = " ".join(errors).lower()
    return any(marker in joined for marker in _RATE_LIMIT_MARKERS)


@router.post("/summary", response_model=SummaryResponse)
async def generate_summary(
    day: date | None = Query(default=None, alias="date"),
    session: Session = Depends(get_session),
    graph: Any = Depends(get_summary_graph_dep),
    current_user: AuthUser = Depends(get_current_user),
) -> SummaryResponse:
    """Generate (and persist) the day's summary, insights, and recommendations."""
    uid = str(current_user.id)
    target = day or datetime.now(UTC).date()
    timeline = TimelineRepository(session, uid).get_by_date(target)
    if timeline is None or not timeline.activities:
        raise HTTPException(status_code=400, detail=f"no activities on {target} to summarize")

    initial = LifeGraphState(
        user_id=uid,
        user_profile=UserRepository(session).get_profile(uid),
        timeline=timeline,
        memories=MemoryRepository(session, uid).list_active(),
    )

    result = await graph.ainvoke(initial)
    state = result_to_state(result)
    if state.daily_summary is None:
        if _is_rate_limited(state.errors):
            raise HTTPException(
                status_code=429,
                detail=(
                    "AI provider daily token limit reached. "
                    "Please try again later or switch to a higher-limit model."
                ),
            )
        raise HTTPException(status_code=502, detail="summary generation failed")
    return SummaryResponse.from_domain(state.daily_summary)


@router.get("/summary/dates", response_model=SummaryCalendarResponse)
def list_summary_dates(
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    session: Session = Depends(get_session),
    current_user: AuthUser = Depends(get_current_user),
) -> SummaryCalendarResponse:
    """List days that have a summary and days that have activity (for the calendar)."""
    uid = str(current_user.id)
    return SummaryCalendarResponse(
        summary_dates=SummaryRepository(session, uid).list_dates(start=start, end=end),
        activity_dates=TimelineRepository(session, uid).list_dates(start=start, end=end),
    )


@router.get("/summary", response_model=SummaryResponse)
def get_summary(
    day: date | None = Query(default=None, alias="date"),
    session: Session = Depends(get_session),
    current_user: AuthUser = Depends(get_current_user),
) -> SummaryResponse:
    repo = SummaryRepository(session, str(current_user.id))
    summary = repo.get_by_date(day) if day is not None else repo.get_latest()
    if summary is None:
        raise HTTPException(status_code=404, detail="no summary available")
    return SummaryResponse.from_domain(summary)
