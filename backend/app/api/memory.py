"""GET /memory — the user's learned memories."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.dependencies import get_session
from app.repositories.memory_repository import MemoryRepository
from app.schemas.memory import MemoryResponse, MemoryView

router = APIRouter(tags=["memory"])


@router.get("/memory", response_model=MemoryResponse)
def get_memory(session: Session = Depends(get_session)) -> MemoryResponse:
    memories = MemoryRepository(session).list()
    views = [MemoryView.from_domain(m) for m in memories]
    return MemoryResponse(memories=views, count=len(views))
