"""SummaryRepository — persistence for DailySummary."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlmodel import select

from app.database.base import to_naive_utc
from app.database.models import SummaryTable
from app.models.base import utcnow
from app.models.insight import Insight
from app.models.recommendation import Recommendation
from app.models.summary import DailySummary
from app.repositories.base import BaseRepository


class SummaryRepository(BaseRepository[DailySummary]):
    table_cls = SummaryTable

    def _to_row(self, model: DailySummary) -> SummaryTable:
        return SummaryTable(
            id=str(model.id),
            date=model.date,
            overview=model.overview,
            timeline=model.timeline,
            metrics=dict(model.metrics),
            insights=[i.model_dump(mode="json") for i in model.insights],
            recommendations=[r.model_dump(mode="json") for r in model.recommendations],
            tomorrow_focus=model.tomorrow_focus,
            created_at=to_naive_utc(utcnow()),
        )

    def _to_domain(self, row: SummaryTable) -> DailySummary:
        return DailySummary(
            id=UUID(row.id),
            date=row.date,
            overview=row.overview,
            timeline=row.timeline,
            metrics=row.metrics,
            insights=[Insight.model_validate(i) for i in row.insights],
            recommendations=[
                Recommendation.model_validate(r) for r in row.recommendations
            ],
            tomorrow_focus=row.tomorrow_focus,
        )

    def get_by_date(self, day: date) -> DailySummary | None:
        """Return the most recent summary for a given day, if any."""
        statement = (
            select(SummaryTable)
            .where(SummaryTable.date == day)
            .order_by(SummaryTable.created_at.desc())
        )
        row = self.session.exec(statement).first()
        return self._to_domain(row) if row is not None else None

    def get_latest(self) -> DailySummary | None:
        """Return the most recently written summary across all days."""
        statement = select(SummaryTable).order_by(SummaryTable.created_at.desc())
        row = self.session.exec(statement).first()
        return self._to_domain(row) if row is not None else None

    def list_dates(
        self, *, start: date | None = None, end: date | None = None
    ) -> list[date]:
        """Return the distinct days that have at least one summary, ascending.

        Powers the calendar view: only dates are loaded (not full summaries), so
        the client can highlight which days are already summarized.
        """
        statement = select(SummaryTable.date).distinct()
        if start is not None:
            statement = statement.where(SummaryTable.date >= start)
        if end is not None:
            statement = statement.where(SummaryTable.date <= end)
        statement = statement.order_by(SummaryTable.date)
        return list(self.session.exec(statement).all())
