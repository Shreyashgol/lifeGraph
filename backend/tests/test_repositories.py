"""Repository tests (Phase 3 acceptance: data persists, queries succeed)."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlmodel import Session

from app.models import (
    Activity,
    DailySummary,
    Insight,
    Memory,
    MemoryStatus,
    MemoryType,
    Priority,
    Recommendation,
    Session as WorkSession,
    Timeline,
    UserProfile,
)
from app.repositories import (
    ActivityRepository,
    MemoryRepository,
    SummaryRepository,
    TimelineRepository,
    UserRepository,
)

TS = datetime(2026, 7, 3, 9, 0, tzinfo=timezone.utc)


# --------------------------------------------------------------------------- #
# UserRepository
# --------------------------------------------------------------------------- #
def test_user_repository_crud(session: Session) -> None:
    repo = UserRepository(session)
    user = UserProfile(
        name="Shreyash",
        occupation="AI Engineer",
        timezone="Asia/Kolkata",
        goals=["Build AI products"],
        active_projects=["LifeGraph"],
        preferences={"editor": "vscode"},
    )

    created = repo.create(user)
    assert created == user

    fetched = repo.get_by_id(user.id)
    assert fetched is not None
    assert fetched.goals == ["Build AI products"]
    assert fetched.preferences == {"editor": "vscode"}

    assert repo.get_first() is not None
    assert len(repo.list()) == 1

    updated = user.model_copy(update={"occupation": "Founding Engineer"})
    assert repo.update(updated).occupation == "Founding Engineer"
    assert repo.get_by_id(user.id).occupation == "Founding Engineer"

    assert repo.delete(user.id) is True
    assert repo.get_by_id(user.id) is None
    assert repo.delete(user.id) is False


# --------------------------------------------------------------------------- #
# ActivityRepository
# --------------------------------------------------------------------------- #
def test_activity_repository_crud_and_roundtrip(session: Session) -> None:
    repo = ActivityRepository(session)
    activity = Activity(
        timestamp=TS,
        raw_text="Worked on auth",
        category="Deep Work",
        project="LifeGraph",
        duration=120,
        people=["Alice"],
        confidence=0.96,
        metadata={"source": "manual"},
    )

    created = repo.create(activity)
    assert created == activity  # full round-trip, incl. UTC timestamp

    fetched = repo.get_by_id(activity.id)
    assert fetched == activity


def test_activity_repository_list_by_day(session: Session) -> None:
    repo = ActivityRepository(session)
    today = Activity(timestamp=TS, raw_text="a", category="Deep Work", confidence=0.9)
    tomorrow = Activity(
        timestamp=TS + timedelta(days=1), raw_text="b", category="Meeting", confidence=0.9
    )
    repo.create(today)
    repo.create(tomorrow)

    todays = repo.list_by_day(date(2026, 7, 3))
    assert [a.id for a in todays] == [today.id]


# --------------------------------------------------------------------------- #
# MemoryRepository
# --------------------------------------------------------------------------- #
def test_memory_repository_crud_and_enum_roundtrip(session: Session) -> None:
    repo = MemoryRepository(session)
    activity_id = Activity(
        timestamp=TS, raw_text="x", category="c", confidence=0.9
    ).id
    memory = Memory(
        type=MemoryType.ROUTINE,
        statement="User prefers morning coding.",
        confidence=0.93,
        evidence_count=17,
        supporting_activity_ids=[activity_id],
        status=MemoryStatus.ACTIVE,
    )

    created = repo.create(memory)
    assert created == memory
    assert created.supporting_activity_ids == [activity_id]

    fetched = repo.get_by_id(memory.id)
    assert fetched.type is MemoryType.ROUTINE
    assert fetched.status is MemoryStatus.ACTIVE


def test_memory_repository_filters(session: Session) -> None:
    repo = MemoryRepository(session)
    active = Memory(
        type=MemoryType.GOAL,
        statement="Ship LifeGraph.",
        confidence=0.9,
        evidence_count=5,
        status=MemoryStatus.ACTIVE,
    )
    candidate = Memory(
        type=MemoryType.INTEREST,
        statement="Likes agentic AI.",
        confidence=0.5,
        evidence_count=1,
        status=MemoryStatus.CANDIDATE,
    )
    repo.create(active)
    repo.create(candidate)

    assert [m.id for m in repo.list_active()] == [active.id]
    assert [m.id for m in repo.list_by_type(MemoryType.INTEREST)] == [candidate.id]


# --------------------------------------------------------------------------- #
# TimelineRepository
# --------------------------------------------------------------------------- #
def test_timeline_repository_upsert_and_nested(session: Session) -> None:
    repo = TimelineRepository(session)
    activity = Activity(
        timestamp=TS, raw_text="a", category="Deep Work", confidence=0.9, duration=120
    )
    work_session = WorkSession(
        start_time=TS,
        end_time=TS + timedelta(hours=2),
        duration=120,
        focus_score=0.9,
        activities=[activity],
    )
    timeline = Timeline(
        date=date(2026, 7, 3),
        activities=[activity],
        sessions=[work_session],
        total_duration=120,
        context_switches=1,
    )

    repo.create(timeline)
    fetched = repo.get_by_date(date(2026, 7, 3))
    assert fetched == timeline
    assert fetched.activities[0].id == activity.id
    assert fetched.sessions[0].focus_score == 0.9

    # Upsert: rebuilding the same date replaces it rather than duplicating.
    repo.create(timeline.model_copy(update={"context_switches": 3}))
    assert len(repo.list()) == 1
    assert repo.get_by_date(date(2026, 7, 3)).context_switches == 3

    assert repo.delete(date(2026, 7, 3)) is True
    assert repo.get_by_date(date(2026, 7, 3)) is None


# --------------------------------------------------------------------------- #
# SummaryRepository
# --------------------------------------------------------------------------- #
def test_summary_repository_crud_and_nested(session: Session) -> None:
    repo = SummaryRepository(session)
    summary = DailySummary(
        date=date(2026, 7, 3),
        overview="A focused day.",
        timeline="09:00 Deep Work",
        metrics={"deep_work_minutes": 120},
        insights=[Insight(title="Focus improved", description="Longer sessions", confidence=0.9)],
        recommendations=[
            Recommendation(
                title="Code before lunch",
                reason="Morning focus is strongest",
                expected_impact="Higher throughput",
                priority=Priority.HIGH,
                confidence=0.88,
            )
        ],
        tomorrow_focus="Ship the API layer.",
    )

    created = repo.create(summary)
    assert created == summary

    by_id = repo.get_by_id(summary.id)
    assert by_id == summary
    assert by_id.insights[0].title == "Focus improved"

    by_date = repo.get_by_date(date(2026, 7, 3))
    assert by_date is not None
    assert by_date.recommendations[0].priority is Priority.HIGH
