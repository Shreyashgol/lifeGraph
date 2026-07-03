"""DailySummary domain model (docs/07_DATA_MODELS.md §13).

The primary user-facing artifact: the narrative produced for the user's day.
"""

from __future__ import annotations

from datetime import date
from typing import Any
from uuid import UUID, uuid4

from pydantic import Field

from app.models.base import DomainModel
from app.models.insight import Insight
from app.models.recommendation import Recommendation


class DailySummary(DomainModel):
    """An end-of-day intelligence report for the user."""

    id: UUID = Field(default_factory=uuid4)
    date: date
    overview: str = Field(min_length=1)
    timeline: str = Field(min_length=1, description="Narrative timeline (Markdown).")
    metrics: dict[str, Any] = Field(default_factory=dict)
    insights: list[Insight] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
    tomorrow_focus: str = Field(min_length=1)
