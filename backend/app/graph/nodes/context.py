"""Context node: select only the context relevant to the current activity.

No AI reasoning. Reads ``structured_activity``, ``user_profile``, ``memories``;
owns ``relevant_context``.
"""

from __future__ import annotations

from app.graph.state import LifeGraphState
from app.models.enums import MemoryType
from app.models.memory import Memory

_ALWAYS_RELEVANT = {MemoryType.IDENTITY, MemoryType.GOAL, MemoryType.PROJECT}


class ContextNode:
    async def __call__(self, state: LifeGraphState) -> dict:
        activity = state.structured_activity
        context: dict = {}

        if state.user_profile is not None:
            context["goals"] = state.user_profile.goals
            context["active_projects"] = state.user_profile.active_projects
            context["preferences"] = state.user_profile.preferences

        if activity is not None and activity.project:
            context["active_project"] = activity.project

        context["relevant_memories"] = [
            m.model_dump(mode="json")
            for m in state.memories
            if self._is_relevant(m, activity.project if activity else None)
        ]
        return {"relevant_context": context}

    @staticmethod
    def _is_relevant(memory: Memory, project: str | None) -> bool:
        if memory.type in _ALWAYS_RELEVANT:
            return True
        if project and project.lower() in memory.statement.lower():
            return True
        return False
