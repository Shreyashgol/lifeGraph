"""Insight node: explain what changed. Owns ``insights``."""

from __future__ import annotations

from app.config.logging import get_logger
from app.graph.state import LifeGraphState
from app.intelligence.errors import IntelligenceError
from app.intelligence.insight_service import InsightIntelligenceService
from app.models.insight import Insight

_logger = get_logger("app.graph.nodes.insight")


class InsightNode:
    def __init__(self, service: InsightIntelligenceService) -> None:
        self.service = service

    async def __call__(self, state: LifeGraphState) -> dict:
        goals = state.user_profile.goals if state.user_profile else []
        try:
            proposal = await self.service.reason(
                behaviour=state.behaviour_patterns,
                timeline=state.timeline,
                memories=state.memories,
                goals=goals,
            )
        except IntelligenceError as exc:
            return {"errors": [*state.errors, f"insight: {exc}"]}

        if proposal is None:
            return {}

        insights = [
            Insight(
                title=i.title,
                description=i.description,
                confidence=i.confidence,
                importance=i.importance,
            )
            for i in proposal.insights
        ]
        return {"insights": insights}
