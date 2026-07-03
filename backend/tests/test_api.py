"""API tests (Phase 7): endpoint validation, responses, and wiring."""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.api.dependencies import get_graph, get_session
from app.graph.state import LifeGraphState
from app.main import create_app
from app.models import Activity, Memory, MemoryType, Timeline
from app.repositories import MemoryRepository, TimelineRepository

TS = datetime(2026, 7, 3, 9, 0, tzinfo=timezone.utc)


class FakeGraph:
    """Stand-in for the compiled graph: returns an enriched state."""

    async def ainvoke(self, state: LifeGraphState) -> LifeGraphState:
        activity = Activity(
            timestamp=TS,
            raw_text=state.current_activity or "",
            category="Deep Work",
            project="LifeGraph",
            duration=120,
            confidence=0.95,
            validated=True,
        )
        timeline = Timeline(date=TS.date(), activities=[activity], total_duration=120)
        return state.model_copy(update={"structured_activity": activity, "timeline": timeline})


@pytest.fixture
def api(session: Session) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[get_graph] = lambda: FakeGraph()
    return TestClient(app)


# --------------------------------------------------------------------------- #
# Onboarding / profile
# --------------------------------------------------------------------------- #
def test_onboarding_then_profile(api: TestClient) -> None:
    resp = api.post(
        "/onboarding",
        json={
            "name": "Shreyash",
            "occupation": "AI Engineer",
            "timezone": "Asia/Kolkata",
            "goals": ["Build AI products"],
            "active_projects": ["LifeGraph"],
        },
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "Shreyash"

    profile = api.get("/profile")
    assert profile.status_code == 200
    assert profile.json()["occupation"] == "AI Engineer"


def test_onboarding_rejects_invalid_timezone(api: TestClient) -> None:
    resp = api.post(
        "/onboarding",
        json={"name": "A", "occupation": "Eng", "timezone": "Mars/Phobos", "goals": ["g"]},
    )
    assert resp.status_code == 422


def test_profile_404_when_absent(api: TestClient) -> None:
    assert api.get("/profile").status_code == 404


# --------------------------------------------------------------------------- #
# Read endpoints (empty)
# --------------------------------------------------------------------------- #
def test_timeline_empty(api: TestClient) -> None:
    resp = api.get("/timeline")
    assert resp.status_code == 200
    assert resp.json()["activities"] == []


def test_memory_empty(api: TestClient) -> None:
    resp = api.get("/memory")
    assert resp.status_code == 200
    assert resp.json()["count"] == 0


def test_summary_404_when_none(api: TestClient) -> None:
    assert api.get("/summary").status_code == 404


def test_insights_and_recommendations_empty(api: TestClient) -> None:
    assert api.get("/insights").json()["count"] == 0
    assert api.get("/recommendations").json()["count"] == 0


# --------------------------------------------------------------------------- #
# POST /activity
# --------------------------------------------------------------------------- #
def test_log_activity_returns_structured_result(api: TestClient) -> None:
    resp = api.post("/activity", json={"activity": "Worked on LifeGraph backend for two hours."})
    assert resp.status_code == 200
    body = resp.json()
    assert body["activity"]["category"] == "Deep Work"
    assert body["activity"]["validated"] is True
    assert body["timeline_updated"] is True


def test_log_activity_validates_empty_input(api: TestClient) -> None:
    assert api.post("/activity", json={"activity": ""}).status_code == 422


# --------------------------------------------------------------------------- #
# Read endpoints (seeded)
# --------------------------------------------------------------------------- #
def test_seeded_timeline_and_memory(api: TestClient, session: Session) -> None:
    activity = Activity(
        timestamp=TS, raw_text="x", category="Deep Work", project="LifeGraph", duration=60, confidence=0.9
    )
    TimelineRepository(session).create(
        Timeline(date=date(2026, 7, 3), activities=[activity], total_duration=60)
    )
    MemoryRepository(session).create(
        Memory(type=MemoryType.GOAL, statement="Ship LifeGraph", confidence=0.9, evidence_count=3)
    )

    timeline = api.get("/timeline", params={"date": "2026-07-03"})
    assert timeline.status_code == 200
    assert len(timeline.json()["activities"]) == 1

    memory = api.get("/memory")
    assert memory.json()["count"] == 1
    assert memory.json()["memories"][0]["type"] == "goal"
