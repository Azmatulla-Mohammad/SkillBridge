from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.utils import utcnow
from app.models import ActivityLog, Assignment, Enrollment, Submission
from app.repositories.public import PublicRepository


def record_activity(
    db: Session,
    *,
    actor_user_id: int | None,
    action: str,
    entity_type: str,
    entity_id: int | None,
    summary: str,
    metadata: dict | None = None,
) -> ActivityLog:
    repo = PublicRepository(db)
    activity = ActivityLog(
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        summary=summary,
        metadata_json=metadata,
        created_at=utcnow(),
    )
    return repo.create_activity(activity)


def calculate_progress(db: Session, student_id: int, course_id: int) -> int:
    total_assignments = db.scalar(
        select(func.count(Assignment.id)).where(Assignment.course_id == course_id)
    ) or 0
    if total_assignments == 0:
        return 0

    completed = db.scalar(
        select(func.count(Submission.id))
        .join(Assignment, Submission.assignment_id == Assignment.id)
        .where(
            Submission.student_id == student_id,
            Assignment.course_id == course_id,
        )
    ) or 0
    return min(100, int((completed / total_assignments) * 100))


def sync_enrollment_progress(db: Session, enrollment: Enrollment) -> int:
    progress = calculate_progress(db, enrollment.student_id, enrollment.course_id)
    enrollment.progress_percent = progress
    db.flush()
    return progress

