"""UserRepository — persistence for accounts and their profiles.

A ``users`` row is both an account (email + credential) and a profile (filled in
at onboarding). This repository exposes account operations returning
:class:`AuthUser`, and profile operations returning :class:`UserProfile` (only
once the user has onboarded).
"""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlmodel import Session, select

from app.database.base import as_utc, to_naive_utc
from app.database.models import UserTable
from app.models.account import AuthUser
from app.models.base import utcnow
from app.models.user import UserProfile


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # --- Accounts ---------------------------------------------------------
    def create_account(
        self,
        *,
        email: str,
        name: str,
        hashed_password: str | None = None,
        picture: str | None = None,
    ) -> AuthUser:
        """Insert a new account (profile fields empty until onboarding)."""
        now = to_naive_utc(utcnow())
        row = UserTable(
            id=str(uuid4()),
            email=email.strip().lower(),
            hashed_password=hashed_password,
            name=name,
            picture=picture,
            occupation=None,
            timezone=None,
            goals=[],
            interests=[],
            active_projects=[],
            preferences={},
            created_at=now,
            updated_at=now,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return self._to_auth(row)

    def get_by_email(self, email: str) -> AuthUser | None:
        row = self.session.exec(
            select(UserTable).where(UserTable.email == email.strip().lower())
        ).first()
        return self._to_auth(row) if row is not None else None

    def get_by_id(self, user_id: str) -> AuthUser | None:
        row = self.session.get(UserTable, user_id)
        return self._to_auth(row) if row is not None else None

    # --- Profiles ---------------------------------------------------------
    def get_profile(self, user_id: str) -> UserProfile | None:
        """Return the onboarded profile, or ``None`` if the user hasn't onboarded."""
        row = self.session.get(UserTable, user_id)
        if row is None or not row.occupation or not row.timezone or not row.goals:
            return None
        return self._to_profile(row)

    def upsert_profile(
        self,
        user_id: str,
        *,
        name: str,
        occupation: str,
        timezone: str,
        goals: list[str],
        interests: list[str],
        active_projects: list[str],
        preferences: dict,
    ) -> UserProfile:
        """Fill in / update the onboarding profile fields on the account row."""
        row = self.session.get(UserTable, user_id)
        if row is None:
            raise ValueError(f"no account for user_id {user_id}")
        row.name = name
        row.occupation = occupation
        row.timezone = timezone
        row.goals = list(goals)
        row.interests = list(interests)
        row.active_projects = list(active_projects)
        row.preferences = dict(preferences)
        row.updated_at = to_naive_utc(utcnow())
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return self._to_profile(row)

    # --- Mapping ----------------------------------------------------------
    def _to_auth(self, row: UserTable) -> AuthUser:
        return AuthUser(
            id=UUID(row.id),
            email=row.email,
            name=row.name,
            picture=row.picture,
            hashed_password=row.hashed_password,
        )

    def _to_profile(self, row: UserTable) -> UserProfile:
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
