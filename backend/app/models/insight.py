"""Insight domain model (docs/07_DATA_MODELS.md §11).

Insights explain *what has changed*. They never prescribe actions, and every
insight must reference supporting evidence.
"""

from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import Field

from app.models.base import DomainModel


class Insight(DomainModel):
    """An explainable observation about a change in the user's behaviour."""

    id: UUID = Field(default_factory=uuid4)
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[UUID] = Field(default_factory=list)
    importance: int = Field(default=0)
