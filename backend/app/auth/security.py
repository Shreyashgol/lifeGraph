"""Password hashing (bcrypt) and session JWTs (PyJWT).

The session JWT is *our own* token — issued after a successful email/password or
Google login and sent back by the client as a Bearer credential. It is distinct
from the Google ID token, which we only verify once at sign-in (see
:mod:`app.auth.google`).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.config import get_settings

_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Return a bcrypt hash of ``password`` (safe to store)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Return True if ``password`` matches the stored bcrypt ``hashed`` value."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        # Malformed hash (e.g. a Google-only account with no password).
        return False


def create_access_token(user_id: str) -> str:
    """Issue a signed session JWT whose subject is the user's id."""
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expiry_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """Return the user id from a valid session JWT, or ``None`` if invalid/expired."""
    try:
        payload = jwt.decode(token, get_settings().jwt_secret, algorithms=[_ALGORITHM])
    except jwt.PyJWTError:
        return None
    sub = payload.get("sub")
    return sub if isinstance(sub, str) else None
