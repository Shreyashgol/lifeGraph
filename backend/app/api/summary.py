"""GET /summary — the end-of-day intelligence report."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.api.dependencies import get_session
from app.repositories.summary_repository import SummaryRepository
from app.schemas.summary import SummaryResponse

router = APIRouter(tags=["summary"])


@router.get("/summary", response_model=SummaryResponse)
def get_summary(
    day: date | None = Query(default=None, alias="date"),
    session: Session = Depends(get_session),
) -> SummaryResponse:
    repo = SummaryRepository(session)
    summary = repo.get_by_date(day) if day is not None else repo.get_latest()
    if summary is None:
        raise HTTPException(status_code=404, detail="no summary available")
    return SummaryResponse.from_domain(summary)
