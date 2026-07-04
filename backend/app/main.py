"""FastAPI application entrypoint.

Wires together configuration, structured logging, middleware, and routers. This
module deliberately stays thin — it is composition only. Business logic lives in
the graph, intelligence, and repository layers introduced in later phases.

Run locally:
    uvicorn app.main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.activity import router as activity_router
from app.api.health import router as health_router
from app.api.insights import router as insights_router
from app.api.memory import router as memory_router
from app.api.onboarding import router as onboarding_router
from app.api.recommendations import router as recommendations_router
from app.api.summary import router as summary_router
from app.api.timeline import router as timeline_router
from app.config import get_settings
from app.config.logging import configure_logging, get_logger
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Configure logging, initialize the database, and log lifecycle events."""
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = get_logger("app.lifespan")
    init_db()
    logger.info(
        "application_startup",
        extra={"environment": settings.environment, "version": __version__},
    )
    yield
    logger.info("application_shutdown")


def create_app() -> FastAPI:
    """Application factory.

    A factory (rather than a module-level singleton assembled at import time)
    keeps the app easy to configure in tests and future deployment contexts.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        summary="AI-Powered Personal Intelligence Engine",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        # In development, accept any localhost port so the frontend "just works"
        # regardless of the dev port (Vite 5173, etc.). Production uses only the
        # explicit allowlist above.
        allow_origin_regex=None if settings.is_production else r"http://localhost:\d+",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(onboarding_router)
    app.include_router(activity_router)
    app.include_router(timeline_router)
    app.include_router(memory_router)
    app.include_router(insights_router)
    app.include_router(recommendations_router)
    app.include_router(summary_router)

    return app


app = create_app()
