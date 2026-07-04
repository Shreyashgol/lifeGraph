"""Activity API schemas (request/response DTOs)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.activity import Activity


class LogActivityRequest(BaseModel):
    """Request body for ``POST /activity``."""

    activity: str = Field(min_length=1, description="Natural-language activity.")
    timestamp: datetime | None = Field(
        default=None, description="Optional occurrence time; defaults to now."
    )


class ActivityView(BaseModel):
    """Public view of a structured activity."""

    id: UUID
    timestamp: datetime
    category: str
    project: str | None = None
    duration: int
    intent: str | None = None
    confidence: float
    evaluation_score: float | None = None
    evaluation_reason: str | None = None
    validated: bool

    @classmethod
    def from_domain(cls, activity: Activity) -> ActivityView:
        return cls(
            id=activity.id,
            timestamp=activity.timestamp,
            category=activity.category,
            project=activity.project,
            duration=activity.duration,
            intent=activity.intent,
            confidence=activity.confidence,
            evaluation_score=activity.evaluation_score,
            evaluation_reason=activity.evaluation_reason,
            validated=activity.validated,
        )


class ActivityResponse(BaseModel):
    """Response for ``POST /activity``."""

    activity: ActivityView | None
    timeline_updated: bool = False
    errors: list[str] = Field(default_factory=list)
