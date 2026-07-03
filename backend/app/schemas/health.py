"""Health check response schema."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Payload returned by ``GET /health``."""

    status: str = Field(description="Service status literal, e.g. 'ok'.")
    app: str = Field(description="Application name.")
    version: str = Field(description="Running application version.")
    environment: str = Field(description="Active deployment environment.")
