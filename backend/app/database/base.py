"""Persistence foundation: the SQLModel declarative base and datetime helpers.

SQLite has no native timezone support, so timestamps are stored as naive UTC and
re-hydrated as timezone-aware UTC on read. This keeps the domain models (which
use timezone-aware UTC) round-tripping cleanly through the database.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import SQLModel

# Single import point for the ORM metadata (used by init_db()).
metadata = SQLModel.metadata


def to_naive_utc(value: datetime | None) -> datetime | None:
    """Normalize a datetime to naive UTC for storage."""
    if value is None:
        return None
    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc)
    return value.replace(tzinfo=None)


def as_utc(value: datetime | None) -> datetime | None:
    """Re-hydrate a stored datetime as timezone-aware UTC."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
