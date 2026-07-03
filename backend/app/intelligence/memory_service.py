"""Memory Intelligence: propose memory create/update/ignore (docs/08 §7)."""

from __future__ import annotations

from typing import Any

from app.intelligence.base import IntelligenceService, to_prompt_value
from app.intelligence.proposals import MemoryProposal
from app.models.activity import Activity
from app.models.memory import Memory


class MemoryIntelligenceService(IntelligenceService):
    prompt_name = "memory"

    async def reason(
        self,
        *,
        structured_activity: Activity,
        memories: list[Memory],
        context: dict[str, Any] | None = None,
    ) -> MemoryProposal | None:
        variables = {
            "structured_activity": to_prompt_value(structured_activity),
            "memories": to_prompt_value(memories),
            "context": to_prompt_value(context or {}),
        }
        return await self._reason_json(variables, MemoryProposal)
