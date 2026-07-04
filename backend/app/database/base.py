"""Persistence foundation: the SQLModel declarative base and datetime helpers.

SQLite has no native timezone support, so timestamps are stored as naive UTC and
re-hydrated as timezone-aware UTC on read. This keeps the domain models (which
use timezone-aware UTC) round-tripping cleanly through the database.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlmodel import SQLModel

# Single import point for the ORM metadata (used by init_db()).
metadata = SQLModel.metadata


def to_naive_utc(value: datetime | None) -> datetime | None:
    """Normalize a datetime to naive UTC for storage."""
    if value is None:
        return None
    if value.tzinfo is not None:
        value = value.astimezone(UTC)
    return value.replace(tzinfo=None)


def as_utc(value: datetime | None) -> datetime | None:
    """Re-hydrate a stored datetime as timezone-aware UTC."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
