"""Reflection Intelligence: end-of-graph holistic QA (docs/08 §14).

Evaluates the whole reasoning pipeline before completion. Never generates new
business data. Distinct from the per-proposal Evaluation service.
"""

from __future__ import annotations

from typing import Any

from app.intelligence.base import IntelligenceService, to_prompt_value
from app.intelligence.proposals import ReflectionProposal


class ReflectionIntelligenceService(IntelligenceService):
    prompt_name = "reflection"

    async def reason(self, *, state: Any) -> ReflectionProposal | None:
        variables = {"state": to_prompt_value(state)}
        return await self._reason_json(variables, ReflectionProposal)
