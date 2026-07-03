"""Behaviour node: detect patterns from accumulated history. Owns ``behaviour_patterns``."""

from __future__ import annotations

from app.config.logging import get_logger
from app.graph.state import LifeGraphState
from app.intelligence.behaviour_service import BehaviourIntelligenceService
from app.intelligence.errors import IntelligenceError
from app.models.behaviour import BehaviourPattern

_logger = get_logger("app.graph.nodes.behaviour")


class BehaviourNode:
    def __init__(self, service: BehaviourIntelligenceService) -> None:
        self.service = service

    async def __call__(self, state: LifeGraphState) -> dict:
        try:
            proposal = await self.service.reason(
                timeline=state.timeline,
                memories=state.memories,
                user_profile=state.user_profile,
            )
        except IntelligenceError as exc:
            return {"errors": [*state.errors, f"behaviour: {exc}"]}

        if proposal is None:
            return {}

        patterns = [
            BehaviourPattern(
                category=p.category,
                title=p.title,
                description=p.description,
                confidence=p.confidence,
                trend=p.trend,
                importance=p.importance,
            )
            for p in proposal.patterns
        ]
        return {"behaviour_patterns": patterns}
