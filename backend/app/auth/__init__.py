"""Authentication: password hashing, session JWTs, and Google token verification.

This package owns identity only — verifying *who* is calling. Per-user data
isolation (scoping queries by the authenticated user) lives in the repositories
and API layer.
"""

from app.auth.google import GoogleAuthError, verify_google_token
from app.auth.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

__all__ = [
    "GoogleAuthError",
    "verify_google_token",
    "create_access_token",
    "decode_access_token",
    "hash_password",
    "verify_password",
]
