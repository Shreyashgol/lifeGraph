"""Authentication API schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.account import AuthUser


def _valid_email(value: str) -> str:
    email = value.strip().lower()
    if "@" not in email or "." not in email.split("@")[-1] or len(email) < 5:
        raise ValueError("invalid email address")
    return email


class RegisterRequest(BaseModel):
    """Body for ``POST /auth/register``."""

    email: str
    password: str = Field(min_length=8, max_length=128)
    name: str | None = Field(default=None, max_length=120)

    _normalize_email = field_validator("email")(_valid_email)


class LoginRequest(BaseModel):
    """Body for ``POST /auth/login``."""

    email: str
    password: str = Field(min_length=1, max_length=128)

    _normalize_email = field_validator("email")(_valid_email)


class GoogleAuthRequest(BaseModel):
    """Body for ``POST /auth/google`` — the Google ID-token credential."""

    id_token: str = Field(min_length=1)


class UserView(BaseModel):
    """Public account view (never includes the password hash)."""

    id: UUID
    email: str
    name: str
    picture: str | None = None

    @classmethod
    def from_domain(cls, user: AuthUser) -> UserView:
        return cls(id=user.id, email=user.email, name=user.name, picture=user.picture)


class AuthResponse(BaseModel):
    """Successful auth response: a session token plus the account."""

    access_token: str
    token_type: str = "bearer"
    user: UserView
