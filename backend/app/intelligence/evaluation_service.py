"""Evaluation Intelligence: LLM-as-a-judge over another service's proposal.

The Evaluation service does not re-solve the task. It judges an already-produced
proposal and returns an :class:`EvaluationDecision` (approve / retry / reject)
with a score and actionable feedback. The graph consumes the decision and owns
the retry loop (max 2 quality-retries); this service only decides.

Version 1 judges the Activity proposal; the signature is generic so other
proposals can be judged later without changing the service.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.intelligence.base import IntelligenceService, to_prompt_value
from app.intelligence.proposals import EvaluationDecision


class EvaluationIntelligenceService(IntelligenceService):
    prompt_name = "evaluation"

    async def reason(
        self,
        *,
        activity: str,
        proposal: BaseModel,
        context: dict[str, Any] | None = None,
    ) -> EvaluationDecision | None:
        variables = {
            "activity": activity,
            "proposal": to_prompt_value(proposal),
            "context": to_prompt_value(context or {}),
        }
        return await self._reason_json(variables, EvaluationDecision)
