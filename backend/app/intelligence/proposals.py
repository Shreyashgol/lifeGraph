"""AI proposal schemas.

Proposals are the *structured outputs* of the intelligence services — validated
but not yet approved or persisted (docs/08 §22). They are distinct from domain
models: they use ``extra="ignore"`` so a stray key from the model does not fail
validation, and they carry only what the LLM returns.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import BehaviourCategory, MemoryType, Priority, TrendDirection


def _coerce_int(v: object) -> object:
    """Coerce an LLM-supplied number to ``int``.

    Smaller models often emit ``3.0`` or ``0.8`` for integer fields (e.g.
    ``importance``, ``duration``). We round numeric values so a stray float does
    not fail validation; anything unparseable falls through to normal validation.
    """
    if isinstance(v, bool):
        return v
    if isinstance(v, float):
        return round(v)
    if isinstance(v, str):
        try:
            return round(float(v.strip()))
        except ValueError:
            return v
    return v


class _ProposalBase(BaseModel):
    """Lenient base: ignore unexpected keys from the model."""

    model_config = ConfigDict(extra="ignore")


class ActivityProposal(_ProposalBase):
    """Structured activity produced by the Activity service."""

    category: str
    subcategory: str | None = None
    intent: str | None = None
    duration: int = Field(default=0, ge=0)
    project: str | None = None
    people: list[str] = Field(default_factory=list)
    location: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)

    _coerce_duration = field_validator("duration", mode="before")(_coerce_int)


class MemoryProposal(_ProposalBase):
    """A proposed memory action (create/update/ignore).

    ``subject`` is a short, stable, canonical key (e.g. "agentic ai", "python",
    "morning coding") used to accumulate evidence across observations.
    """

    action: Literal["create", "update", "ignore"]
    type: MemoryType | None = None
    subject: str | None = None
    statement: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str


class BehaviourPatternItem(_ProposalBase):
    category: BehaviourCategory
    title: str
    description: str
    trend: TrendDirection = TrendDirection.UNKNOWN
    confidence: float = Field(ge=0.0, le=1.0)
    importance: int = 0

    _coerce_importance = field_validator("importance", mode="before")(_coerce_int)


class BehaviourProposal(_ProposalBase):
    patterns: list[BehaviourPatternItem] = Field(default_factory=list)


class InsightItem(_ProposalBase):
    title: str
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    importance: int = 0

    _coerce_importance = field_validator("importance", mode="before")(_coerce_int)


class InsightProposal(_ProposalBase):
    insights: list[InsightItem] = Field(default_factory=list)


class RecommendationItem(_ProposalBase):
    title: str
    reason: str
    expected_impact: str
    priority: Priority
    confidence: float = Field(ge=0.0, le=1.0)


class RecommendationProposal(_ProposalBase):
    recommendations: list[RecommendationItem] = Field(default_factory=list)


class ReflectionProposal(_ProposalBase):
    """End-of-graph holistic QA result (docs/08 §14)."""

    approved: bool
    warnings: list[str] = Field(default_factory=list)
    notes: str = ""
    suggest_retry: bool = False


class EvaluationDecision(_ProposalBase):
    """LLM-as-a-judge verdict on another service's proposal.

    ``decision`` drives the graph's conditional retry edge (approve -> continue,
    retry -> re-run the source node with ``retry_reason`` injected, reject ->
    stop). Retries are capped by the graph (max 2).
    """

    decision: Literal["approve", "retry", "reject"]
    score: float = Field(ge=0.0, le=1.0)
    feedback: str = ""
    retry_reason: str = ""
