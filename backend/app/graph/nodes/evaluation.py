"""Evaluation node: LLM-as-a-judge over the Activity proposal.

Writes the verdict onto ``structured_activity`` (score/reason/retry_count/
validated). The *routing* decision lives in ``app/graph/edges.py`` and reads
these fields; this node only judges. Reject or exhausted retries pin
``retry_count`` at the cap so the router stops looping (graceful degradation —
one bad proposal never aborts the pipeline).
"""

from __future__ import annotations

from app.config.constants import MAX_QUALITY_RETRIES
from app.config.logging import get_logger
from app.graph.state import LifeGraphState
from app.intelligence.errors import IntelligenceError
from app.intelligence.evaluation_service import EvaluationIntelligenceService

_logger = get_logger("app.graph.nodes.evaluation")


class EvaluationNode:
    def __init__(self, service: EvaluationIntelligenceService) -> None:
        self.service = service

    async def __call__(self, state: LifeGraphState) -> dict:
        activity = state.structured_activity
        if activity is None:
            return {}

        try:
            decision = await self.service.reason(
                activity=state.current_activity or "",
                proposal=activity,
                context=state.relevant_context,
            )
        except IntelligenceError as exc:
            # Could not evaluate — accept best-effort rather than abort.
            updated = activity.model_copy(update={"validated": True})
            return {"structured_activity": updated, "errors": [*state.errors, f"evaluation: {exc}"]}

        if decision is None:
            updated = activity.model_copy(update={"validated": True})
            return {"structured_activity": updated}

        if decision.decision == "approve":
            update = {
                "validated": True,
                "evaluation_score": decision.score,
                "evaluation_reason": decision.feedback,
            }
        elif decision.decision == "retry":
            update = {
                "validated": False,
                "evaluation_score": decision.score,
                "evaluation_reason": decision.retry_reason or decision.feedback,
                "retry_count": activity.retry_count + 1,
            }
        else:  # reject -> stop retrying
            update = {
                "validated": False,
                "evaluation_score": decision.score,
                "evaluation_reason": decision.retry_reason or decision.feedback,
                "retry_count": MAX_QUALITY_RETRIES,
            }

        return {"structured_activity": activity.model_copy(update=update)}
