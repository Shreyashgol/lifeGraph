"""BehaviourPattern domain model (docs/07_DATA_MODELS.md §10).

A behavioural trend detected from accumulated history. Describes *how* the user
behaves, distinct from Memory (*what* is known about the user).
"""

from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import Field

from app.models.base import DomainModel
from app.models.enums import BehaviourCategory, TrendDirection


class BehaviourPattern(DomainModel):
    """A detected behavioural trend with a direction and supporting evidence."""

    id: UUID = Field(default_factory=uuid4)
    category: BehaviourCategory
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[UUID] = Field(default_factory=list)
    trend: TrendDirection = TrendDirection.UNKNOWN
    importance: int = Field(default=0)
