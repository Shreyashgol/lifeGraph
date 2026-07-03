"""Graph builder: wiring only, no business logic (docs/06 §37 Rule 8).

Constructs the intelligence services, validators, and nodes, then assembles the
LangGraph ``StateGraph``. Dependencies (the LLM client and the persistence
session factory) are injected so the graph is testable with fakes.

Execution order (docs/12 Phase 6 + the Evaluation addition):

    START -> activity -> evaluation -> context -> memory -> timeline ->
    behaviour -> insight -> recommendation -> summary -> reflection ->
    persist -> END

with a conditional retry edge evaluation -> activity (max 2).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from sqlmodel import Session

from app.graph.edges import route_after_evaluation
from app.graph.nodes import (
    ActivityNode,
    BehaviourNode,
    ContextNode,
    EvaluationNode,
    InsightNode,
    MemoryNode,
    PersistNode,
    RecommendationNode,
    ReflectionNode,
    SummaryNode,
    TimelineNode,
)
from app.graph.state import LifeGraphState
from app.intelligence.activity_service import ActivityIntelligenceService
from app.intelligence.behaviour_service import BehaviourIntelligenceService
from app.intelligence.evaluation_service import EvaluationIntelligenceService
from app.intelligence.insight_service import InsightIntelligenceService
from app.intelligence.llm_client import LLMClient
from app.intelligence.memory_service import MemoryIntelligenceService
from app.intelligence.recommendation_service import RecommendationIntelligenceService
from app.intelligence.reflection_service import ReflectionIntelligenceService
from app.intelligence.summary_service import SummaryIntelligenceService
from app.services.timeline_service import TimelineService
from app.validators.activity_validator import ActivityValidator
from app.validators.memory_validator import MemoryValidator


def build_graph(
    *,
    llm_client: LLMClient,
    session_factory: Callable[[], Session],
    checkpointer: Any | None = None,
) -> Any:
    """Assemble and compile the LifeGraph reasoning graph."""
    # Lazy import keeps the module importable without langgraph installed.
    from langgraph.graph import END, START, StateGraph

    nodes = {
        "activity": ActivityNode(ActivityIntelligenceService(llm_client), ActivityValidator()),
        "evaluation": EvaluationNode(EvaluationIntelligenceService(llm_client)),
        "context": ContextNode(),
        "memory": MemoryNode(MemoryIntelligenceService(llm_client), MemoryValidator()),
        "timeline": TimelineNode(TimelineService()),
        "behaviour": BehaviourNode(BehaviourIntelligenceService(llm_client)),
        "insight": InsightNode(InsightIntelligenceService(llm_client)),
        "recommendation": RecommendationNode(RecommendationIntelligenceService(llm_client)),
        "summary": SummaryNode(SummaryIntelligenceService(llm_client)),
        "reflection": ReflectionNode(ReflectionIntelligenceService(llm_client)),
        "persist": PersistNode(session_factory),
    }

    builder = StateGraph(LifeGraphState)
    for name, node in nodes.items():
        builder.add_node(name, node)

    builder.add_edge(START, "activity")
    builder.add_edge("activity", "evaluation")
    builder.add_conditional_edges(
        "evaluation",
        route_after_evaluation,
        {"activity": "activity", "context": "context"},
    )
    builder.add_edge("context", "memory")
    builder.add_edge("memory", "timeline")
    builder.add_edge("timeline", "behaviour")
    builder.add_edge("behaviour", "insight")
    builder.add_edge("insight", "recommendation")
    builder.add_edge("recommendation", "summary")
    builder.add_edge("summary", "reflection")
    builder.add_edge("reflection", "persist")
    builder.add_edge("persist", END)

    return builder.compile(checkpointer=checkpointer)
