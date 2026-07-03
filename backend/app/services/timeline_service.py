"""Deterministic timeline construction (no AI).

Adds an activity to the day's timeline, keeping it ordered and recomputing
duration and context-switch statistics.
"""

from __future__ import annotations

from datetime import date

from app.models.activity import Activity
from app.models.timeline import Timeline


class TimelineService:
    """Builds and updates the daily :class:`Timeline` from activities."""

    def add_activity(
        self, timeline: Timeline | None, activity: Activity, day: date
    ) -> Timeline:
        existing = list(timeline.activities) if timeline else []
        activities = sorted([*existing, activity], key=lambda a: a.timestamp)
        return Timeline(
            date=timeline.date if timeline else day,
            activities=activities,
            sessions=list(timeline.sessions) if timeline else [],
            total_duration=sum(a.duration for a in activities),
            context_switches=self._count_context_switches(activities),
        )

    @staticmethod
    def _count_context_switches(activities: list[Activity]) -> int:
        """Count transitions between distinct project/category contexts."""
        switches = 0
        previous: str | None = None
        for activity in activities:
            current = activity.project or activity.category
            if previous is not None and current != previous:
                switches += 1
            previous = current
        return switches
