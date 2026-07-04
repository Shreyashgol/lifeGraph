"""Application settings.

All configuration is loaded from environment variables (optionally via a local
``.env`` file) and validated through Pydantic. Secrets are never hardcoded and
never committed — see ``.env.example`` for the expected keys.
"""

from __future__ import annotations

import json
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed, validated application configuration.

    Values are sourced from the process environment and an optional ``.env``
    file. Unknown environment variables are ignored so the same environment can
    host multiple applications.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application -------------------------------------------------------
    app_name: str = "LifeGraph"
    environment: str = Field(
        default="development",
        description="Deployment environment: development | staging | production.",
    )
    log_level: str = Field(default="INFO", description="Root logging level.")

    # --- HTTP server -------------------------------------------------------
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api"
    cors_origins: list[str] | str = Field(
        default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"],
        description="Origins permitted to call the API (the Vite frontend on 5173).",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed]
                except json.JSONDecodeError:
                    pass
            return [item.strip() for item in v.split(",") if item.strip()]
        elif isinstance(v, list):
            return [str(item).strip() for item in v]
        return v

    # --- Persistence -------------------------------------------------------
    # SQLite for Version 1; migrates to PostgreSQL later with no business-layer
    # changes (see docs/04_TECH_STACK.md).
    database_url: str = "sqlite:///./lifegraph.db"

    # --- AI provider -------------------------------------------------------
    # Optional in Phase 1 so the application boots without an LLM key. The
    # intelligence layer (Phase 5) requires it.
    groq_api_key: str | None = None
    model_name: str = "llama-3.3-70b-versatile"

    @property
    def is_production(self) -> bool:
        """True when running in a production-like environment."""
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Return a process-wide, cached :class:`Settings` instance.

    Caching keeps configuration immutable during a run and makes ``Settings`` a
    single injectable dependency (FastAPI ``Depends``) rather than a global.
    """
    return Settings()
