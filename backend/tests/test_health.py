"""Health endpoint tests (Phase 1 acceptance: the health endpoint responds)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app import __version__


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app"] == "LifeGraph"
    assert body["version"] == __version__
    assert body["environment"]


def test_health_matches_response_schema(client: TestClient) -> None:
    body = client.get("/health").json()

    assert set(body.keys()) == {"status", "app", "version", "environment"}
