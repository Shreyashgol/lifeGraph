"""Base repository.

Provides the standard CRUD contract (docs/14 §"Repository Implementation
Checklist"): create, get_by_id, list, update, delete. Subclasses implement the
domain <-> persistence conversion via ``_to_row`` and ``_to_domain``.

Repositories own persistence only — no AI reasoning, no business rules.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import Session, SQLModel, select

DomainT = TypeVar("DomainT", bound=BaseModel)


class BaseRepository(ABC, Generic[DomainT]):
    """CRUD repository for entities keyed by a string primary key."""

    table_cls: ClassVar[type[SQLModel]]

    def __init__(self, session: Session) -> None:
        self.session = session

    @abstractmethod
    def _to_row(self, model: DomainT) -> SQLModel:
        """Convert a domain model into a persistence row."""

    @abstractmethod
    def _to_domain(self, row: SQLModel) -> DomainT:
        """Convert a persistence row into a domain model."""

    def create(self, model: DomainT) -> DomainT:
        row = self._to_row(model)
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return self._to_domain(row)

    def get_by_id(self, entity_id: UUID | str) -> DomainT | None:
        row = self.session.get(self.table_cls, str(entity_id))
        return self._to_domain(row) if row is not None else None

    def list(self) -> list[DomainT]:
        rows = self.session.exec(select(self.table_cls)).all()
        return [self._to_domain(row) for row in rows]

    def update(self, model: DomainT) -> DomainT:
        """Upsert by primary key and return the persisted domain model."""
        row = self.session.merge(self._to_row(model))
        self.session.commit()
        return self._to_domain(row)

    def delete(self, entity_id: UUID | str) -> bool:
        row = self.session.get(self.table_cls, str(entity_id))
        if row is None:
            return False
        self.session.delete(row)
        self.session.commit()
        return True
