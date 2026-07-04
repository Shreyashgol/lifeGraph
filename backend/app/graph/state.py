"""LifeGraphState — the central data contract of the application.

Every LangGraph node receives the current state, enriches it, and returns an
updated state. Nodes never communicate with one another directly; all
communication flows through ``LifeGraphState`` (see ``docs/07_DATA_MODELS.md``
§14). State is the application's *working memory* (docs/10 §17): transient and
never persisted directly.

Nodes update only the fields they own (the ownership matrix in docs/07 §14) and
prefer :meth:`~pydantic.BaseModel.model_copy` (``update={...}``) over in-place
mutation so state transitions stay traceable.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.models.activity import Activity
from app.models.behaviour import BehaviourPattern
from app.models.insight import Insight
from app.models.memory import Memory
from app.models.recommendation import Recommendation
from app.models.summary import DailySummary
from app.models.timeline import Timeline
from app.models.user import UserProfile


class ExecutionMetadata(BaseModel):
    """Observability metadata for one graph execution (docs/07 §14).

    This metadata never influences reasoning; its sole purpose is observability
    (owned by the Reflection node).
    """

    model_config = ConfigDict(extra="forbid")

    execution_id: UUID = Field(default_factory=uuid4)
    graph_version: str = "v1"
    prompt_versions: dict[str, str] = Field(default_factory=dict)
    model_name: str | None = None
    total_runtime_ms: float | None = None
    retry_count: int = Field(default=0, ge=0)
    node_timings: dict[str, float] = Field(default_factory=dict)
    validation_results: dict[str, Any] = Field(default_factory=dict)


class LifeGraphState(BaseModel):
    """Shared execution state threaded through every graph node.

    Fields are grouped by owning node (docs/07 §14). Collections default to empty
    and single objects default to ``None`` so the state can be initialized from
    just a raw activity and progressively enriched.
    """

    model_config = ConfigDict(extra="forbid")

    # Graph Builder
    execution_id: UUID = Field(default_factory=uuid4)

    # Owner of this run — every persisted row is scoped to this user.
    user_id: str | None = None

    # User Service
    user_profile: UserProfile | None = None

    # Activity Node
    current_activity: str | None = Field(
        default=None, description="Raw natural-language activity text."
    )
    structured_activity: Activity | None = None

    # Context Node
    relevant_context: dict[str, Any] = Field(default_factory=dict)

    # Timeline Node
    timeline: Timeline | None = None

    # Memory Node
    memories: list[Memory] = Field(default_factory=list)
    memory_proposals: list[Memory] = Field(default_factory=list)

    # Behaviour Node
    behaviour_patterns: list[BehaviourPattern] = Field(default_factory=list)

    # Insight Node
    insights: list[Insight] = Field(default_factory=list)

    # Recommendation Node
    recommendations: list[Recommendation] = Field(default_factory=list)

    # Summary Node
    daily_summary: DailySummary | None = None

    # Reflection Node
    execution_metadata: ExecutionMetadata = Field(default_factory=ExecutionMetadata)
    confidence_scores: dict[str, float] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
