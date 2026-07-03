"""Summary node: generate the day's narrative. Owns ``daily_summary``.

The Summary service returns one Markdown document. Version 1 stores that document
in ``overview`` and derives the structured fields; splitting the Markdown into
DailySummary's individual sections is a later refinement (see design review).
"""

from __future__ import annotations

from datetime import date

from app.config.logging import get_logger
from app.graph.state import LifeGraphState
from app.intelligence.errors import IntelligenceError
from app.intelligence.summary_service import SummaryIntelligenceService
from app.models.summary import DailySummary

_logger = get_logger("app.graph.nodes.summary")


class SummaryNode:
    def __init__(self, service: SummaryIntelligenceService) -> None:
        self.service = service

    async def __call__(self, state: LifeGraphState) -> dict:
        day = (
            state.structured_activity.timestamp.date()
            if state.structured_activity
            else date.today()
        )
        try:
            markdown = await self.service.reason(
                today=day,
                timeline=state.timeline,
                behaviour=state.behaviour_patterns,
                insights=state.insights,
                recommendations=state.recommendations,
                memories=state.memories,
            )
        except IntelligenceError as exc:
            return {"errors": [*state.errors, f"summary: {exc}"]}

        total_duration = state.timeline.total_duration if state.timeline else 0
        activity_count = len(state.timeline.activities) if state.timeline else 0
        summary = DailySummary(
            date=day,
            overview=markdown,
            timeline=f"{activity_count} activities, {total_duration} minutes",
            metrics={"total_duration": total_duration, "activities": activity_count},
            insights=state.insights,
            recommendations=state.recommendations,
            tomorrow_focus="See the recommendations above.",
        )
        return {"daily_summary": summary}
