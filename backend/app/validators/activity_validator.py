"""Business validation for activity proposals."""

from __future__ import annotations

from app.config.constants import MIN_ACTIVITY_CONFIDENCE
from app.intelligence.proposals import ActivityProposal
from app.validators.base import ValidationResult


class ActivityValidator:
    """Enforces activity business rules beyond schema validation."""

    def validate(self, proposal: ActivityProposal) -> ValidationResult:
        if not proposal.category.strip():
            return ValidationResult(False, "activity category is empty")
        if proposal.confidence < MIN_ACTIVITY_CONFIDENCE:
            return ValidationResult(
                False,
                f"activity confidence {proposal.confidence:.2f} below "
                f"{MIN_ACTIVITY_CONFIDENCE:.2f}",
            )
        return ValidationResult(True)
