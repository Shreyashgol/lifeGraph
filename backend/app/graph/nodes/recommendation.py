"""Recommendation node: insights -> actions. Owns ``recommendations``."""

from __future__ import annotations

from app.config.logging import get_logger
from app.graph.state import LifeGraphState
from app.intelligence.errors import IntelligenceError
from app.intelligence.recommendation_service import RecommendationIntelligenceService
from app.models.recommendation import Recommendation

_logger = get_logger("app.graph.nodes.recommendation")


class RecommendationNode:
    def __init__(self, service: RecommendationIntelligenceService) -> None:
        self.service = service

    async def __call__(self, state: LifeGraphState) -> dict:
        profile = state.user_profile
        try:
            proposal = await self.service.reason(
                insights=state.insights,
                behaviour=state.behaviour_patterns,
                goals=profile.goals if profile else [],
                preferences=profile.preferences if profile else {},
                active_projects=profile.active_projects if profile else [],
            )
        except IntelligenceError as exc:
            return {"errors": [*state.errors, f"recommendation: {exc}"]}

        if proposal is None:
            return {}

        recommendations = [
            Recommendation(
                title=r.title,
                reason=r.reason,
                expected_impact=r.expected_impact,
                priority=r.priority,
                confidence=r.confidence,
            )
            for r in proposal.recommendations
        ]
        return {"recommendations": recommendations}
