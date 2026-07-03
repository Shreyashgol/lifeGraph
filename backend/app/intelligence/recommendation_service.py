"""Recommendation Intelligence: insights -> actions (docs/08 §12)."""

from __future__ import annotations

from typing import Any

from app.intelligence.base import IntelligenceService, to_prompt_value
from app.intelligence.proposals import RecommendationProposal
from app.models.behaviour import BehaviourPattern
from app.models.insight import Insight


class RecommendationIntelligenceService(IntelligenceService):
    prompt_name = "recommendation"

    async def reason(
        self,
        *,
        insights: list[Insight],
        behaviour: list[BehaviourPattern],
        goals: list[str],
        preferences: dict[str, Any],
        active_projects: list[str],
    ) -> RecommendationProposal | None:
        variables = {
            "insights": to_prompt_value(insights),
            "behaviour": to_prompt_value(behaviour),
            "goals": to_prompt_value(goals),
            "preferences": to_prompt_value(preferences),
            "active_projects": to_prompt_value(active_projects),
        }
        return await self._reason_json(variables, RecommendationProposal)
