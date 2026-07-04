"""Google Sign-In ID-token verification.

We verify the Google ID token *server-side* (signature + audience) exactly once,
at login, then issue our own session JWT. This prevents a client from claiming an
arbitrary identity — the whole point of the multi-tenancy fix.
"""

from __future__ import annotations

from dataclasses import dataclass

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from app.config import get_settings


class GoogleAuthError(Exception):
    """The Google ID token was missing, invalid, or for the wrong audience."""


@dataclass(frozen=True)
class GoogleIdentity:
    sub: str
    email: str
    name: str | None
    picture: str | None


def verify_google_token(token: str) -> GoogleIdentity:
    """Validate a Google ID token and return the verified identity.

    Raises :class:`GoogleAuthError` if verification fails or Google sign-in is not
    configured (``GOOGLE_CLIENT_ID`` unset).
    """
    client_id = get_settings().google_client_id
    if not client_id:
        raise GoogleAuthError("Google sign-in is not configured (GOOGLE_CLIENT_ID unset)")
    try:
        claims = google_id_token.verify_oauth2_token(token, google_requests.Request(), client_id)
    except Exception as exc:
        raise GoogleAuthError(f"invalid Google token: {exc}") from exc

    email = claims.get("email")
    sub = claims.get("sub")
    if not email or not sub:
        raise GoogleAuthError("Google token missing email/sub")
    if claims.get("email_verified") is False:
        raise GoogleAuthError("Google email not verified")
    return GoogleIdentity(
        sub=sub, email=email, name=claims.get("name"), picture=claims.get("picture")
    )
