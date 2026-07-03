"""Intelligence layer (AI reasoning services).

Each service performs exactly one reasoning task: build a prompt, invoke the
model client, parse and validate the response, and return a structured
*proposal*. Services never persist data, mutate graph state, call repositories,
or call one another.
"""

from app.intelligence.activity_service import ActivityIntelligenceService
from app.intelligence.behaviour_service import BehaviourIntelligenceService
from app.intelligence.errors import (
    IntelligenceError,
    InvalidLLMResponseError,
    LLMError,
    LLMRateLimitError,
    LLMResponseError,
    LLMTimeoutError,
)
from app.intelligence.evaluation_service import EvaluationIntelligenceService
from app.intelligence.groq_client import GroqClient
from app.intelligence.insight_service import InsightIntelligenceService
from app.intelligence.llm_client import LLMClient
from app.intelligence.memory_service import MemoryIntelligenceService
from app.intelligence.proposals import (
    ActivityProposal,
    BehaviourProposal,
    EvaluationDecision,
    InsightProposal,
    MemoryProposal,
    RecommendationProposal,
    ReflectionProposal,
)
from app.intelligence.recommendation_service import RecommendationIntelligenceService
from app.intelligence.reflection_service import ReflectionIntelligenceService
from app.intelligence.summary_service import SummaryIntelligenceService

__all__ = [
    "ActivityIntelligenceService",
    "ActivityProposal",
    "BehaviourIntelligenceService",
    "BehaviourProposal",
    "EvaluationDecision",
    "EvaluationIntelligenceService",
    "GroqClient",
    "InsightIntelligenceService",
    "InsightProposal",
    "IntelligenceError",
    "InvalidLLMResponseError",
    "LLMClient",
    "LLMError",
    "LLMRateLimitError",
    "LLMResponseError",
    "LLMTimeoutError",
    "MemoryIntelligenceService",
    "MemoryProposal",
    "RecommendationIntelligenceService",
    "RecommendationProposal",
    "ReflectionIntelligenceService",
    "ReflectionProposal",
    "SummaryIntelligenceService",
]
