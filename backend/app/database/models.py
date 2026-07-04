"""SQLModel persistence entities (docs/07_DATA_MODELS.md §16).

These tables are optimized for storage, not business logic. They mirror the
domain models but flatten collections and nested aggregates into JSON columns —
repositories perform the domain <-> persistence conversion.

Tables: users, activities, memories, timelines, summaries (docs/15_DATABASE_SCHEMA.md).
The ``metadata`` domain field is mapped to a column named ``metadata`` via the
``metadata_`` attribute, because ``metadata`` is reserved by SQLAlchemy's
declarative base.
"""

from __future__ import annotations

from datetime import date as date_type
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class UserTable(SQLModel, table=True):
    """Persistence entity for a user account + :class:`app.models.user.UserProfile`.

    One row is both the *account* (email, password/Google identity) and the
    *profile* (occupation, goals, …). Profile fields are nullable/empty until the
    user completes onboarding.
    """

    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str | None = None  # null for Google-only accounts
    name: str
    picture: str | None = None
    # Profile fields — filled in at onboarding.
    occupation: str | None = None
    timezone: str | None = None
    goals: list[str] = Field(sa_column=Column(JSON))
    interests: list[str] = Field(sa_column=Column(JSON))
    active_projects: list[str] = Field(sa_column=Column(JSON))
    preferences: dict[str, Any] = Field(sa_column=Column(JSON))
    created_at: datetime
    updated_at: datetime


class ActivityTable(SQLModel, table=True):
    """Persistence entity for :class:`app.models.activity.Activity`."""

    __tablename__ = "activities"

    id: str = Field(primary_key=True)
    user_id: str = Field(index=True)
    timestamp: datetime = Field(index=True)
    raw_text: str
    normalized_text: str | None = None
    category: str
    subcategory: str | None = None
    duration: int = 0
    intent: str | None = None
    project: str | None = Field(default=None, index=True)
    people: list[str] = Field(sa_column=Column(JSON))
    location: str | None = None
    confidence: float
    metadata_: dict[str, Any] = Field(sa_column=Column("metadata", JSON))
    evaluation_score: float | None = None
    evaluation_reason: str | None = None
    retry_count: int = 0
    validated: bool = False


class MemoryTable(SQLModel, table=True):
    """Persistence entity for :class:`app.models.memory.Memory`.

    Indexed on the fields the retrieval strategy ranks by (docs/10 §28):
    type, status, confidence, updated_at.
    """

    __tablename__ = "memories"

    id: str = Field(primary_key=True)
    user_id: str = Field(index=True)
    type: str = Field(index=True)
    statement: str
    confidence: float = Field(index=True)
    evidence_count: int
    supporting_activity_ids: list[str] = Field(sa_column=Column(JSON))
    status: str = Field(index=True)
    source: str | None = None
    created_at: datetime
    updated_at: datetime = Field(index=True)
    expires_at: datetime | None = None
    metadata_: dict[str, Any] = Field(sa_column=Column("metadata", JSON))


class TimelineTable(SQLModel, table=True):
    """Persistence entity for :class:`app.models.timeline.Timeline`.

    Keyed by ``date`` (one timeline per day). Nested activities and sessions are
    stored as JSON document aggregates.
    """

    __tablename__ = "timelines"

    user_id: str = Field(primary_key=True)
    date: date_type = Field(primary_key=True)
    activities: list[Any] = Field(sa_column=Column(JSON))
    sessions: list[Any] = Field(sa_column=Column(JSON))
    total_duration: int = 0
    context_switches: int = 0


class SummaryTable(SQLModel, table=True):
    """Persistence entity for :class:`app.models.summary.DailySummary`."""

    __tablename__ = "summaries"

    id: str = Field(primary_key=True)
    user_id: str = Field(index=True)
    date: date_type = Field(index=True)
    overview: str
    timeline: str
    metrics: dict[str, Any] = Field(sa_column=Column(JSON))
    insights: list[Any] = Field(sa_column=Column(JSON))
    recommendations: list[Any] = Field(sa_column=Column(JSON))
    tomorrow_focus: str
    # Storage-only: distinguishes multiple summaries written for the same day so
    # reads can return the most recent (not part of the DailySummary domain model).
    created_at: datetime = Field(index=True)
