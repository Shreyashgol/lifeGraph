"""User onboarding and profile endpoints.

Onboarding fills in the reasoning profile (occupation, goals, …) for the
**authenticated** account created at sign-up. ``GET /profile`` returns it, or 404
until the user has onboarded.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlmodel import Session

from app.api.dependencies import get_current_user, get_session
from app.models.account import AuthUser
from app.models.user import UserProfile
from app.repositories.user_repository import UserRepository
from app.schemas.user import OnboardingRequest, ProfileResponse

router = APIRouter(tags=["user"])


@router.post("/onboarding", response_model=ProfileResponse, status_code=201)
def onboard(
    payload: OnboardingRequest,
    session: Session = Depends(get_session),
    current_user: AuthUser = Depends(get_current_user),
) -> ProfileResponse:
    """Create/update the current user's reasoning profile."""
    try:
        # Validate via the domain model (timezone, non-blank fields, unique projects).
        UserProfile(
            id=current_user.id,
            name=payload.name,
            occupation=payload.occupation,
            timezone=payload.timezone,
            goals=payload.goals,
            interests=payload.interests,
            active_projects=payload.active_projects,
            preferences=payload.preferences,
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=[{"loc": e["loc"], "msg": e["msg"], "type": e["type"]} for e in exc.errors()],
        ) from exc

    saved = UserRepository(session).upsert_profile(
        str(current_user.id),
        name=payload.name,
        occupation=payload.occupation,
        timezone=payload.timezone,
        goals=payload.goals,
        interests=payload.interests,
        active_projects=payload.active_projects,
        preferences=payload.preferences,
    )
    return ProfileResponse.from_domain(saved)


@router.get("/profile", response_model=ProfileResponse)
def get_profile(
    session: Session = Depends(get_session),
    current_user: AuthUser = Depends(get_current_user),
) -> ProfileResponse:
    profile = UserRepository(session).get_profile(str(current_user.id))
    if profile is None:
        raise HTTPException(status_code=404, detail="no profile; onboard first")
    return ProfileResponse.from_domain(profile)
