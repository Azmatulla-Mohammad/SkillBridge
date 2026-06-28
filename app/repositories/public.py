from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import ActivityLog, Inquiry


class PublicRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_inquiry(self, inquiry: Inquiry) -> Inquiry:
        self.db.add(inquiry)
        self.db.flush()
        self.db.refresh(inquiry)
        return inquiry

    def create_activity(self, activity: ActivityLog) -> ActivityLog:
        self.db.add(activity)
        self.db.flush()
        self.db.refresh(activity)
        return activity

    def recent_activity(self, limit: int = 8) -> list[ActivityLog]:
        stmt = (
            select(ActivityLog)
            .options(joinedload(ActivityLog.actor))
            .order_by(ActivityLog.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).unique().all())

    def list_activity_logs(
        self,
        *,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ActivityLog], int]:
        stmt = select(ActivityLog).options(joinedload(ActivityLog.actor))
        if search:
            term = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    ActivityLog.summary.ilike(term),
                    ActivityLog.action.ilike(term),
                    ActivityLog.entity_type.ilike(term),
                )
            )

        total = self.db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
        items = list(
            self.db.scalars(
                stmt.order_by(ActivityLog.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            .unique()
            .all()
        )
        return items, total
