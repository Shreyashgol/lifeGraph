"""Insight API schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from app.models.insight import Insight


class InsightView(BaseModel):
    id: UUID
    title: str
    description: str
    confidence: float
    importance: int

    @classmethod
    def from_domain(cls, insight: Insight) -> "InsightView":
        return cls(
            id=insight.id,
            title=insight.title,
            description=insight.description,
            confidence=insight.confidence,
            importance=insight.importance,
        )


class InsightsResponse(BaseModel):
    """Response for ``GET /insights``."""

    insights: list[InsightView]
    count: int
