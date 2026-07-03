"""GET /insights — explainable observations from the latest summary.

Insights are persisted within the daily summary (docs/07 §16), so this endpoint
reads them from the latest (or a given day's) summary.
"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.api.dependencies import get_session
from app.repositories.summary_repository import SummaryRepository
from app.schemas.insight import InsightsResponse, InsightView

router = APIRouter(tags=["insights"])


@router.get("/insights", response_model=InsightsResponse)
def get_insights(
    day: date | None = Query(default=None, alias="date"),
    session: Session = Depends(get_session),
) -> InsightsResponse:
    repo = SummaryRepository(session)
    summary = repo.get_by_date(day) if day is not None else repo.get_latest()
    insights = summary.insights if summary is not None else []
    views = [InsightView.from_domain(i) for i in insights]
    return InsightsResponse(insights=views, count=len(views))
