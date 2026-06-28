from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Announcement,
    Assignment,
    Course,
    Enrollment,
    Material,
    Meeting,
    Submission,
    User,
)


class AcademicRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_course(self, course_id: int) -> Course | None:
        return self.db.get(Course, course_id)

    def get_course_by_slug(self, slug: str) -> Course | None:
        return self.db.scalar(select(Course).where(Course.slug == slug))

    def list_courses(
        self,
        *,
        search: str | None = None,
        is_active: bool | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Course], int]:
        stmt = select(Course)
        if is_active is not None:
            stmt = stmt.where(Course.is_active == is_active)
        if search:
            term = f"%{search.strip()}%"
            stmt = stmt.where(or_(Course.title.ilike(term), Course.description.ilike(term)))

        total = self.db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
        items = list(
            self.db.scalars(
                stmt.order_by(Course.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).all()
        )
        return items, total

    def create_course(self, course: Course) -> Course:
        self.db.add(course)
        self.db.flush()
        self.db.refresh(course)
        return course

    def delete_course(self, course: Course) -> None:
        self.db.delete(course)
        self.db.flush()

    def get_enrollment(self, enrollment_id: int) -> Enrollment | None:
        stmt = (
            select(Enrollment)
            .options(
                joinedload(Enrollment.student),
                joinedload(Enrollment.teacher),
                joinedload(Enrollment.course),
            )
            .where(Enrollment.id == enrollment_id)
        )
        return self.db.scalar(stmt)

    def find_enrollment(self, student_id: int, course_id: int) -> Enrollment | None:
        stmt = select(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id,
        )
        return self.db.scalar(stmt)

    def list_enrollments(
        self,
        *,
        search: str | None = None,
        teacher_id: int | None = None,
        student_id: int | None = None,
        course_id: int | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Enrollment], int]:
        stmt = (
            select(Enrollment)
            .join(User, Enrollment.student_id == User.id)
            .options(
                joinedload(Enrollment.student),
                joinedload(Enrollment.teacher),
                joinedload(Enrollment.course),
            )
        )
        if teacher_id:
            stmt = stmt.where(Enrollment.teacher_id == teacher_id)
        if student_id:
            stmt = stmt.where(Enrollment.student_id == student_id)
        if course_id:
            stmt = stmt.where(Enrollment.course_id == course_id)
        if search:
            term = f"%{search.strip()}%"
            stmt = stmt.where(or_(User.full_name.ilike(term), User.email.ilike(term)))

        total = self.db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
        items = list(
            self.db.scalars(
                stmt.order_by(Enrollment.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            .unique()
            .all()
        )
        return items, total

    def create_enrollment(self, enrollment: Enrollment) -> Enrollment:
        self.db.add(enrollment)
        self.db.flush()
        self.db.refresh(enrollment)
        return enrollment

    def delete_enrollment(self, enrollment: Enrollment) -> None:
        self.db.delete(enrollment)
        self.db.flush()

    def get_material(self, material_id: int) -> Material | None:
        stmt = (
            select(Material)
            .options(joinedload(Material.course), joinedload(Material.teacher))
            .where(Material.id == material_id)
        )
        return self.db.scalar(stmt)

    def list_materials(
        self,
        *,
        course_id: int | None = None,
        teacher_id: int | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Material], int]:
        stmt = select(Material).options(joinedload(Material.course), joinedload(Material.teacher))
        if course_id:
            stmt = stmt.where(Material.course_id == course_id)
        if teacher_id:
            stmt = stmt.where(Material.teacher_id == teacher_id)

        total = self.db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
        items = list(
            self.db.scalars(
                stmt.order_by(Material.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            .unique()
            .all()
        )
        return items, total

    def create_material(self, material: Material) -> Material:
        self.db.add(material)
        self.db.flush()
        self.db.refresh(material)
        return material

    def delete_material(self, material: Material) -> None:
        self.db.delete(material)
        self.db.flush()

    def get_assignment(self, assignment_id: int) -> Assignment | None:
        stmt = (
            select(Assignment)
            .options(joinedload(Assignment.course), joinedload(Assignment.teacher))
            .where(Assignment.id == assignment_id)
        )
        return self.db.scalar(stmt)

    def list_assignments(
        self,
        *,
        course_id: int | None = None,
        teacher_id: int | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Assignment], int]:
        stmt = select(Assignment).options(
            joinedload(Assignment.course),
            joinedload(Assignment.teacher),
        )
        if course_id:
            stmt = stmt.where(Assignment.course_id == course_id)
        if teacher_id:
            stmt = stmt.where(Assignment.teacher_id == teacher_id)
        if search:
            term = f"%{search.strip()}%"
            stmt = stmt.where(or_(Assignment.title.ilike(term), Assignment.description.ilike(term)))

        total = self.db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
        items = list(
            self.db.scalars(
                stmt.order_by(Assignment.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            .unique()
            .all()
        )
        return items, total

    def create_assignment(self, assignment: Assignment) -> Assignment:
        self.db.add(assignment)
        self.db.flush()
        self.db.refresh(assignment)
        return assignment

    def delete_assignment(self, assignment: Assignment) -> None:
        self.db.delete(assignment)
        self.db.flush()

    def get_submission(self, submission_id: int) -> Submission | None:
        stmt = (
            select(Submission)
            .options(
                joinedload(Submission.assignment).joinedload(Assignment.course),
                joinedload(Submission.student),
            )
            .where(Submission.id == submission_id)
        )
        return self.db.scalar(stmt)

    def get_submission_for_assignment_student(
        self,
        assignment_id: int,
        student_id: int,
    ) -> Submission | None:
        stmt = (
            select(Submission)
            .options(joinedload(Submission.assignment), joinedload(Submission.student))
            .where(
                Submission.assignment_id == assignment_id,
                Submission.student_id == student_id,
            )
        )
        return self.db.scalar(stmt)

    def list_submissions(
        self,
        *,
        assignment_id: int | None = None,
        student_id: int | None = None,
        teacher_id: int | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Submission], int]:
        stmt = (
            select(Submission)
            .join(Assignment, Submission.assignment_id == Assignment.id)
            .options(
                joinedload(Submission.assignment).joinedload(Assignment.course),
                joinedload(Submission.student),
            )
        )
        if assignment_id:
            stmt = stmt.where(Submission.assignment_id == assignment_id)
        if student_id:
            stmt = stmt.where(Submission.student_id == student_id)
        if teacher_id:
            stmt = stmt.where(Assignment.teacher_id == teacher_id)

        total = self.db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
        items = list(
            self.db.scalars(
                stmt.order_by(Submission.submitted_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            .unique()
            .all()
        )
        return items, total

    def create_submission(self, submission: Submission) -> Submission:
        self.db.add(submission)
        self.db.flush()
        self.db.refresh(submission)
        return submission

    def get_announcement(self, announcement_id: int) -> Announcement | None:
        stmt = (
            select(Announcement)
            .options(joinedload(Announcement.course), joinedload(Announcement.teacher))
            .where(Announcement.id == announcement_id)
        )
        return self.db.scalar(stmt)

    def list_announcements(
        self,
        *,
        course_id: int | None = None,
        teacher_id: int | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Announcement], int]:
        stmt = select(Announcement).options(
            joinedload(Announcement.course),
            joinedload(Announcement.teacher),
        )
        if course_id:
            stmt = stmt.where(Announcement.course_id == course_id)
        if teacher_id:
            stmt = stmt.where(Announcement.teacher_id == teacher_id)

        total = self.db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
        items = list(
            self.db.scalars(
                stmt.order_by(Announcement.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            .unique()
            .all()
        )
        return items, total

    def create_announcement(self, announcement: Announcement) -> Announcement:
        self.db.add(announcement)
        self.db.flush()
        self.db.refresh(announcement)
        return announcement

    def delete_announcement(self, announcement: Announcement) -> None:
        self.db.delete(announcement)
        self.db.flush()

    def get_meeting(self, meeting_id: int) -> Meeting | None:
        stmt = (
            select(Meeting)
            .options(
                joinedload(Meeting.enrollment).joinedload(Enrollment.student),
                joinedload(Meeting.enrollment).joinedload(Enrollment.course),
                joinedload(Meeting.teacher),
            )
            .where(Meeting.id == meeting_id)
        )
        return self.db.scalar(stmt)

    def list_meetings(
        self,
        *,
        enrollment_id: int | None = None,
        teacher_id: int | None = None,
        student_id: int | None = None,
        upcoming_only: bool = False,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Meeting], int]:
        stmt = (
            select(Meeting)
            .join(Enrollment, Meeting.enrollment_id == Enrollment.id)
            .options(
                joinedload(Meeting.enrollment).joinedload(Enrollment.student),
                joinedload(Meeting.enrollment).joinedload(Enrollment.course),
                joinedload(Meeting.teacher),
            )
        )
        if enrollment_id:
            stmt = stmt.where(Meeting.enrollment_id == enrollment_id)
        if teacher_id:
            stmt = stmt.where(Meeting.teacher_id == teacher_id)
        if student_id:
            stmt = stmt.where(Enrollment.student_id == student_id)
        if upcoming_only:
            stmt = stmt.where(Meeting.scheduled_at >= datetime.utcnow())

        total = self.db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
        items = list(
            self.db.scalars(
                stmt.order_by(Meeting.scheduled_at.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            .unique()
            .all()
        )
        return items, total

    def create_meeting(self, meeting: Meeting) -> Meeting:
        self.db.add(meeting)
        self.db.flush()
        self.db.refresh(meeting)
        return meeting

    def delete_meeting(self, meeting: Meeting) -> None:
        self.db.delete(meeting)
        self.db.flush()

