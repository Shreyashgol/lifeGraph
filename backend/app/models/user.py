"""UserProfile domain model (docs/07_DATA_MODELS.md §5).

The central intelligence model around which personalization is built — not
merely an account. Created during onboarding and updated by the Memory and
Behaviour nodes as understanding evolves.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import Field, field_validator

from app.models.base import DomainModel, utcnow


class UserProfile(DomainModel):
    """Long-term profile and stable knowledge about a user."""

    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1)
    occupation: str = Field(min_length=1)
    timezone: str = Field(description="IANA timezone, e.g. 'Asia/Kolkata'.")
    goals: list[str] = Field(min_length=1, description="At least one long-term goal.")
    interests: list[str] = Field(default_factory=list)
    active_projects: list[str] = Field(default_factory=list)
    preferences: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    @field_validator("name", "occupation")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        """Reject whitespace-only values and normalize surrounding whitespace."""
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be blank")
        return stripped

    @field_validator("timezone")
    @classmethod
    def _valid_iana_timezone(cls, value: str) -> str:
        """Ensure the timezone is a resolvable IANA identifier."""
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValueError(f"invalid IANA timezone: {value!r}") from exc
        return value

    @field_validator("active_projects")
    @classmethod
    def _unique_projects(cls, value: list[str]) -> list[str]:
        """Projects must be unique."""
        if len(set(value)) != len(value):
            raise ValueError("active_projects must be unique")
        return value
