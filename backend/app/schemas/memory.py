"""Memory API schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from app.models.memory import Memory


class MemoryView(BaseModel):
    """Public view of a semantic memory."""

    id: UUID
    type: str
    statement: str
    confidence: float
    evidence_count: int
    status: str

    @classmethod
    def from_domain(cls, memory: Memory) -> MemoryView:
        return cls(
            id=memory.id,
            type=memory.type.value,
            statement=memory.statement,
            confidence=memory.confidence,
            evidence_count=memory.evidence_count,
            status=memory.status.value,
        )


class MemoryResponse(BaseModel):
    """Response for ``GET /memory``."""

    memories: list[MemoryView]
    count: int
