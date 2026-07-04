"""AuthUser — the authenticated caller's identity.

Distinct from :class:`app.models.user.UserProfile`: ``AuthUser`` is the account
identity established at login (who you are), while ``UserProfile`` is the rich,
onboarded profile used for personalization (what we know about you). Both are
backed by the same ``users`` row.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from app.models.base import DomainModel


class AuthUser(DomainModel):
    """The identity of the currently authenticated user."""

    id: UUID
    email: str
    name: str
    picture: str | None = None
    # Internal only — the stored bcrypt hash. Excluded from any serialization so
    # it can never leak through an API response.
    hashed_password: str | None = Field(default=None, exclude=True, repr=False)
