"""MemoryRepository — persistence for Memory (semantic memory)."""

from __future__ import annotations

from uuid import UUID

from sqlmodel import select

from app.config.constants import MEMORY_ACTIVATION_CONFIDENCE, MEMORY_EVIDENCE_THRESHOLD
from app.database.base import as_utc, to_naive_utc
from app.database.models import MemoryTable
from app.models.base import utcnow
from app.models.enums import MemoryStatus, MemoryType
from app.models.memory import Memory
from app.repositories.base import BaseRepository


def _earned_confidence(evidence_count: int) -> float:
    """Confidence grows with corroborating observations (rewards consistency)."""
    return min(0.95, 0.45 + 0.10 * evidence_count)


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

    def accumulate_memory(
        self,
        *,
        memory_type: MemoryType,
        key: str,
        statement: str,
        activity_id: UUID,
        source: str = "accumulator",
    ) -> Memory:
        """Record one more observation supporting a memory (the "earned" path).

        Memories are matched by ``(type, metadata['key'])``. A new memory starts
        as a CANDIDATE and is promoted to ACTIVE once it clears the evidence and
        confidence thresholds. The canonical ``statement`` is kept stable; only
        the evidence and confidence grow.
        """
        normalized = key.strip().lower()
        existing = next(
            (m for m in self.list_by_type(memory_type) if m.metadata.get("key") == normalized),
            None,
        )

        if existing is not None:
            count = existing.evidence_count + 1
            confidence = _earned_confidence(count)
            status = (
                MemoryStatus.ACTIVE
                if count >= MEMORY_EVIDENCE_THRESHOLD
                and confidence >= MEMORY_ACTIVATION_CONFIDENCE
                else existing.status
            )
            updated = existing.model_copy(
                update={
                    "evidence_count": count,
                    "confidence": confidence,
                    "status": status,
                    "supporting_activity_ids": [*existing.supporting_activity_ids, activity_id],
                    "updated_at": utcnow(),
                }
            )
            return self.update(updated)

        candidate = Memory(
            type=memory_type,
            statement=statement,
            confidence=_earned_confidence(1),
            evidence_count=1,
            supporting_activity_ids=[activity_id],
            status=MemoryStatus.CANDIDATE,
            source=source,
            metadata={"key": normalized},
        )
        return self.create(candidate)

    def accumulate_project(self, project: str, activity_id: UUID) -> Memory:
        """Deterministic project-evidence accumulation (from ``activity.project``)."""
        return self.accumulate_memory(
            memory_type=MemoryType.PROJECT,
            key=project,
            statement=f"Actively works on {project}.",
            activity_id=activity_id,
            source="project_accumulator",
        )
