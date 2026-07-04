"""GET /recommendations — personalized actions from the latest summary."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.api.dependencies import get_current_user, get_session
from app.models.account import AuthUser
from app.repositories.summary_repository import SummaryRepository
from app.schemas.recommendation import RecommendationsResponse, RecommendationView

router = APIRouter(tags=["recommendations"])


@router.get("/recommendations", response_model=RecommendationsResponse)
def get_recommendations(
    day: date | None = Query(default=None, alias="date"),
    session: Session = Depends(get_session),
    current_user: AuthUser = Depends(get_current_user),
) -> RecommendationsResponse:
    repo = SummaryRepository(session, str(current_user.id))
    summary = repo.get_by_date(day) if day is not None else repo.get_latest()
    recommendations = summary.recommendations if summary is not None else []
    views = [RecommendationView.from_domain(r) for r in recommendations]
    return RecommendationsResponse(recommendations=views, count=len(views))
