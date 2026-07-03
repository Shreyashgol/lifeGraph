"""Domain models.

Pydantic representations of business concepts (UserProfile, Activity, Session,
Timeline, Memory, BehaviourPattern, Insight, Recommendation, DailySummary).
Independent of FastAPI and SQLModel. The graph state (``LifeGraphState``) lives
in ``app/graph`` because it is a graph model, not a domain model.
"""

from app.models.activity import Activity
from app.models.behaviour import BehaviourPattern
from app.models.enums import (
    BehaviourCategory,
    MemoryStatus,
    MemoryType,
    Priority,
    TrendDirection,
)
from app.models.insight import Insight
from app.models.memory import Memory
from app.models.recommendation import Recommendation
from app.models.session import Session
from app.models.summary import DailySummary
from app.models.timeline import Timeline
from app.models.user import UserProfile

__all__ = [
    "Activity",
    "BehaviourCategory",
    "BehaviourPattern",
    "DailySummary",
    "Insight",
    "Memory",
    "MemoryStatus",
    "MemoryType",
    "Priority",
    "Recommendation",
    "Session",
    "Timeline",
    "TrendDirection",
    "UserProfile",
]
