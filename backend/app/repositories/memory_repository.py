"""MemoryRepository — persistence for Memory (semantic memory)."""

from __future__ import annotations

from uuid import UUID

from sqlmodel import select

from app.database.base import as_utc, to_naive_utc
from app.database.models import MemoryTable
from app.models.enums import MemoryStatus, MemoryType
from app.models.memory import Memory
from app.repositories.base import BaseRepository


class MemoryRepository(BaseRepository[Memory]):
    table_cls = MemoryTable

    def _to_row(self, model: Memory) -> MemoryTable:
        return MemoryTable(
            id=str(model.id),
            type=model.type.value,
            statement=model.statement,
            confidence=model.confidence,
            evidence_count=model.evidence_count,
            supporting_activity_ids=[str(x) for x in model.supporting_activity_ids],
            status=model.status.value,
            source=model.source,
            created_at=to_naive_utc(model.created_at),
            updated_at=to_naive_utc(model.updated_at),
            expires_at=to_naive_utc(model.expires_at),
            metadata_=dict(model.metadata),
        )

    def _to_domain(self, row: MemoryTable) -> Memory:
        return Memory(
            id=UUID(row.id),
            type=MemoryType(row.type),
            statement=row.statement,
            confidence=row.confidence,
            evidence_count=row.evidence_count,
            supporting_activity_ids=[UUID(x) for x in row.supporting_activity_ids],
            status=MemoryStatus(row.status),
            source=row.source,
            created_at=as_utc(row.created_at),
            updated_at=as_utc(row.updated_at),
            expires_at=as_utc(row.expires_at),
            metadata=row.metadata_,
        )

    def list_active(self) -> list[Memory]:
        """Return only ACTIVE memories — the ones that participate in reasoning."""
        statement = select(MemoryTable).where(
            MemoryTable.status == MemoryStatus.ACTIVE.value
        )
        return [self._to_domain(row) for row in self.session.exec(statement).all()]

    def list_by_type(self, memory_type: MemoryType) -> list[Memory]:
        """Return memories of a single category."""
        statement = select(MemoryTable).where(MemoryTable.type == memory_type.value)
        return [self._to_domain(row) for row in self.session.exec(statement).all()]
