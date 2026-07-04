"""Persist node: the designated database writer.

The only node that touches repositories. Writes the validated activity, any
memory proposals, the updated timeline, and the daily summary. Persistence
failures are captured in ``errors`` rather than aborting the run.
"""

from __future__ import annotations

from collections.abc import Callable

from sqlmodel import Session

from app.config.logging import get_logger
from app.graph.state import LifeGraphState
from app.models.enums import MemoryType
from app.repositories.activity_repository import ActivityRepository
from app.repositories.memory_repository import MemoryRepository
from app.repositories.summary_repository import SummaryRepository
from app.repositories.timeline_repository import TimelineRepository

_logger = get_logger("app.graph.nodes.persist")


class PersistNode:
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self.session_factory = session_factory

    async def __call__(self, state: LifeGraphState) -> dict:
        if not state.user_id:
            # Without an owner we cannot persist safely; skip writes.
            return {"errors": [*state.errors, "persist: no user_id on state"]}
        uid = state.user_id
        try:
            with self.session_factory() as session:
                memory_repo = MemoryRepository(session, uid)
                activity = state.structured_activity
                if activity is not None:
                    ActivityRepository(session, uid).create(activity)
                    # "Memory is earned": accrue evidence rather than inserting a
                    # fresh candidate each time. Projects come deterministically
                    # from the activity; other memories from the LLM proposals.
                    if activity.project:
                        memory_repo.accumulate_project(activity.project, activity.id)
                    for proposal in state.memory_proposals:
                        key = proposal.metadata.get("key")
                        if not key or proposal.type is None or proposal.type is MemoryType.PROJECT:
                            continue  # projects are owned by the deterministic path
                        memory_repo.accumulate_memory(
                            memory_type=proposal.type,
                            key=key,
                            statement=proposal.statement,
                            activity_id=activity.id,
                            source="memory_node",
                        )
                if state.timeline is not None:
                    TimelineRepository(session, uid).create(state.timeline)
                if state.daily_summary is not None:
                    SummaryRepository(session, uid).create(state.daily_summary)
        except Exception as exc:  # persistence must not abort the graph
            _logger.warning("persist_failed", extra={"error": str(exc)})
            return {"errors": [*state.errors, f"persist: {exc}"]}
        return {}
