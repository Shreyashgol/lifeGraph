"""Shared base for domain models.

All domain models inherit :class:`DomainModel`, which forbids unknown fields so
that malformed data is rejected at the boundary rather than silently absorbed.
Extensible data belongs in explicit ``metadata`` fields, never as stray
top-level keys.
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict


def utcnow() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(UTC)


class DomainModel(BaseModel):
    """Base class for all LifeGraph domain models.

    Domain models are pure business concepts, independent of FastAPI and
    SQLModel. They are updated via :meth:`~pydantic.BaseModel.model_copy`
    (``update={...}``) rather than in-place mutation, which keeps state
    transitions traceable (see ``docs/07_DATA_MODELS.md`` §"State Immutability").
    """

    model_config = ConfigDict(extra="forbid")
