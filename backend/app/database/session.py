"""Database engine, session management, and initialization.

The engine is dialect-agnostic: it reads ``DATABASE_URL`` from configuration, so
the same code runs against SQLite (local/tests) or Neon Postgres (production).
On Postgres the pgvector extension is enabled for semantic-memory embeddings.
Repositories receive a :class:`~sqlmodel.Session` (dependency-injected), which
keeps them testable against an isolated database.
"""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

from app.config import get_settings

_settings = get_settings()
_is_sqlite = _settings.database_url.startswith("sqlite")

# SQLite needs check_same_thread under FastAPI's threadpool; Postgres (Neon is
# serverless) benefits from pre-ping so dropped connections are recycled.
_connect_args = {"check_same_thread": False} if _is_sqlite else {}

engine = create_engine(
    _settings.database_url,
    echo=False,
    pool_pre_ping=True,
    connect_args=_connect_args,
)


def init_db() -> None:
    """Create tables (and the pgvector extension on Postgres). Idempotent."""
    # Import models so their tables are registered on SQLModel.metadata.
    from app.database import models  # noqa: F401

    if not _is_sqlite:
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """Yield a database session (FastAPI dependency)."""
    with Session(engine) as session:
        yield session
