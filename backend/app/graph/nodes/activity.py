"""Activity node: raw text -> structured Activity.

On an Evaluation-driven retry, the previous proposal's ``evaluation_reason`` is
injected as corrective feedback and the retry count is carried forward. Reads
``current_activity`` (+ profile/context); owns ``structured_activity``.
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.config.logging import get_logger
from app.graph.state import LifeGraphState
from app.intelligence.activity_service import ActivityIntelligenceService
from app.intelligence.errors import IntelligenceError
from app.models.activity import Activity
from app.validators.activity_validator import ActivityValidator

_logger = get_logger("app.graph.nodes.activity")


class ActivityNode:
    def __init__(
        self, service: ActivityIntelligenceService, validator: ActivityValidator
    ) -> None:
        self.service = service
        self.validator = validator

    async def __call__(self, state: LifeGraphState) -> dict:
        previous = state.structured_activity
        retry_count = previous.retry_count if previous else 0
        timestamp = previous.timestamp if previous else datetime.now(UTC)

        context = dict(state.relevant_context)
        if previous is not None and retry_count > 0 and previous.evaluation_reason:
            context["evaluation_feedback"] = previous.evaluation_reason

        try:
            proposal = await self.service.reason(
                activity=state.current_activity or "",
                timestamp=timestamp,
                user_profile=state.user_profile,
                context=context,
            )
        except IntelligenceError as exc:
            return {"errors": [*state.errors, f"activity: {exc}"]}

        if proposal is None:
            return {"errors": [*state.errors, "activity: insufficient_context"]}

        result = self.validator.validate(proposal)
        activity = Activity(
            timestamp=timestamp,
            raw_text=state.current_activity or "",
            category=proposal.category,
            subcategory=proposal.subcategory,
            duration=proposal.duration,
            intent=proposal.intent,
            project=proposal.project,
            people=proposal.people,
            location=proposal.location,
            confidence=proposal.confidence,
            retry_count=retry_count,
            validated=False,
            evaluation_reason=None if result.ok else result.reason,
        )
        return {"structured_activity": activity}
