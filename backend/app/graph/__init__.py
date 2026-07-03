"""Orchestration layer (LangGraph).

The heart of LifeGraph. Owns the StateGraph builder, ``LifeGraphState``, nodes,
edges, and checkpointing. Coordinates business rules; it does not implement
reasoning or persistence.
"""

from app.graph.builder import build_graph
from app.graph.checkpointer import create_checkpointer
from app.graph.edges import route_after_evaluation
from app.graph.state import ExecutionMetadata, LifeGraphState

__all__ = [
    "ExecutionMetadata",
    "LifeGraphState",
    "build_graph",
    "create_checkpointer",
    "route_after_evaluation",
]
