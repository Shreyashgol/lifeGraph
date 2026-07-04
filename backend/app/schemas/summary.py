"""Summary API schemas."""

from __future__ import annotations

from datetime import date as date_type
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.models.summary import DailySummary
from app.schemas.insight import InsightView
from app.schemas.recommendation import RecommendationView


class SummaryCalendarResponse(BaseModel):
    """Which days have data, for rendering the summary calendar.

    ``summary_dates`` are days with a generated summary; ``activity_dates`` are
    days with logged activity (a summary can be generated for these).
    """

    summary_dates: list[date_type]
    activity_dates: list[date_type]


class SummaryResponse(BaseModel):
    """Response for ``GET /summary``."""

    id: UUID
    date: date_type
    overview: str
    timeline: str
    metrics: dict[str, Any]
    insights: list[InsightView]
    recommendations: list[RecommendationView]
    tomorrow_focus: str

    @classmethod
    def from_domain(cls, summary: DailySummary) -> SummaryResponse:
        return cls(
            id=summary.id,
            date=summary.date,
            overview=summary.overview,
            timeline=summary.timeline,
            metrics=summary.metrics,
            insights=[InsightView.from_domain(i) for i in summary.insights],
            recommendations=[
                RecommendationView.from_domain(r) for r in summary.recommendations
            ],
            tomorrow_focus=summary.tomorrow_focus,
        )
