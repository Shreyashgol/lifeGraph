"""Behaviour Intelligence: detect patterns from history (docs/08 §8)."""

from __future__ import annotations

from app.intelligence.base import IntelligenceService, to_prompt_value
from app.intelligence.proposals import BehaviourProposal
from app.models.memory import Memory
from app.models.timeline import Timeline
from app.models.user import UserProfile


class BehaviourIntelligenceService(IntelligenceService):
    prompt_name = "behaviour"

    async def reason(
        self,
        *,
        timeline: Timeline | None,
        memories: list[Memory],
        user_profile: UserProfile | None = None,
    ) -> BehaviourProposal | None:
        variables = {
            "timeline": to_prompt_value(timeline),
            "memories": to_prompt_value(memories),
            "user_profile": to_prompt_value(user_profile),
        }
        return await self._reason_json(variables, BehaviourProposal)
