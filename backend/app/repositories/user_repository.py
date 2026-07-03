"""UserRepository — persistence for UserProfile."""

from __future__ import annotations

from uuid import UUID

from sqlmodel import select

from app.database.base import as_utc, to_naive_utc
from app.database.models import UserTable
from app.models.user import UserProfile
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[UserProfile]):
    table_cls = UserTable

    def _to_row(self, model: UserProfile) -> UserTable:
        return UserTable(
            id=str(model.id),
            name=model.name,
            occupation=model.occupation,
            timezone=model.timezone,
            goals=list(model.goals),
            interests=list(model.interests),
            active_projects=list(model.active_projects),
            preferences=dict(model.preferences),
            created_at=to_naive_utc(model.created_at),
            updated_at=to_naive_utc(model.updated_at),
        )

    def _to_domain(self, row: UserTable) -> UserProfile:
        return UserProfile(
            id=UUID(row.id),
            name=row.name,
            occupation=row.occupation,
            timezone=row.timezone,
            goals=row.goals,
            interests=row.interests,
            active_projects=row.active_projects,
            preferences=row.preferences,
            created_at=as_utc(row.created_at),
            updated_at=as_utc(row.updated_at),
        )

    def get_first(self) -> UserProfile | None:
        """Return the first user — convenient for single-user Version 1."""
        row = self.session.exec(select(UserTable)).first()
        return self._to_domain(row) if row is not None else None
