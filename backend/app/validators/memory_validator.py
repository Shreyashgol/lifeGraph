"""Business validation for memory proposals.

Enforces the core memory rule: memory is earned. A single observation may
propose a *candidate* memory, but activation requires accumulated evidence and
sufficient confidence.
"""

from __future__ import annotations

from app.config.constants import MEMORY_ACTIVATION_CONFIDENCE, MEMORY_EVIDENCE_THRESHOLD
from app.intelligence.proposals import MemoryProposal
from app.validators.base import ValidationResult


class MemoryValidator:
    """Enforces memory business rules beyond schema validation."""

    def validate(self, proposal: MemoryProposal) -> ValidationResult:
        if proposal.action == "ignore":
            return ValidationResult(True, "ignored")
        if not proposal.statement or not proposal.statement.strip():
            return ValidationResult(False, "memory proposal missing statement")
        if proposal.type is None:
            return ValidationResult(False, "memory proposal missing type")
        return ValidationResult(True)

    @staticmethod
    def should_activate(evidence_count: int, confidence: float) -> bool:
        """Whether a memory has enough evidence/confidence to become ACTIVE."""
        return (
            evidence_count >= MEMORY_EVIDENCE_THRESHOLD
            and confidence >= MEMORY_ACTIVATION_CONFIDENCE
        )
