"""Enumerations used across the domain models.

String-valued enums so they serialize to human-readable JSON. Values match the
examples in the canonical data contract (``docs/07_DATA_MODELS.md``).
"""

from __future__ import annotations

from enum import Enum


class MemoryType(str, Enum):
    """Category of a semantic memory (docs/07 §9).

    Version 1 supports the seven memory domains enumerated by the canonical data
    contract. Additional domains from docs/10 (skills, relationships, health,
    finance) are deferred to later versions.
    """

    IDENTITY = "identity"
    GOAL = "goal"
    PROJECT = "project"
    ROUTINE = "routine"
    BEHAVIOUR = "behaviour"
    PREFERENCE = "preference"
    INTEREST = "interest"


class MemoryStatus(str, Enum):
    """Lifecycle state of a memory (docs/10 §10).

    Only ``ACTIVE`` memories participate in reasoning; ``CANDIDATE`` memories are
    still accumulating evidence.
    """

    CANDIDATE = "candidate"
    ACTIVE = "active"
    ARCHIVED = "archived"


class BehaviourCategory(str, Enum):
    """Behavioural pattern category (docs/07 §10)."""

    PRODUCTIVITY = "Productivity"
    FOCUS = "Focus"
    ROUTINE = "Routine"
    LEARNING = "Learning"
    CONTEXT_SWITCHING = "Context Switching"
    MEETINGS = "Meetings"
    ENERGY = "Energy"
    WORK_STYLE = "Work Style"


class TrendDirection(str, Enum):
    """Direction of a behavioural trend (docs/07 §10)."""

    INCREASING = "Increasing"
    STABLE = "Stable"
    DECREASING = "Decreasing"
    UNKNOWN = "Unknown"


class Priority(str, Enum):
    """Recommendation priority (docs/07 §12)."""

    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
