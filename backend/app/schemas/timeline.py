"""Timeline API schemas."""

from __future__ import annotations

from datetime import date as date_type

from pydantic import BaseModel

from app.models.timeline import Timeline
from app.schemas.activity import ActivityView


class TimelineResponse(BaseModel):
    """Response for ``GET /timeline``."""

    date: date_type
    activities: list[ActivityView]
    total_duration: int
    context_switches: int
    session_count: int

    @classmethod
    def from_domain(cls, timeline: Timeline) -> TimelineResponse:
        return cls(
            date=timeline.date,
            activities=[ActivityView.from_domain(a) for a in timeline.activities],
            total_duration=timeline.total_duration,
            context_switches=timeline.context_switches,
            session_count=len(timeline.sessions),
        )

    @classmethod
    def empty(cls, day: date_type) -> TimelineResponse:
        return cls(
            date=day,
            activities=[],
            total_duration=0,
            context_switches=0,
            session_count=0,
        )
