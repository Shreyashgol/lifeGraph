"""ActivityRepository — persistence for Activity."""

from __future__ import annotations

from datetime import date, datetime, time
from uuid import UUID

from sqlmodel import select

from app.database.base import as_utc, to_naive_utc
from app.database.models import ActivityTable
from app.models.activity import Activity
from app.repositories.base import BaseRepository


class ActivityRepository(BaseRepository[Activity]):
    table_cls = ActivityTable

    def _to_row(self, model: Activity) -> ActivityTable:
        return ActivityTable(
            id=str(model.id),
            timestamp=to_naive_utc(model.timestamp),
            raw_text=model.raw_text,
            normalized_text=model.normalized_text,
            category=model.category,
            subcategory=model.subcategory,
            duration=model.duration,
            intent=model.intent,
            project=model.project,
            people=list(model.people),
            location=model.location,
            confidence=model.confidence,
            metadata_=dict(model.metadata),
            evaluation_score=model.evaluation_score,
            evaluation_reason=model.evaluation_reason,
            retry_count=model.retry_count,
            validated=model.validated,
        )

    def _to_domain(self, row: ActivityTable) -> Activity:
        return Activity(
            id=UUID(row.id),
            timestamp=as_utc(row.timestamp),
            raw_text=row.raw_text,
            normalized_text=row.normalized_text,
            category=row.category,
            subcategory=row.subcategory,
            duration=row.duration,
            intent=row.intent,
            project=row.project,
            people=row.people,
            location=row.location,
            confidence=row.confidence,
            metadata=row.metadata_,
            evaluation_score=row.evaluation_score,
            evaluation_reason=row.evaluation_reason,
            retry_count=row.retry_count,
            validated=row.validated,
        )

    def list_by_day(self, day: date) -> list[Activity]:
        """Return the day's activities ordered chronologically.

        Uses a naive-UTC datetime range (portable across SQLite and Postgres)
        rather than a dialect-specific ``date()`` function.
        """
        start = datetime.combine(day, time.min)
        end = datetime.combine(day, time.max)
        statement = (
            select(ActivityTable)
            .where(ActivityTable.timestamp >= start, ActivityTable.timestamp <= end)
            .order_by(ActivityTable.timestamp)
        )
        return [self._to_domain(row) for row in self.session.exec(statement).all()]
