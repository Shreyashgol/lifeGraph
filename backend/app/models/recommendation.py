"""Recommendation domain model (docs/07_DATA_MODELS.md §12).

Recommendations convert understanding into action. Every recommendation must
carry its reason, supporting evidence, and expected impact — no generic advice.
"""

from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import Field

from app.models.base import DomainModel
from app.models.enums import Priority


class Recommendation(DomainModel):
    """A personalized, evidence-backed suggested action."""

    id: UUID = Field(default_factory=uuid4)
    title: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    evidence: list[UUID] = Field(default_factory=list)
    expected_impact: str = Field(min_length=1)
    priority: Priority
    confidence: float = Field(ge=0.0, le=1.0)
