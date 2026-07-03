"""Graph nodes — one file per node.

Each node reads only the ``LifeGraphState`` fields it needs, updates only the
fields it owns, and returns a partial-update dict. Nodes never call each other
and never embed prompts.
"""

from app.graph.nodes.activity import ActivityNode
from app.graph.nodes.behaviour import BehaviourNode
from app.graph.nodes.context import ContextNode
from app.graph.nodes.evaluation import EvaluationNode
from app.graph.nodes.insight import InsightNode
from app.graph.nodes.memory import MemoryNode
from app.graph.nodes.persist import PersistNode
from app.graph.nodes.recommendation import RecommendationNode
from app.graph.nodes.reflection import ReflectionNode
from app.graph.nodes.summary import SummaryNode
from app.graph.nodes.timeline import TimelineNode

__all__ = [
    "ActivityNode",
    "BehaviourNode",
    "ContextNode",
    "EvaluationNode",
    "InsightNode",
    "MemoryNode",
    "PersistNode",
    "RecommendationNode",
    "ReflectionNode",
    "SummaryNode",
    "TimelineNode",
]
