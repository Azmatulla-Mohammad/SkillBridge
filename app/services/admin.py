from __future__ import annotations

import logging

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password

from app.core.utils import slugify
from app.models import (
    Assignment,
    Course,
    Enrollment,
    Material,
    Meeting,
    StudentProfile,
    TeacherProfile,
    User,
    UserRole,
)
from app.repositories.academic import AcademicRepository
from app.repositories.public import PublicRepository
from app.repositories.users import UserRepository
from app.schemas.admin import (
    AssignmentAdminCreate,
    AssignmentAdminUpdate,
    CourseCreate,
    CourseUpdate,
    EnrollmentCreate,
    EnrollmentUpdate,
    UserCreate,
    UserUpdate,
)
from app.services.common import record_activity, sync_enrollment_progress


settings = get_settings()
logger = logging.getLogger(__name__)


class AdminService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.academic_repo = AcademicRepository(db)
        self.public_repo = PublicRepository(db)

    def bootstrap_defaults(self) -> None:
        course = self.academic_repo.get_course_by_slug(settings.default_course_slug)
        if not course:
            self.academic_repo.create_course(
                Course(
                    title=settings.default_course_title,
                    slug=settings.default_course_slug,
                    description=settings.default_course_description,
                    duration_weeks=settings.default_course_duration_weeks,
                    price=settings.default_course_price,
                    is_active=True,
                )
            )

        existing_admin = self.db.scalar(
            select(User).where(User.role == UserRole.ADMIN).order_by(User.id.asc())
        )

        # Idempotent bootstrap:
        # - If an admin already exists: never change password/email.
        if existing_admin:
            logger.info("Default Admin already exists. Skipping bootstrap.")
            self.db.commit()
            return

        # Create default admin exactly once when missing.
        if not settings.default_admin_email or not settings.default_admin_password:
            raise RuntimeError(
                "Admin bootstrap required but environment variables DEFAULT_ADMIN_EMAIL and DEFAULT_ADMIN_PASSWORD are not set."
            )

        admin = User(
            full_name=settings.admin_bootstrap_name,
            email=settings.default_admin_email.lower().strip(),
            password_hash=hash_password(settings.default_admin_password),
            role=UserRole.ADMIN,
            is_active=True,
        )
        self.user_repo.create(admin)

        self.db.commit()


    def dashboard(self) -> dict:
        total_students = self.db.scalar(
            select(func.count(User.id)).where(User.role == UserRole.STUDENT)
        ) or 0
        total_teachers = self.db.scalar(
            select(func.count(User.id)).where(User.role == UserRole.TEACHER)
        ) or 0
        total_courses = self.db.scalar(select(func.count(Course.id))) or 0
        total_assignments = self.db.scalar(select(func.count(Assignment.id))) or 0
        total_materials = self.db.scalar(select(func.count(Material.id))) or 0
        total_meetings = self.db.scalar(select(func.count(Meeting.id))) or 0
        recent_activity = self.public_repo.recent_activity(limit=8)
        upcoming_meetings, _ = self.academic_repo.list_meetings(upcoming_only=True, page_size=5)
        return {
            "stats": {
                "students": total_students,
                "teachers": total_teachers,
                "courses": total_courses,
                "assignments": total_assignments,
                "materials": total_materials,
                "meetings": total_meetings,
            },
            "recent_activity": recent_activity,
            "upcoming_meetings": upcoming_meetings,
        }

    def list_users(
        self,
        *,
        role: UserRole | None,
        search: str | None,
        is_active: bool | None,
        page: int,
        page_size: int,
    ) -> tuple[list[User], int]:
        return self.user_repo.list_users(
            role=role,
            search=search,
            is_active=is_active,
            page=page,
            page_size=page_size,
        )

    def create_user(self, data: UserCreate, actor_id: int) -> tuple[User, str | None]:
        email = data.email.lower().strip()
        if self.user_repo.get_by_email(email):
            raise ValueError("A user with this email already exists.")

        # New requirement: Admin must provide a password.
        if not data.password:
            raise ValueError("Password is required.")

        user = User(
            full_name=data.full_name.strip(),
            email=email,
            password_hash=hash_password(data.password),

            role=data.role,
            phone=data.phone,
            bio=data.bio,
            is_active=True,
            temporary_password_required=False,
            password_changed_at=None,
        )
        self.user_repo.create(user)

        if data.role == UserRole.TEACHER:
            self.user_repo.create_teacher_profile(
                TeacherProfile(
                    user_id=user.id,
                    headline=data.headline,
                    expertise=data.expertise,
                )
            )
        elif data.role == UserRole.STUDENT:
            self.user_repo.create_student_profile(
                StudentProfile(
                    user_id=user.id,
                    guardian_name=data.guardian_name,
                    learning_goals=data.learning_goals,
                )
            )

        record_activity(
            self.db,
            actor_user_id=actor_id,
            action="admin.user.created",
            entity_type="user",
            entity_id=user.id,
            summary=f"Created {data.role.value} account for {user.full_name}.",
            metadata={"role": data.role.value, "email": user.email},
        )
        self.db.commit()
        return self.user_repo.get(user.id) or user, generated_temporary_password

    def update_user(self, user_id: int, data: UserUpdate, actor_id: int) -> User:
        user = self.user_repo.get(user_id)
        if not user:
            raise LookupError("User not found.")

        if data.email and data.email.lower().strip() != user.email:
            existing = self.user_repo.get_by_email(data.email)
            if existing and existing.id != user.id:
                raise ValueError("Another user already uses this email address.")
            user.email = data.email.lower().strip()

        if data.full_name is not None:
            user.full_name = data.full_name.strip()
        if data.phone is not None:
            user.phone = data.phone.strip() or None
        if data.bio is not None:
            user.bio = data.bio.strip() or None
        if data.password:
            user.password_hash = hash_password(data.password)
        if data.is_active is not None:
            user.is_active = data.is_active

        # Role changes are not allowed in update.
        if getattr(data, "role", None) is not None and getattr(data, "role") != user.role:
            raise ValueError("Role modification is not allowed.")

        if user.role == UserRole.TEACHER:
            profile = user.teacher_profile or TeacherProfile(user_id=user.id)
            if not user.teacher_profile:
                self.user_repo.create_teacher_profile(profile)
            profile.headline = data.headline
            profile.expertise = data.expertise
        elif user.role == UserRole.STUDENT:
            profile = user.student_profile or StudentProfile(user_id=user.id)
            if not user.student_profile:
                self.user_repo.create_student_profile(profile)
            profile.guardian_name = data.guardian_name
            profile.learning_goals = data.learning_goals

        record_activity(
            self.db,
            actor_user_id=actor_id,
            action="admin.user.updated",
            entity_type="user",
            entity_id=user.id,
            summary=f"Updated {user.full_name}.",
            metadata={"role": user.role.value},
        )
        self.db.commit()
        return self.user_repo.get(user.id) or user

    def set_user_active_state(self, user_id: int, is_active: bool, actor_id: int) -> User:
        user = self.user_repo.get(user_id)
        if not user:
            raise LookupError("User not found.")

        user.is_active = is_active
        record_activity(
            self.db,
            actor_user_id=actor_id,
            action="admin.user.activated" if is_active else "admin.user.deactivated",
            entity_type="user",
            entity_id=user.id,
            summary=f"{'Activated' if is_active else 'Deactivated'} {user.full_name}.",
        )
        self.db.commit()
        return user

    def reset_password(self, user_id: int, actor_id: int) -> str:
        user = self.user_repo.get(user_id)
        if not user:
            raise LookupError("User not found.")

        temporary_password = generate_random_password()
        user.password_hash = hash_password(temporary_password)
        user.temporary_password_required = True
        user.password_changed_at = None

        record_activity(
            self.db,
            actor_user_id=actor_id,
            action="admin.user.password_reset",
            entity_type="user",
            entity_id=user.id,
            summary=f"Reset password for {user.full_name}.",
        )
        self.db.commit()
        return temporary_password

    def delete_user(self, user_id: int, actor_id: int) -> None:
        user = self.user_repo.get(user_id)
        if not user:
            raise LookupError("User not found.")

        # Safe delete: block permanent deletion if any related academic records exist.
        # Do not cascade-delete academic data.
        related_items: list[str] = []

        if user.teacher_enrollments or user.student_enrollments:
            related_items.append("enrollments")

        if user.teaching_materials:
            related_items.append("teaching materials")

        if user.teaching_assignments:
            related_items.append("assignments")

        # Feedback/submissions are linked through submissions, not directly on User.
        from app.models import Announcement, Submission  # local import to avoid circulars


        submissions_count = 0
        meetings_count = 0
        announcements_count = 0

        if user.role == UserRole.STUDENT:
            submissions_count = self.db.scalar(
                select(func.count(Submission.id)).where(Submission.student_id == user.id)
            ) or 0
        else:
            # Teacher/admin won't have direct submissions in the model, but still safe to check.
            submissions_count = self.db.scalar(
                select(func.count(Submission.id)).where(Submission.student_id == user.id)
            ) or 0

        # Meetings and announcements are related to enrollments/courses.
        meetings_count = self.db.scalar(
            select(func.count(Meeting.id)).where(Meeting.teacher_id == user.id)
        ) or 0
        announcements_count = self.db.scalar(
            select(func.count(Announcement.id)).where(Announcement.teacher_id == user.id)
        ) or 0

        if submissions_count:
            related_items.append("feedback / submissions")
        if meetings_count:
            related_items.append("meetings")
        if announcements_count:
            related_items.append("announcements")

        if related_items:
            related_str = ", ".join(related_items)
            raise ValueError(
                "Permanent deletion is blocked because this account has related academic records ("
                f"{related_str}).\n"
                "Recommended action: deactivate the account instead."
            )

        summary = f"Deleted {user.role.value} account for {user.full_name}."
        self.user_repo.delete(user)
        record_activity(
            self.db,
            actor_user_id=actor_id,
            action="admin.user.deleted",
            entity_type="user",
            entity_id=user_id,
            summary=summary,
        )
        self.db.commit()


    def list_courses(
        self, *, search: str | None, is_active: bool | None, page: int, page_size: int
    ) -> tuple[list[Course], int]:
        return self.academic_repo.list_courses(
            search=search,
            is_active=is_active,
            page=page,
            page_size=page_size,
        )

    def create_course(self, data: CourseCreate, actor_id: int) -> Course:
        slug = slugify(data.slug or data.title)
        if self.academic_repo.get_course_by_slug(slug):
            raise ValueError("A course with this slug already exists.")

        course = self.academic_repo.create_course(
            Course(
                title=data.title.strip(),
                slug=slug,
                description=data.description.strip(),
                duration_weeks=data.duration_weeks,
                price=data.price,
                is_active=data.is_active,
            )
        )
        record_activity(
            self.db,
            actor_user_id=actor_id,
            action="admin.course.created",
            entity_type="course",
            entity_id=course.id,
            summary=f"Created course {course.title}.",
        )
        self.db.commit()
        return course

    def update_course(self, course_id: int, data: CourseUpdate, actor_id: int) -> Course:
        course = self.academic_repo.get_course(course_id)
        if not course:
            raise LookupError("Course not found.")

        if data.title is not None:
            course.title = data.title.strip()
        if data.slug is not None:
            slug = slugify(data.slug)
            existing = self.academic_repo.get_course_by_slug(slug)
            if existing and existing.id != course.id:
                raise ValueError("Another course already uses this slug.")
            course.slug = slug
        if data.description is not None:
            course.description = data.description.strip()
        if data.duration_weeks is not None:
            course.duration_weeks = data.duration_weeks
        if data.price is not None:
            course.price = data.price
        if data.is_active is not None:
            course.is_active = data.is_active

        record_activity(
            self.db,
            actor_user_id=actor_id,
            action="admin.course.updated",
            entity_type="course",
            entity_id=course.id,
            summary=f"Updated course {course.title}.",
        )
        self.db.commit()
        return course

    def delete_course(self, course_id: int, actor_id: int) -> None:
        course = self.academic_repo.get_course(course_id)
        if not course:
            raise LookupError("Course not found.")
        if course.enrollments or course.materials or course.assignments:
            raise ValueError("This course has live records and cannot be deleted.")

        title = course.title
        self.academic_repo.delete_course(course)
        record_activity(
            self.db,
            actor_user_id=actor_id,
            action="admin.course.deleted",
            entity_type="course",
            entity_id=course_id,
            summary=f"Deleted course {title}.",
        )
        self.db.commit()

    def list_enrollments(
        self,
        *,
        search: str | None,
        teacher_id: int | None,
        student_id: int | None,
        course_id: int | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Enrollment], int]:
        enrollments, total = self.academic_repo.list_enrollments(
            search=search,
            teacher_id=teacher_id,
            student_id=student_id,
            course_id=course_id,
            page=page,
            page_size=page_size,
        )
        for enrollment in enrollments:
            sync_enrollment_progress(self.db, enrollment)
        self.db.commit()
        return enrollments, total

    def create_enrollment(self, data: EnrollmentCreate, actor_id: int) -> Enrollment:
        student = self.user_repo.get(data.student_id)
        teacher = self.user_repo.get(data.teacher_id)
        course = self.academic_repo.get_course(data.course_id)

        if not student or student.role != UserRole.STUDENT:
            raise ValueError("Selected student account is invalid.")
        if not student.is_active:
            raise ValueError("Selected student account is inactive. Activate the student before assignment.")

        if not teacher or teacher.role != UserRole.TEACHER:
            raise ValueError("Selected teacher account is invalid.")
        if not teacher.is_active:
            raise ValueError("Selected teacher account is inactive. Activate the teacher before assignment.")

        if not course or not course.is_active:
            raise ValueError("Selected course does not exist or is inactive.")

        existing = self.academic_repo.find_enrollment(student.id, course.id)
        if existing:
            # Duplicate-prevention + teacher reassignment support:
            # keep the unique (student_id, course_id) mapping, but update teacher.
            existing.teacher_id = teacher.id
            existing.status = data.status
            existing.start_date = data.start_date
            existing.meeting_link = data.meeting_link
            existing.notes = data.notes
            sync_enrollment_progress(self.db, existing)
            record_activity(
                self.db,
                actor_user_id=actor_id,
                action="admin.enrollment.updated",
                entity_type="enrollment",
                entity_id=existing.id,
                summary=(
                    f"Updated assignment for {student.full_name}: "
                    f"teacher={teacher.full_name}, course={course.title}."
                ),
            )
            self.db.commit()
            return self.academic_repo.get_enrollment(existing.id) or existing

        enrollment = self.academic_repo.create_enrollment(
            Enrollment(
                student_id=student.id,
                teacher_id=teacher.id,
                course_id=course.id,
                status=data.status,
                start_date=data.start_date,
                meeting_link=data.meeting_link,
                notes=data.notes,
            )
        )
        sync_enrollment_progress(self.db, enrollment)
        record_activity(
            self.db,
            actor_user_id=actor_id,
            action="admin.enrollment.created",
            entity_type="enrollment",
            entity_id=enrollment.id,
            summary=f"Assigned {student.full_name} to {teacher.full_name} for {course.title}.",
        )
        self.db.commit()
        return self.academic_repo.get_enrollment(enrollment.id) or enrollment


    def update_enrollment(self, enrollment_id: int, data: EnrollmentUpdate, actor_id: int) -> Enrollment:
        enrollment = self.academic_repo.get_enrollment(enrollment_id)
        if not enrollment:
            raise LookupError("Enrollment not found.")

        if data.teacher_id is not None:
            teacher = self.user_repo.get(data.teacher_id)
            if not teacher or teacher.role != UserRole.TEACHER:
                raise ValueError("Selected teacher account is invalid.")
            enrollment.teacher_id = teacher.id
        if data.course_id is not None:
            course = self.academic_repo.get_course(data.course_id)
            if not course:
                raise ValueError("Selected course does not exist.")
            enrollment.course_id = course.id
        if data.status is not None:
            enrollment.status = data.status
        if data.start_date is not None:
            enrollment.start_date = data.start_date
        if data.meeting_link is not None:
            enrollment.meeting_link = data.meeting_link.strip() or None
        if data.notes is not None:
            enrollment.notes = data.notes.strip() or None
        if data.progress_percent is not None:
            enrollment.progress_percent = data.progress_percent
        else:
            sync_enrollment_progress(self.db, enrollment)

        record_activity(
            self.db,
            actor_user_id=actor_id,
            action="admin.enrollment.updated",
            entity_type="enrollment",
            entity_id=enrollment.id,
            summary=f"Updated enrollment #{enrollment.id}.",
        )
        self.db.commit()
        return self.academic_repo.get_enrollment(enrollment.id) or enrollment

    def delete_enrollment(self, enrollment_id: int, actor_id: int) -> None:
        enrollment = self.academic_repo.get_enrollment(enrollment_id)
        if not enrollment:
            raise LookupError("Enrollment not found.")

        self.academic_repo.delete_enrollment(enrollment)
        record_activity(
            self.db,
            actor_user_id=actor_id,
            action="admin.enrollment.deleted",
            entity_type="enrollment",
            entity_id=enrollment_id,
            summary=f"Removed enrollment #{enrollment_id}.",
        )
        self.db.commit()

    def list_assignments(
        self,
        *,
        search: str | None,
        course_id: int | None,
        teacher_id: int | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Assignment], int]:
        return self.academic_repo.list_assignments(
            search=search,
            course_id=course_id,
            teacher_id=teacher_id,
            page=page,
            page_size=page_size,
        )

    def create_assignment(
        self,
        data: AssignmentAdminCreate,
        actor_id: int,
        *,
        attachment_url: str | None = None,
    ) -> Assignment:
        course = self.academic_repo.get_course(data.course_id)
        teacher = self.user_repo.get(data.teacher_id)
        if not course:
            raise ValueError("Selected course does not exist.")
        if not teacher or teacher.role != UserRole.TEACHER:
            raise ValueError("Selected teacher account is invalid.")

        assignment = self.academic_repo.create_assignment(
            Assignment(
                title=data.title.strip(),
                description=data.description.strip(),
                course_id=course.id,
                teacher_id=teacher.id,
                due_at=data.due_at,
                max_score=data.max_score,
                attachment_url=attachment_url or data.attachment_url,
            )
        )
        record_activity(
            self.db,
            actor_user_id=actor_id,
            action="admin.assignment.created",
            entity_type="assignment",
            entity_id=assignment.id,
            summary=f"Created assignment {assignment.title}.",
        )
        self.db.commit()
        return self.academic_repo.get_assignment(assignment.id) or assignment

    def update_assignment(
        self,
        assignment_id: int,
        data: AssignmentAdminUpdate,
        actor_id: int,
    ) -> Assignment:
        assignment = self.academic_repo.get_assignment(assignment_id)
        if not assignment:
            raise LookupError("Assignment not found.")

        if data.title is not None:
            assignment.title = data.title.strip()
        if data.description is not None:
            assignment.description = data.description.strip()
        if data.course_id is not None:
            course = self.academic_repo.get_course(data.course_id)
            if not course:
                raise ValueError("Selected course does not exist.")
            assignment.course_id = course.id
        if data.teacher_id is not None:
            teacher = self.user_repo.get(data.teacher_id)
            if not teacher or teacher.role != UserRole.TEACHER:
                raise ValueError("Selected teacher account is invalid.")
            assignment.teacher_id = teacher.id
        if data.due_at is not None:
            assignment.due_at = data.due_at
        if data.max_score is not None:
            assignment.max_score = data.max_score
        if data.attachment_url is not None:
            assignment.attachment_url = data.attachment_url

        record_activity(
            self.db,
            actor_user_id=actor_id,
            action="admin.assignment.updated",
            entity_type="assignment",
            entity_id=assignment.id,
            summary=f"Updated assignment {assignment.title}.",
        )
        self.db.commit()
        return self.academic_repo.get_assignment(assignment.id) or assignment

    def delete_assignment(self, assignment_id: int, actor_id: int) -> None:
        assignment = self.academic_repo.get_assignment(assignment_id)
        if not assignment:
            raise LookupError("Assignment not found.")
        title = assignment.title
        self.academic_repo.delete_assignment(assignment)
        record_activity(
            self.db,
            actor_user_id=actor_id,
            action="admin.assignment.deleted",
            entity_type="assignment",
            entity_id=assignment_id,
            summary=f"Deleted assignment {title}.",
        )
        self.db.commit()

    def list_logs(self, *, search: str | None, page: int, page_size: int):
        return self.public_repo.list_activity_logs(search=search, page=page, page_size=page_size)

    def teacher_options(self) -> list[User]:
        items, _ = self.user_repo.list_users(role=UserRole.TEACHER, page_size=500, page=1)
        return items

    def student_options(self) -> list[User]:
        items, _ = self.user_repo.list_users(role=UserRole.STUDENT, page_size=500, page=1)
        return items

    def course_options(self) -> list[Course]:
        items, _ = self.academic_repo.list_courses(page=1, page_size=500)
        return items


