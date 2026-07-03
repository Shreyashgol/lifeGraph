"""Intelligence layer tests (Phase 5 acceptance: validated proposals, retries)."""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from app.intelligence import (
    ActivityIntelligenceService,
    BehaviourIntelligenceService,
    EvaluationIntelligenceService,
    InvalidLLMResponseError,
    LLMClient,
    LLMTimeoutError,
    MemoryIntelligenceService,
    SummaryIntelligenceService,
)
from app.intelligence.proposals import ActivityProposal
from app.models import Activity

TS = datetime(2026, 7, 3, 9, 0, tzinfo=timezone.utc)


class FakeLLMClient(LLMClient):
    """A queue-driven fake: returns strings, or raises queued exceptions."""

    def __init__(self, responses: list) -> None:
        self._responses = list(responses)
        self.calls: list[dict] = []

    async def complete(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout: float,
        json_mode: bool = False,
    ) -> str:
        self.calls.append({"json_mode": json_mode, "model": model})
        item = self._responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


async def test_activity_service_parses_valid_json() -> None:
    client = FakeLLMClient(['{"category":"Deep Work","duration":120,"confidence":0.96,"people":[]}'])
    proposal = await ActivityIntelligenceService(client).reason(
        activity="Worked on auth", timestamp=TS
    )
    assert isinstance(proposal, ActivityProposal)
    assert proposal.category == "Deep Work"
    assert proposal.duration == 120
    assert client.calls[0]["json_mode"] is True


async def test_activity_service_insufficient_context_returns_none() -> None:
    client = FakeLLMClient(['{"status":"insufficient_context"}'])
    result = await ActivityIntelligenceService(client).reason(activity="", timestamp=TS)
    assert result is None


async def test_retry_on_bad_json_then_success() -> None:
    client = FakeLLMClient(["not json at all", '{"category":"c","confidence":0.5}'])
    proposal = await ActivityIntelligenceService(client).reason(activity="x", timestamp=TS)
    assert proposal is not None and proposal.category == "c"
    assert len(client.calls) == 2


async def test_raises_after_retries_exhausted() -> None:
    client = FakeLLMClient(["bad", "bad", "bad"])  # activity retry_limit == 3
    with pytest.raises(InvalidLLMResponseError):
        await ActivityIntelligenceService(client).reason(activity="x", timestamp=TS)
    assert len(client.calls) == 3


async def test_retry_on_transient_error_then_success() -> None:
    client = FakeLLMClient([LLMTimeoutError("timeout"), '{"category":"c","confidence":0.5}'])
    proposal = await ActivityIntelligenceService(client).reason(activity="x", timestamp=TS)
    assert proposal is not None and proposal.category == "c"


async def test_schema_validation_failure_triggers_retry() -> None:
    # First response is schema-invalid (no category, confidence > 1); second is valid.
    client = FakeLLMClient(['{"confidence":2.0}', '{"category":"c","confidence":0.5}'])
    proposal = await ActivityIntelligenceService(client).reason(activity="x", timestamp=TS)
    assert proposal is not None and proposal.category == "c"
    assert len(client.calls) == 2


async def test_memory_service_parses_action() -> None:
    client = FakeLLMClient(['{"action":"ignore","confidence":0.3,"reason":"single observation"}'])
    activity = Activity(timestamp=TS, raw_text="x", category="c", confidence=0.9)
    proposal = await MemoryIntelligenceService(client).reason(
        structured_activity=activity, memories=[]
    )
    assert proposal is not None and proposal.action == "ignore"


async def test_behaviour_service_parses_pattern_list() -> None:
    client = FakeLLMClient(
        ['{"patterns":[{"category":"Focus","title":"t","description":"d",'
         '"trend":"Increasing","confidence":0.9,"importance":2}]}']
    )
    proposal = await BehaviourIntelligenceService(client).reason(timeline=None, memories=[])
    assert proposal is not None and len(proposal.patterns) == 1
    assert proposal.patterns[0].category.value == "Focus"


async def test_summary_service_returns_markdown_text() -> None:
    client = FakeLLMClient(["## Overview\nA good day."])
    text = await SummaryIntelligenceService(client).reason(
        today=date(2026, 7, 3),
        timeline=None,
        behaviour=[],
        insights=[],
        recommendations=[],
        memories=[],
    )
    assert "Overview" in text
    assert client.calls[0]["json_mode"] is False


async def test_evaluation_service_returns_decision() -> None:
    client = FakeLLMClient(
        ['{"score":0.62,"decision":"retry","feedback":"category looks off",'
         '"retry_reason":"should be Deep Work, not Learning"}']
    )
    proposal = ActivityProposal(category="Learning", confidence=0.5)
    decision = await EvaluationIntelligenceService(client).reason(
        activity="Implemented the auth module", proposal=proposal
    )
    assert decision is not None
    assert decision.decision == "retry"
    assert decision.score == 0.62
    assert decision.retry_reason
