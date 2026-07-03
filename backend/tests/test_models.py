"""Domain model tests (Phase 2 acceptance: models validate, serialize, pass)."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.models import (
    Activity,
    BehaviourPattern,
    DailySummary,
    Insight,
    Memory,
    MemoryStatus,
    MemoryType,
    Priority,
    Recommendation,
    Session,
    Timeline,
    TrendDirection,
    UserProfile,
)
from app.models.enums import BehaviourCategory

TS = datetime(2026, 7, 3, 9, 0, tzinfo=timezone.utc)


# --------------------------------------------------------------------------- #
# UserProfile
# --------------------------------------------------------------------------- #
def test_userprofile_valid_with_defaults() -> None:
    user = UserProfile(
        name="Shreyash",
        occupation="AI Engineer",
        timezone="Asia/Kolkata",
        goals=["Build AI products"],
    )
    assert user.id is not None
    assert user.interests == []
    assert user.active_projects == []
    assert user.preferences == {}


def test_userprofile_name_stripped() -> None:
    user = UserProfile(
        name="  Shreyash  ", occupation="Eng", timezone="UTC", goals=["g"]
    )
    assert user.name == "Shreyash"


def test_userprofile_blank_name_rejected() -> None:
    with pytest.raises(ValidationError):
        UserProfile(name="   ", occupation="Eng", timezone="UTC", goals=["g"])


def test_userprofile_requires_at_least_one_goal() -> None:
    with pytest.raises(ValidationError):
        UserProfile(name="A", occupation="Eng", timezone="UTC", goals=[])


def test_userprofile_rejects_invalid_timezone() -> None:
    with pytest.raises(ValidationError):
        UserProfile(name="A", occupation="Eng", timezone="Mars/Phobos", goals=["g"])


def test_userprofile_rejects_duplicate_projects() -> None:
    with pytest.raises(ValidationError):
        UserProfile(
            name="A",
            occupation="Eng",
            timezone="UTC",
            goals=["g"],
            active_projects=["X", "X"],
        )


# --------------------------------------------------------------------------- #
# Activity
# --------------------------------------------------------------------------- #
def test_activity_valid_with_defaults() -> None:
    activity = Activity(
        timestamp=TS, raw_text="Worked on LifeGraph", category="Deep Work", confidence=0.96
    )
    assert activity.duration == 0
    assert activity.people == []
    assert activity.metadata == {}
    assert activity.project is None


@pytest.mark.parametrize("bad", [1.5, -0.1])
def test_activity_confidence_out_of_bounds_rejected(bad: float) -> None:
    with pytest.raises(ValidationError):
        Activity(timestamp=TS, raw_text="x", category="c", confidence=bad)


def test_activity_negative_duration_rejected() -> None:
    with pytest.raises(ValidationError):
        Activity(timestamp=TS, raw_text="x", category="c", confidence=0.5, duration=-5)


@pytest.mark.parametrize("field,value", [("raw_text", ""), ("category", "")])
def test_activity_required_text_fields(field: str, value: str) -> None:
    kwargs = {"timestamp": TS, "raw_text": "x", "category": "c", "confidence": 0.5}
    kwargs[field] = value
    with pytest.raises(ValidationError):
        Activity(**kwargs)


def test_activity_forbids_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        Activity(
            timestamp=TS, raw_text="x", category="c", confidence=0.5, unexpected="nope"
        )


# --------------------------------------------------------------------------- #
# Session / Timeline
# --------------------------------------------------------------------------- #
def test_session_valid() -> None:
    session = Session(
        start_time=TS, end_time=TS + timedelta(hours=2), duration=120, focus_score=0.9
    )
    assert session.activities == []


def test_session_end_before_start_rejected() -> None:
    with pytest.raises(ValidationError):
        Session(
            start_time=TS, end_time=TS - timedelta(hours=1), duration=60, focus_score=0.5
        )


def test_session_focus_score_out_of_bounds_rejected() -> None:
    with pytest.raises(ValidationError):
        Session(
            start_time=TS, end_time=TS + timedelta(hours=1), duration=60, focus_score=1.2
        )


def test_timeline_valid_defaults() -> None:
    timeline = Timeline(date=date(2026, 7, 3))
    assert timeline.total_duration == 0
    assert timeline.context_switches == 0
    assert timeline.activities == []
    assert timeline.sessions == []


# --------------------------------------------------------------------------- #
# Memory
# --------------------------------------------------------------------------- #
def test_memory_valid_defaults() -> None:
    memory = Memory(
        type=MemoryType.ROUTINE,
        statement="User prefers coding in the morning.",
        confidence=0.93,
        evidence_count=17,
    )
    assert memory.status is MemoryStatus.CANDIDATE
    assert memory.source is None
    assert memory.expires_at is None
    assert memory.supporting_activity_ids == []


def test_memory_evidence_count_minimum_one() -> None:
    with pytest.raises(ValidationError):
        Memory(type=MemoryType.ROUTINE, statement="x", confidence=0.5, evidence_count=0)


def test_memory_empty_statement_rejected() -> None:
    with pytest.raises(ValidationError):
        Memory(type=MemoryType.GOAL, statement="", confidence=0.5, evidence_count=1)


def test_memory_confidence_out_of_bounds_rejected() -> None:
    with pytest.raises(ValidationError):
        Memory(type=MemoryType.GOAL, statement="x", confidence=2.0, evidence_count=1)


# --------------------------------------------------------------------------- #
# BehaviourPattern / Insight / Recommendation
# --------------------------------------------------------------------------- #
def test_behaviour_pattern_valid_defaults() -> None:
    pattern = BehaviourPattern(
        category=BehaviourCategory.FOCUS,
        title="Morning Deep Work",
        description="Consistently codes in the morning.",
        confidence=0.91,
    )
    assert pattern.trend is TrendDirection.UNKNOWN
    assert pattern.evidence == []
    assert pattern.importance == 0


def test_insight_valid() -> None:
    insight = Insight(
        title="Morning productivity improved.",
        description="Focus sessions grew longer.",
        confidence=0.94,
    )
    assert insight.evidence == []


def test_recommendation_valid() -> None:
    rec = Recommendation(
        title="Schedule coding before lunch.",
        reason="Morning focus consistently exceeds afternoon focus.",
        expected_impact="Higher focus and throughput.",
        priority=Priority.HIGH,
        confidence=0.88,
    )
    assert rec.priority is Priority.HIGH


def test_recommendation_requires_reason() -> None:
    with pytest.raises(ValidationError):
        Recommendation(
            title="x", reason="", expected_impact="y", priority=Priority.LOW, confidence=0.5
        )


# --------------------------------------------------------------------------- #
# DailySummary
# --------------------------------------------------------------------------- #
def test_daily_summary_valid_defaults() -> None:
    summary = DailySummary(
        date=date(2026, 7, 3),
        overview="A focused day.",
        timeline="09:00 Deep Work",
        tomorrow_focus="Ship the API layer.",
    )
    assert summary.insights == []
    assert summary.recommendations == []
    assert summary.metrics == {}


# --------------------------------------------------------------------------- #
# Serialization
# --------------------------------------------------------------------------- #
def test_activity_json_roundtrip() -> None:
    activity = Activity(
        timestamp=TS,
        raw_text="Worked on auth",
        category="Deep Work",
        project="LifeGraph",
        duration=120,
        confidence=0.9,
    )
    restored = Activity.model_validate_json(activity.model_dump_json())
    assert restored == activity


def test_memory_serializes_enum_values() -> None:
    memory = Memory(
        type=MemoryType.INTEREST,
        statement="Enjoys agentic AI.",
        confidence=0.8,
        evidence_count=5,
    )
    dumped = memory.model_dump()
    assert dumped["type"] == "interest"
    assert dumped["status"] == "candidate"
    assert Memory.model_validate_json(memory.model_dump_json()) == memory


def test_daily_summary_nested_json_roundtrip() -> None:
    summary = DailySummary(
        date=date(2026, 7, 3),
        overview="o",
        timeline="t",
        tomorrow_focus="f",
        insights=[Insight(title="i", description="d", confidence=0.9)],
        recommendations=[
            Recommendation(
                title="r",
                reason="because evidence",
                expected_impact="x",
                priority=Priority.MEDIUM,
                confidence=0.7,
            )
        ],
    )
    restored = DailySummary.model_validate_json(summary.model_dump_json())
    assert restored == summary
    assert restored.insights[0].title == "i"


def test_enum_values_match_data_contract() -> None:
    assert Priority.HIGH.value == "High"
    assert TrendDirection.INCREASING.value == "Increasing"
    assert BehaviourCategory.CONTEXT_SWITCHING.value == "Context Switching"
    assert MemoryType.ROUTINE.value == "routine"
