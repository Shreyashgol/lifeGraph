"""Memory domain model (docs/07_DATA_MODELS.md §9, docs/10_MEMORY_ARCHITECTURE.md).

Semantic memory: an evidence-backed conclusion about the user, not an
observation. Memory is earned — it evolves from repeated evidence and is never
created from a single activity.

Reconciliation note (flagged in design review §6): the field set is the
canonical data contract from docs/07, extended with ``status`` and ``source``
from docs/10, whose memory-state lifecycle (candidate -> active -> archived) is
architecturally load-bearing: only ACTIVE memories participate in reasoning.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import Field

from app.models.base import DomainModel, utcnow
from app.models.enums import MemoryStatus, MemoryType


class Memory(DomainModel):
    """A structured, evidence-backed piece of stable knowledge about the user."""

    id: UUID = Field(default_factory=uuid4)
    type: MemoryType
    statement: str = Field(min_length=1, description="The learned fact.")
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_count: int = Field(ge=1, description="Number of supporting observations.")
    supporting_activity_ids: list[UUID] = Field(default_factory=list)
    status: MemoryStatus = MemoryStatus.CANDIDATE
    source: str | None = Field(default=None, description="Origin of the memory.")
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    expires_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
