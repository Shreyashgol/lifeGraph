"""LifeGraphState tests (Phase 2 acceptance: the graph state contract)."""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from app.graph.state import ExecutionMetadata, LifeGraphState
from app.models import Activity, Memory, MemoryType, Timeline

TS = datetime(2026, 7, 3, 9, 0, tzinfo=UTC)


def test_state_initializes_from_raw_activity() -> None:
    state = LifeGraphState(current_activity="Worked on LifeGraph backend for two hours.")
    assert state.structured_activity is None
    assert state.memories == []
    assert state.memory_proposals == []
    assert state.insights == []
    assert state.recommendations == []
    assert state.daily_summary is None
    assert isinstance(state.execution_metadata, ExecutionMetadata)
    assert state.execution_id is not None


def test_state_model_copy_update_leaves_original_unchanged() -> None:
    state = LifeGraphState(current_activity="x")
    activity = Activity(timestamp=TS, raw_text="x", category="Deep Work", confidence=0.9)

    enriched = state.model_copy(update={"structured_activity": activity})

    assert state.structured_activity is None  # original untouched
    assert enriched.structured_activity == activity
    assert enriched.current_activity == "x"


def test_state_accepts_owned_collections() -> None:
    state = LifeGraphState(
        timeline=Timeline(date=date(2026, 7, 3)),
        memories=[
            Memory(
                type=MemoryType.GOAL,
                statement="Build an AI startup.",
                confidence=0.8,
                evidence_count=3,
            )
        ],
        confidence_scores={"activity": 0.97, "memory": 0.84},
    )
    assert state.timeline is not None
    assert state.timeline.date == date(2026, 7, 3)
    assert state.memories[0].type is MemoryType.GOAL
    assert state.confidence_scores["activity"] == 0.97


def test_state_forbids_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        LifeGraphState(unknown_field=123)


def test_execution_metadata_defaults() -> None:
    metadata = ExecutionMetadata()
    assert metadata.graph_version == "v1"
    assert metadata.retry_count == 0
    assert metadata.prompt_versions == {}
    assert metadata.node_timings == {}


def test_state_json_roundtrip() -> None:
    state = LifeGraphState(current_activity="x", confidence_scores={"activity": 0.9})
    restored = LifeGraphState.model_validate_json(state.model_dump_json())
    assert restored == state
