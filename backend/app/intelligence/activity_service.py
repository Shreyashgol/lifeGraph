"""Activity Intelligence: natural language -> structured activity (docs/08 §6)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.intelligence.base import IntelligenceService, to_prompt_value
from app.intelligence.proposals import ActivityProposal
from app.models.user import UserProfile


class ActivityIntelligenceService(IntelligenceService):
    prompt_name = "activity"

    async def reason(
        self,
        *,
        activity: str,
        timestamp: datetime,
        user_profile: UserProfile | None = None,
        context: dict[str, Any] | None = None,
    ) -> ActivityProposal | None:
        variables = {
            "activity": activity,
            "timestamp": timestamp.isoformat(),
            "user_profile": to_prompt_value(user_profile),
            "context": to_prompt_value(context or {}),
        }
        return await self._reason_json(variables, ActivityProposal)
