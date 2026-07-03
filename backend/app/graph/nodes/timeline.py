"""Timeline node: add the activity to the day's chronology (no AI).

Owns ``timeline``.
"""

from __future__ import annotations

from app.graph.state import LifeGraphState
from app.services.timeline_service import TimelineService


class TimelineNode:
    def __init__(self, service: TimelineService) -> None:
        self.service = service

    async def __call__(self, state: LifeGraphState) -> dict:
        activity = state.structured_activity
        if activity is None:
            return {}
        timeline = self.service.add_activity(
            state.timeline, activity, activity.timestamp.date()
        )
        return {"timeline": timeline}
