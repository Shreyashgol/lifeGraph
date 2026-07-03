"""User / onboarding API schemas."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.user import UserProfile


class OnboardingRequest(BaseModel):
    """Request body for ``POST /onboarding``."""

    name: str = Field(min_length=1)
    occupation: str = Field(min_length=1)
    timezone: str = Field(description="IANA timezone, e.g. 'Asia/Kolkata'.")
    goals: list[str] = Field(min_length=1)
    interests: list[str] = Field(default_factory=list)
    active_projects: list[str] = Field(default_factory=list)
    preferences: dict[str, Any] = Field(default_factory=dict)


class ProfileResponse(BaseModel):
    """Response for onboarding and ``GET /profile``."""

    id: UUID
    name: str
    occupation: str
    timezone: str
    goals: list[str]
    interests: list[str]
    active_projects: list[str]
    preferences: dict[str, Any]

    @classmethod
    def from_domain(cls, profile: UserProfile) -> "ProfileResponse":
        return cls(
            id=profile.id,
            name=profile.name,
            occupation=profile.occupation,
            timezone=profile.timezone,
            goals=profile.goals,
            interests=profile.interests,
            active_projects=profile.active_projects,
            preferences=profile.preferences,
        )
