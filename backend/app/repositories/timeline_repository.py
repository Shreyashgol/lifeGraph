"""TimelineRepository — persistence for the daily Timeline.

The Timeline domain model has no id; it is keyed by ``date`` (one per day).
Nested activities and sessions are stored as JSON document aggregates, so this
repository keys on date rather than the generic string-id CRUD of
:class:`BaseRepository`.
"""

from __future__ import annotations

from datetime import date

from sqlmodel import Session, select

from app.database.models import TimelineTable
from app.models.activity import Activity
from app.models.session import Session as WorkSession
from app.models.timeline import Timeline


class TimelineRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def _to_row(self, model: Timeline) -> TimelineTable:
        return TimelineTable(
            date=model.date,
            activities=[a.model_dump(mode="json") for a in model.activities],
            sessions=[s.model_dump(mode="json") for s in model.sessions],
            total_duration=model.total_duration,
            context_switches=model.context_switches,
        )

    def _to_domain(self, row: TimelineTable) -> Timeline:
        return Timeline(
            date=row.date,
            activities=[Activity.model_validate(a) for a in row.activities],
            sessions=[WorkSession.model_validate(s) for s in row.sessions],
            total_duration=row.total_duration,
            context_switches=row.context_switches,
        )

    def create(self, model: Timeline) -> Timeline:
        """Upsert the timeline for its date (a day's timeline is rebuilt in place)."""
        row = self.session.merge(self._to_row(model))
        self.session.commit()
        return self._to_domain(row)

    # A day's timeline is an aggregate rebuilt in place, so update == create.
    update = create

    def get_by_date(self, day: date) -> Timeline | None:
        row = self.session.get(TimelineTable, day)
        return self._to_domain(row) if row is not None else None

    def list(self) -> list[Timeline]:
        statement = select(TimelineTable).order_by(TimelineTable.date)
        return [self._to_domain(row) for row in self.session.exec(statement).all()]

    def delete(self, day: date) -> bool:
        row = self.session.get(TimelineTable, day)
        if row is None:
            return False
        self.session.delete(row)
        self.session.commit()
        return True
