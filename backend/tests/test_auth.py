"""Tests for authentication and per-user data isolation."""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.api.dependencies import get_session
from app.auth.google import GoogleAuthError, GoogleIdentity
from app.auth.security import create_access_token
from app.models.activity import Activity
from app.models.timeline import Timeline
from app.repositories.timeline_repository import TimelineRepository


def test_auth_register_success(client: TestClient) -> None:
    resp = client.post(
        "/auth/register",
        json={"email": "newuser@example.com", "password": "securepassword123", "name": "New User"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "access_token" in body
    assert body["user"]["email"] == "newuser@example.com"
    assert body["user"]["name"] == "New User"


def test_auth_register_conflict(client: TestClient, session: Session) -> None:
    from app.repositories.user_repository import UserRepository
    UserRepository(session).create_account(
        email="existing@example.com", name="Existing", hashed_password="pwd"
    )

    resp = client.post(
        "/auth/register",
        json={"email": "existing@example.com", "password": "securepassword123"},
    )
    assert resp.status_code == 409
    assert "already exists" in resp.json()["detail"]


def test_auth_login_success(client: TestClient, session: Session) -> None:
    from app.auth.security import hash_password
    from app.repositories.user_repository import UserRepository
    UserRepository(session).create_account(
        email="login@example.com", name="Login", hashed_password=hash_password("password123")
    )

    resp = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "password123"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["user"]["email"] == "login@example.com"


def test_auth_login_invalid(client: TestClient, session: Session) -> None:
    from app.auth.security import hash_password
    from app.repositories.user_repository import UserRepository
    UserRepository(session).create_account(
        email="login@example.com", name="Login", hashed_password=hash_password("password123")
    )

    # Wrong password
    resp = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401

    # Non-existing user
    resp = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "password123"},
    )
    assert resp.status_code == 401


def test_auth_me_unauthorized(client: TestClient) -> None:
    resp = client.get("/auth/me")
    assert resp.status_code == 401

    client.headers["Authorization"] = "Bearer invalidtoken"
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_auth_me_success(auth_client: tuple[TestClient, str]) -> None:
    client, user_id = auth_client
    resp = client.get("/auth/me")
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "test@example.com"
    assert body["id"] == user_id


@patch("app.api.auth.verify_google_token")
def test_auth_google_success(mock_verify: patch, client: TestClient) -> None:
    mock_verify.return_value = GoogleIdentity(
        sub="google123", email="google@example.com", name="Google User", picture="pic.jpg"
    )

    resp = client.post("/auth/google", json={"id_token": "valid_token"})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["user"]["email"] == "google@example.com"
    assert body["user"]["name"] == "Google User"
    assert body["user"]["picture"] == "pic.jpg"


@patch("app.api.auth.verify_google_token")
def test_auth_google_failure(mock_verify: patch, client: TestClient) -> None:
    mock_verify.side_effect = GoogleAuthError("Token expired")

    resp = client.post("/auth/google", json={"id_token": "expired_token"})
    assert resp.status_code == 401
    assert "Google sign-in failed" in resp.json()["detail"]


def test_cross_user_isolation(session: Session) -> None:
    """Ensure user A cannot see or modify user B's data."""
    from app.main import create_app
    from app.repositories.user_repository import UserRepository

    # Create user A and user B
    repo = UserRepository(session)
    user_a = repo.create_account(email="usera@example.com", name="User A")
    user_b = repo.create_account(email="userb@example.com", name="User B")

    # Seed data for user B
    timeline_repo_b = TimelineRepository(session, str(user_b.id))
    activity = Activity(
        timestamp="2026-07-03T10:00:00Z",
        raw_text="Secret activity B",
        category="Deep Work",
        confidence=0.9,
    )
    timeline_repo_b.create(
        Timeline(date=date(2026, 7, 3), activities=[activity], total_duration=60)
    )

    # Build client for user A
    app = create_app()
    app.dependency_overrides[get_session] = lambda: session
    client_a = TestClient(app)
    token_a = create_access_token(str(user_a.id))
    client_a.headers["Authorization"] = f"Bearer {token_a}"

    # Verify user A sees empty timeline
    resp_a = client_a.get("/timeline", params={"date": "2026-07-03"})
    assert resp_a.status_code == 200
    assert resp_a.json()["activities"] == []

    # Verify user B sees their own timeline
    client_b = TestClient(app)
    token_b = create_access_token(str(user_b.id))
    client_b.headers["Authorization"] = f"Bearer {token_b}"
    resp_b = client_b.get("/timeline", params={"date": "2026-07-03"})
    assert resp_b.status_code == 200
    assert len(resp_b.json()["activities"]) == 1
    assert resp_b.json()["activities"][0]["category"] == "Deep Work"
