"""Insight Intelligence: explain what changed (docs/08 §11)."""

from __future__ import annotations

from app.intelligence.base import IntelligenceService, to_prompt_value
from app.intelligence.proposals import InsightProposal
from app.models.behaviour import BehaviourPattern
from app.models.memory import Memory
from app.models.timeline import Timeline


class InsightIntelligenceService(IntelligenceService):
    prompt_name = "insight"

    async def reason(
        self,
        *,
        behaviour: list[BehaviourPattern],
        timeline: Timeline | None,
        memories: list[Memory],
        goals: list[str],
    ) -> InsightProposal | None:
        variables = {
            "behaviour": to_prompt_value(behaviour),
            "timeline": to_prompt_value(timeline),
            "memories": to_prompt_value(memories),
            "goals": to_prompt_value(goals),
        }
        return await self._reason_json(variables, InsightProposal)
