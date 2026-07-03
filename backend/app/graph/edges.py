"""Graph edges: routing decisions only, no business logic.

The single conditional edge is the Evaluation retry loop. It reads the verdict
the Evaluation node wrote onto ``structured_activity`` and decides where to go
next — it does not re-judge.
"""

from __future__ import annotations

from app.config.constants import MAX_QUALITY_RETRIES
from app.graph.state import LifeGraphState

# Route targets (node names).
CONTINUE = "context"
RETRY = "activity"


def route_after_evaluation(state: LifeGraphState) -> str:
    """Approve/exhausted -> continue; otherwise retry the Activity node (max 2)."""
    activity = state.structured_activity
    if activity is None or activity.validated:
        return CONTINUE
    if activity.retry_count >= MAX_QUALITY_RETRIES:
        return CONTINUE
    return RETRY
