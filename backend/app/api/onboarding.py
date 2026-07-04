"""User onboarding and profile endpoints.

Added to fill the FR-1 onboarding gap (design review §6 #11): the reasoning graph
needs a user profile to personalize. Version 1 is single-user, so the API
resolves "the current user" as the first (and only) profile.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlmodel import Session

from app.api.dependencies import get_session
from app.models.user import UserProfile
from app.repositories.user_repository import UserRepository
from app.schemas.user import OnboardingRequest, ProfileResponse

router = APIRouter(tags=["user"])


@router.post("/onboarding", response_model=ProfileResponse, status_code=201)
def onboard(
    payload: OnboardingRequest, session: Session = Depends(get_session)
) -> ProfileResponse:
    """Create (or, for the single user, update) the profile."""
    try:
        profile = UserProfile(
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

    repo = UserRepository(session)
    existing = repo.get_first()
    if existing is not None:
        profile = profile.model_copy(
            update={"id": existing.id, "created_at": existing.created_at}
        )
        saved = repo.update(profile)
    else:
        saved = repo.create(profile)
    return ProfileResponse.from_domain(saved)


@router.get("/profile", response_model=ProfileResponse)
def get_profile(session: Session = Depends(get_session)) -> ProfileResponse:
    profile = UserRepository(session).get_first()
    if profile is None:
        raise HTTPException(status_code=404, detail="no profile; onboard first")
    return ProfileResponse.from_domain(profile)
