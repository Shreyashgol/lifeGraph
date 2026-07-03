"""Graph tests (Phase 6): node behaviour, routing, and end-to-end execution."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.config.constants import MAX_QUALITY_RETRIES
from app.graph.edges import route_after_evaluation
from app.graph.nodes import ActivityNode, ContextNode, EvaluationNode, MemoryNode
from app.graph.state import LifeGraphState
from app.intelligence.llm_client import LLMClient
from app.intelligence.proposals import ActivityProposal, EvaluationDecision, MemoryProposal
from app.models import Activity, Memory, MemoryStatus, MemoryType, UserProfile
from app.services.timeline_service import TimelineService
from app.validators import ActivityValidator, MemoryValidator

TS = datetime(2026, 7, 3, 9, 0, tzinfo=timezone.utc)


class _FakeService:
    """Returns a fixed proposal from ``reason(**kwargs)``."""

    def __init__(self, result: object) -> None:
        self._result = result

    async def reason(self, **kwargs: object) -> object:
        return self._result


def _activity(**overrides: object) -> Activity:
    base = dict(timestamp=TS, raw_text="x", category="Deep Work", confidence=0.9)
    base.update(overrides)
    return Activity(**base)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# ActivityNode
# --------------------------------------------------------------------------- #
async def test_activity_node_builds_structured_activity() -> None:
    proposal = ActivityProposal(category="Deep Work", duration=120, confidence=0.9, project="LifeGraph")
    node = ActivityNode(_FakeService(proposal), ActivityValidator())
    update = await node(LifeGraphState(current_activity="Worked on LifeGraph"))

    activity = update["structured_activity"]
    assert activity.category == "Deep Work"
    assert activity.raw_text == "Worked on LifeGraph"
    assert activity.validated is False


async def test_activity_node_injects_retry_feedback() -> None:
    captured: dict = {}

    class CapturingService:
        async def reason(self, **kwargs: object) -> ActivityProposal:
            captured.update(kwargs)
            return ActivityProposal(category="Deep Work", confidence=0.9)

    previous = _activity(
        category="Learning", confidence=0.5, retry_count=1, evaluation_reason="should be Deep Work"
    )
    node = ActivityNode(CapturingService(), ActivityValidator())
    update = await node(LifeGraphState(current_activity="x", structured_activity=previous))

    assert captured["context"]["evaluation_feedback"] == "should be Deep Work"
    assert update["structured_activity"].retry_count == 1  # carried forward
    assert update["structured_activity"].timestamp == TS  # preserved across retry


# --------------------------------------------------------------------------- #
# EvaluationNode + routing
# --------------------------------------------------------------------------- #
async def test_evaluation_node_approve_marks_validated() -> None:
    node = EvaluationNode(_FakeService(EvaluationDecision(decision="approve", score=0.95, feedback="good")))
    update = await node(LifeGraphState(current_activity="x", structured_activity=_activity()))
    activity = update["structured_activity"]
    assert activity.validated is True
    assert activity.evaluation_score == 0.95


async def test_evaluation_node_retry_increments_count() -> None:
    node = EvaluationNode(
        _FakeService(EvaluationDecision(decision="retry", score=0.4, retry_reason="wrong category"))
    )
    update = await node(
        LifeGraphState(current_activity="x", structured_activity=_activity(retry_count=0))
    )
    activity = update["structured_activity"]
    assert activity.validated is False
    assert activity.retry_count == 1
    assert activity.evaluation_reason == "wrong category"


async def test_evaluation_node_reject_pins_retry_to_cap() -> None:
    node = EvaluationNode(_FakeService(EvaluationDecision(decision="reject", score=0.1)))
    update = await node(LifeGraphState(current_activity="x", structured_activity=_activity()))
    assert update["structured_activity"].retry_count == MAX_QUALITY_RETRIES


def test_route_after_evaluation() -> None:
    assert route_after_evaluation(LifeGraphState(structured_activity=_activity(validated=True))) == "context"
    assert (
        route_after_evaluation(
            LifeGraphState(structured_activity=_activity(validated=False, retry_count=1))
        )
        == "activity"
    )
    assert (
        route_after_evaluation(
            LifeGraphState(structured_activity=_activity(validated=False, retry_count=MAX_QUALITY_RETRIES))
        )
        == "context"
    )


# --------------------------------------------------------------------------- #
# ContextNode / MemoryNode / TimelineService / validators
# --------------------------------------------------------------------------- #
async def test_context_node_selects_relevant_memories() -> None:
    profile = UserProfile(
        name="A", occupation="Eng", timezone="UTC", goals=["g"], active_projects=["LifeGraph"]
    )
    goal_mem = Memory(type=MemoryType.GOAL, statement="Build an AI startup", confidence=0.9, evidence_count=3)
    pref_mem = Memory(type=MemoryType.PREFERENCE, statement="likes tea", confidence=0.9, evidence_count=3)
    state = LifeGraphState(
        user_profile=profile,
        memories=[goal_mem, pref_mem],
        structured_activity=_activity(project="LifeGraph"),
    )
    context = (await ContextNode()(state))["relevant_context"]

    assert context["active_project"] == "LifeGraph"
    statements = [m["statement"] for m in context["relevant_memories"]]
    assert "Build an AI startup" in statements  # goal always relevant
    assert "likes tea" not in statements  # preference, no project match


async def test_memory_node_ignore_returns_no_update() -> None:
    node = MemoryNode(
        _FakeService(MemoryProposal(action="ignore", confidence=0.3, reason="single observation")),
        MemoryValidator(),
    )
    update = await node(LifeGraphState(current_activity="x", structured_activity=_activity()))
    assert update == {}


async def test_memory_node_create_adds_candidate() -> None:
    proposal = MemoryProposal(
        action="create",
        type=MemoryType.ROUTINE,
        statement="Prefers morning coding",
        confidence=0.8,
        reason="repeated",
    )
    node = MemoryNode(_FakeService(proposal), MemoryValidator())
    update = await node(LifeGraphState(current_activity="x", structured_activity=_activity()))

    proposals = update["memory_proposals"]
    assert len(proposals) == 1
    assert proposals[0].status is MemoryStatus.CANDIDATE
    assert proposals[0].evidence_count == 1


def test_timeline_service_counts_context_switches() -> None:
    service = TimelineService()
    a1 = _activity(project="LifeGraph", duration=60)
    a2 = _activity(timestamp=TS + timedelta(hours=1), category="Meeting", duration=30)
    timeline = service.add_activity(None, a1, date(2026, 7, 3))
    timeline = service.add_activity(timeline, a2, date(2026, 7, 3))

    assert timeline.total_duration == 90
    assert len(timeline.activities) == 2
    assert timeline.context_switches == 1


def test_activity_validator_rejects_low_confidence() -> None:
    assert ActivityValidator().validate(ActivityProposal(category="c", confidence=0.4)).ok is False
    assert ActivityValidator().validate(ActivityProposal(category="c", confidence=0.9)).ok is True


def test_memory_validator_rules() -> None:
    assert MemoryValidator().validate(MemoryProposal(action="ignore", confidence=0.2, reason="x")).ok
    invalid = MemoryProposal(action="create", type=MemoryType.GOAL, statement="", confidence=0.8, reason="x")
    assert MemoryValidator().validate(invalid).ok is False


# --------------------------------------------------------------------------- #
# Full graph (requires langgraph)
# --------------------------------------------------------------------------- #
class RoutingFakeClient(LLMClient):
    """Routes canned responses by inspecting the prompt's ROLE section."""

    async def complete(self, prompt: str, *, model, temperature, max_tokens, timeout, json_mode=False) -> str:
        if "AI evaluator" in prompt:
            return '{"score":0.95,"decision":"approve","feedback":"ok","retry_reason":""}'
        if "Activity Understanding" in prompt:
            return '{"category":"Deep Work","duration":120,"confidence":0.95,"people":[]}'
        if "Memory Intelligence" in prompt:
            return '{"action":"ignore","confidence":0.3,"reason":"single observation"}'
        if "Behaviour Intelligence" in prompt:
            return '{"patterns":[]}'
        if "Insight Intelligence" in prompt:
            return '{"insights":[]}'
        if "Recommendation Intelligence" in prompt:
            return '{"recommendations":[]}'
        if "Summary Intelligence" in prompt:
            return "## Overview\nA productive day."
        if "Reflection component" in prompt:
            return '{"approved":true,"warnings":[],"notes":"ok","suggest_retry":false}'
        return "{}"


async def test_full_graph_executes_end_to_end() -> None:
    pytest.importorskip("langgraph")
    from app.graph.builder import build_graph

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    from app.database import models  # noqa: F401  (register tables)

    SQLModel.metadata.create_all(engine)

    graph = build_graph(
        llm_client=RoutingFakeClient(),
        session_factory=lambda: Session(engine),
        checkpointer=None,
    )
    initial = LifeGraphState(current_activity="Worked on LifeGraph backend for two hours.")
    result = await graph.ainvoke(initial)

    data = result if isinstance(result, dict) else result.model_dump()
    assert data["structured_activity"] is not None
    assert data["timeline"] is not None
    assert data["daily_summary"] is not None
