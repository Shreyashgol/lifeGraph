"""Shared pytest fixtures."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.dependencies import get_session
from app.main import create_app


@pytest.fixture
def client(session: Session) -> TestClient:
    """An unauthenticated TestClient with get_session overridden to the in-memory session."""
    app = create_app()
    app.dependency_overrides[get_session] = lambda: session
    return TestClient(app)


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


@pytest.fixture
def auth_client(session: Session) -> Iterator[tuple[TestClient, str]]:
    """A TestClient pre-authenticated as a newly registered user.

    Yields a tuple of (client, user_id).
    """
    from app.auth.security import create_access_token
    from app.repositories.user_repository import UserRepository

    app = create_app()
    app.dependency_overrides[get_session] = lambda: session

    # Create an initial user account
    repo = UserRepository(session)
    user = repo.create_account(
        email="test@example.com",
        name="Test User",
        hashed_password="mock-password-hash",
    )

    token = create_access_token(str(user.id))
    client = TestClient(app)
    client.headers["Authorization"] = f"Bearer {token}"
    client.user_id = str(user.id)

    yield client, str(user.id)


