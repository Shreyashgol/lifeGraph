"""Session domain model (docs/07_DATA_MODELS.md §8).

A stretch of uninterrupted work on a single context, built from activities.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import Field, model_validator

from app.models.activity import Activity
from app.models.base import DomainModel


class Session(DomainModel):
    """Uninterrupted work on one context within the day."""

    start_time: datetime
    end_time: datetime
    duration: int = Field(ge=0, description="Session length in minutes.")
    activities: list[Activity] = Field(default_factory=list)
    dominant_category: str | None = None
    dominant_project: str | None = None
    focus_score: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def _end_after_start(self) -> "Session":
        """A session must end after it starts."""
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self
