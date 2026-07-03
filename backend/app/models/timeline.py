"""Timeline domain model (docs/07_DATA_MODELS.md §7).

The chronological reconstruction of a user's day. Unlike raw activities, the
timeline groups observations into meaningful sessions.
"""

from __future__ import annotations

from datetime import date

from pydantic import Field

from app.models.activity import Activity
from app.models.base import DomainModel
from app.models.session import Session


class Timeline(DomainModel):
    """A single day's ordered activities and sessions."""

    date: date
    activities: list[Activity] = Field(default_factory=list)
    sessions: list[Session] = Field(default_factory=list)
    total_duration: int = Field(default=0, ge=0, description="Total minutes for the day.")
    context_switches: int = Field(default=0, ge=0)
