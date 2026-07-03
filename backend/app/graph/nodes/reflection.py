"""Reflection node: holistic end-of-graph QA.

Reads the whole state; owns ``confidence_scores``, ``execution_metadata``, and
``errors``. Never creates new business data (docs/08 §14). A compact state
summary is sent to the model so large objects and internals are not leaked.
"""

from __future__ import annotations

from app.config.logging import get_logger
from app.graph.state import LifeGraphState
from app.intelligence.errors import IntelligenceError
from app.intelligence.reflection_service import ReflectionIntelligenceService

_logger = get_logger("app.graph.nodes.reflection")


class ReflectionNode:
    def __init__(self, service: ReflectionIntelligenceService) -> None:
        self.service = service

    async def __call__(self, state: LifeGraphState) -> dict:
        scores: dict[str, float] = {}
        if state.structured_activity is not None:
            scores["activity"] = state.structured_activity.confidence
        if state.memory_proposals:
            scores["memory"] = max(m.confidence for m in state.memory_proposals)
        if state.behaviour_patterns:
            scores["behaviour"] = max(b.confidence for b in state.behaviour_patterns)
        if state.insights:
            scores["insight"] = max(i.confidence for i in state.insights)
        if state.recommendations:
            scores["recommendation"] = max(r.confidence for r in state.recommendations)

        errors = list(state.errors)
        summary = {
            "activity_validated": bool(
                state.structured_activity and state.structured_activity.validated
            ),
            "memory_proposals": len(state.memory_proposals),
            "insights": len(state.insights),
            "recommendations": len(state.recommendations),
            "confidence_scores": scores,
            "errors": errors,
        }

        try:
            proposal = await self.service.reason(state=summary)
        except IntelligenceError as exc:
            errors = [*errors, f"reflection: {exc}"]
            proposal = None

        if proposal is not None and not proposal.approved:
            errors = [*errors, "reflection: pipeline not approved"]

        metadata = state.execution_metadata.model_copy(
            update={"validation_results": {"reflection_approved": bool(proposal and proposal.approved)}}
        )
        return {
            "confidence_scores": scores,
            "execution_metadata": metadata,
            "errors": errors,
        }
