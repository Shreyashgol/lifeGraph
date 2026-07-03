"""Recommendation API schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from app.models.recommendation import Recommendation


class RecommendationView(BaseModel):
    id: UUID
    title: str
    reason: str
    expected_impact: str
    priority: str
    confidence: float

    @classmethod
    def from_domain(cls, rec: Recommendation) -> "RecommendationView":
        return cls(
            id=rec.id,
            title=rec.title,
            reason=rec.reason,
            expected_impact=rec.expected_impact,
            priority=rec.priority.value,
            confidence=rec.confidence,
        )


class RecommendationsResponse(BaseModel):
    """Response for ``GET /recommendations``."""

    recommendations: list[RecommendationView]
    count: int
