"""Authentication endpoints.

``/auth/register`` and ``/auth/login`` handle email+password accounts;
``/auth/google`` handles Google Sign-In. All three return the same
``AuthResponse`` (a session token + the account) so the frontend treats them
uniformly. ``/auth/me`` echoes the current account.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.dependencies import get_current_user, get_session
from app.auth import (
    GoogleAuthError,
    create_access_token,
    hash_password,
    verify_google_token,
    verify_password,
)
from app.models.account import AuthUser
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    AuthResponse,
    GoogleAuthRequest,
    LoginRequest,
    RegisterRequest,
    UserView,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _auth_response(user: AuthUser) -> AuthResponse:
    return AuthResponse(
        access_token=create_access_token(str(user.id)),
        user=UserView.from_domain(user),
    )


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(payload: RegisterRequest, session: Session = Depends(get_session)) -> AuthResponse:
    """Create an email/password account and return a session token."""
    repo = UserRepository(session)
    if repo.get_by_email(payload.email) is not None:
        raise HTTPException(status_code=409, detail="an account with this email already exists")
    name = (payload.name or payload.email.split("@")[0]).strip()
    user = repo.create_account(
        email=payload.email, name=name, hashed_password=hash_password(payload.password)
    )
    return _auth_response(user)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, session: Session = Depends(get_session)) -> AuthResponse:
    """Verify email/password and return a session token."""
    user = UserRepository(session).get_by_email(payload.email)
    if user is None or not verify_password(payload.password, user.hashed_password or ""):
        raise HTTPException(status_code=401, detail="invalid email or password")
    return _auth_response(user)


@router.post("/google", response_model=AuthResponse)
def google(payload: GoogleAuthRequest, session: Session = Depends(get_session)) -> AuthResponse:
    """Verify a Google ID token, upsert the account, and return a session token."""
    try:
        identity = verify_google_token(payload.id_token)
    except GoogleAuthError as exc:
        raise HTTPException(status_code=401, detail=f"Google sign-in failed: {exc}") from exc

    repo = UserRepository(session)
    user = repo.get_by_email(identity.email)
    if user is None:
        user = repo.create_account(
            email=identity.email,
            name=(identity.name or identity.email.split("@")[0]).strip(),
            picture=identity.picture,
        )
    return _auth_response(user)


@router.get("/me", response_model=UserView)
def me(current_user: AuthUser = Depends(get_current_user)) -> UserView:
    """Return the currently authenticated account."""
    return UserView.from_domain(current_user)
