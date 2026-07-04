"""Memory node: propose (never persist) a candidate memory.

A new memory always enters as a CANDIDATE with a single observation — memory is
earned through accumulated evidence (docs/10). Owns ``memory_proposals``.
"""

from __future__ import annotations

from app.config.logging import get_logger
from app.graph.state import LifeGraphState
from app.intelligence.errors import IntelligenceError
from app.intelligence.memory_service import MemoryIntelligenceService
from app.models.enums import MemoryStatus, MemoryType
from app.models.memory import Memory
from app.validators.memory_validator import MemoryValidator

_logger = get_logger("app.graph.nodes.memory")


class MemoryNode:
    def __init__(
        self, service: MemoryIntelligenceService, validator: MemoryValidator
    ) -> None:
        self.service = service
        self.validator = validator

    async def __call__(self, state: LifeGraphState) -> dict:
        activity = state.structured_activity
        if activity is None:
            return {}

        try:
            proposal = await self.service.reason(
                structured_activity=activity,
                memories=state.memories,
                context=state.relevant_context,
            )
        except IntelligenceError as exc:
            return {"errors": [*state.errors, f"memory: {exc}"]}

        if proposal is None or proposal.action == "ignore":
            return {}

        result = self.validator.validate(proposal)
        if not result.ok:
            return {"errors": [*state.errors, f"memory: {result.reason}"]}

        statement = proposal.statement or ""
        # A stable key so repeated evidence about the same fact accumulates
        # (the Persist node routes proposals through the accumulator by this key).
        key = (proposal.subject or statement).strip().lower()
        candidate = Memory(
            type=proposal.type or MemoryType.BEHAVIOUR,
            statement=statement,
            confidence=proposal.confidence,
            evidence_count=1,
            supporting_activity_ids=[activity.id],
            status=MemoryStatus.CANDIDATE,
            source="memory_node",
            metadata={"key": key},
        )
        return {"memory_proposals": [*state.memory_proposals, candidate]}
