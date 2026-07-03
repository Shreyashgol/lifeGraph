"""Health check endpoint.

A liveness probe used for local development, deployment platforms (Render), and
end-to-end verification. It performs no I/O so it stays well under the 100 ms
target in ``docs/05_SYSTEM_FLOW.md``.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app import __version__
from app.config import Settings, get_settings
from app.config.constants import STATUS_OK
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Service health")
async def health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
    """Report that the service is running and echo basic build metadata."""
    return HealthResponse(
        status=STATUS_OK,
        app=settings.app_name,
        version=__version__,
        environment=settings.environment,
    )
