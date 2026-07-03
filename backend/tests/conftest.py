"""Shared pytest fixtures."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    """A TestClient bound to a freshly built application instance."""
    return TestClient(create_app())


@pytest.fixture
def session() -> Iterator[Session]:
    """An isolated in-memory database session for repository tests.

    A ``StaticPool`` shares the single in-memory connection across the session so
    the schema persists for the test's lifetime.
    """
    # Import registers the tables on SQLModel.metadata.
    from app.database import models  # noqa: F401

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as db_session:
        yield db_session
