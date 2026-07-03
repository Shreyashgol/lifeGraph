"""Activity domain model (docs/07_DATA_MODELS.md §6).

A structured activity extracted from natural language. Activities are immutable
observations — never long-term knowledge — and are never updated after
validation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import Field

from app.models.base import DomainModel


class Activity(DomainModel):
    """One structured observation of something the user did."""

    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(description="When the activity occurred.")
    raw_text: str = Field(min_length=1, description="Original natural-language input.")
    normalized_text: str | None = None
    category: str = Field(min_length=1, description="e.g. Deep Work, Meeting, Learning.")
    subcategory: str | None = None
    duration: int = Field(default=0, ge=0, description="Duration in minutes.")
    intent: str | None = None
    project: str | None = None
    people: list[str] = Field(default_factory=list)
    location: str | None = None
    confidence: float = Field(ge=0.0, le=1.0, description="AI confidence in the parse.")
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Evaluation metadata (docs/08 §Evaluation) — populated by the Evaluation
    # node's LLM-as-a-judge pass. Retained on the activity for later analytics.
    evaluation_score: float | None = Field(default=None, ge=0.0, le=1.0)
    evaluation_reason: str | None = None
    retry_count: int = Field(default=0, ge=0)
    validated: bool = False
