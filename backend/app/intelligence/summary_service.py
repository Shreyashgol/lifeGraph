"""Summary Intelligence: the day's narrative in Markdown (docs/08 §13).

The only service that returns long-form text rather than a JSON proposal.
"""

from __future__ import annotations

from datetime import date

from app.intelligence.base import IntelligenceService, to_prompt_value
from app.models.behaviour import BehaviourPattern
from app.models.insight import Insight
from app.models.memory import Memory
from app.models.recommendation import Recommendation
from app.models.timeline import Timeline


class SummaryIntelligenceService(IntelligenceService):
    prompt_name = "summary"

    async def reason(
        self,
        *,
        today: date,
        timeline: Timeline | None,
        behaviour: list[BehaviourPattern],
        insights: list[Insight],
        recommendations: list[Recommendation],
        memories: list[Memory],
    ) -> str:
        variables = {
            "today": today.isoformat(),
            "timeline": to_prompt_value(timeline),
            "behaviour": to_prompt_value(behaviour),
            "insights": to_prompt_value(insights),
            "recommendations": to_prompt_value(recommendations),
            "memories": to_prompt_value(memories),
        }
        return await self._reason_text(variables)
