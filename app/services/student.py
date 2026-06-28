from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.storage import SupabaseStorageService
from app.core.utils import utcnow
from app.models import Enrollment, StudentProfile, Submission, User
from app.repositories.academic import AcademicRepository
from app.repositories.users import UserRepository
from app.schemas.student import StudentProfileUpdate
from app.services.common import record_activity, sync_enrollment_progress


class StudentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.academic_repo = AcademicRepository(db)
        self.storage = SupabaseStorageService()

    def _enrollments(self, student_id: int):
        return self.academic_repo.list_enrollments(student_id=student_id, page=1, page_size=200)[0]

    def dashboard(self, student_id: int) -> dict:
        enrollments = self._enrollments(student_id)
        for enrollment in enrollments:
            sync_enrollment_progress(self.db, enrollment)
        course_ids = [enrollment.course_id for enrollment in enrollments]

        assignments = []
        materials = []
        announcements = []
        if course_ids:
            assignments, _ = self.academic_repo.list_assignments(course_id=course_ids[0], page=1, page_size=10)
            materials, _ = self.academic_repo.list_materials(course_id=course_ids[0], page=1, page_size=10)
            announcements, _ = self.academic_repo.list_announcements(course_id=course_ids[0], page=1, page_size=10)

        meetings, _ = self.academic_repo.list_meetings(student_id=student_id, upcoming_only=True, page=1, page_size=5)
        submissions, _ = self.academic_repo.list_submissions(student_id=student_id, page=1, page_size=20)
        self.db.commit()
        return {
            "enrollments": enrollments,
            "assignments": assignments,
            "materials": materials,
            "announcements": announcements,
            "meetings": meetings,
            "submissions": submissions,
        }

    def list_materials(self, student_id: int, *, page: int, page_size: int):
        enrollments = self._enrollments(student_id)
        if not enrollments:
            return [], 0
        return self.academic_repo.list_materials(
            course_id=enrollments[0].course_id,
            page=page,
            page_size=page_size,
        )

    def list_assignments(self, student_id: int, *, page: int, page_size: int):
        enrollments = self._enrollments(student_id)
        if not enrollments:
            return [], 0
        return self.academic_repo.list_assignments(
            course_id=enrollments[0].course_id,
            page=page,
            page_size=page_size,
        )

    def list_feedback(self, student_id: int, *, page: int, page_size: int):
        return self.academic_repo.list_submissions(student_id=student_id, page=page, page_size=page_size)

    def list_meetings(self, student_id: int, *, page: int, page_size: int):
        return self.academic_repo.list_meetings(student_id=student_id, page=page, page_size=page_size)

    def list_announcements(self, student_id: int, *, page: int, page_size: int):
        enrollments = self._enrollments(student_id)
        if not enrollments:
            return [], 0
        return self.academic_repo.list_announcements(
            course_id=enrollments[0].course_id,
            page=page,
            page_size=page_size,
        )

    async def submit_assignment(self, student_id: int, assignment_id: int, upload) -> Submission:
        assignment = self.academic_repo.get_assignment(assignment_id)
        if not assignment:
            raise LookupError("Assignment not found.")

        enrollment = self.academic_repo.find_enrollment(student_id=student_id, course_id=assignment.course_id)
        if not enrollment:
            raise PermissionError("You are not enrolled in this assignment's course.")

        existing = self.academic_repo.get_submission_for_assignment_student(assignment_id, student_id)
        if existing:
            await self.storage.delete_file(existing.file_url)
        result = await self.storage.upload_file(upload, folder="submissions", owner_id=student_id)

        if existing:
            existing.file_url = result.file_url
            existing.original_filename = result.original_filename
            existing.content_type = result.content_type
            existing.submitted_at = utcnow()
            existing.feedback = None
            existing.score = None
            existing.reviewed_at = None
            submission = existing
        else:
            submission = self.academic_repo.create_submission(
                Submission(
                    assignment_id=assignment_id,
                    student_id=student_id,
                    file_url=result.file_url,
                    original_filename=result.original_filename,
                    content_type=result.content_type,
                    submitted_at=utcnow(),
                )
            )

        sync_enrollment_progress(self.db, enrollment)
        record_activity(
            self.db,
            actor_user_id=student_id,
            action="student.assignment.submitted",
            entity_type="submission",
            entity_id=submission.id,
            summary=f"Submitted assignment {assignment.title}.",
        )
        self.db.commit()
        return self.academic_repo.get_submission(submission.id) or submission

    def update_profile(self, student_id: int, data: StudentProfileUpdate) -> User:
        user = self.user_repo.get(student_id)
        if not user:
            raise LookupError("User not found.")

        if data.full_name is not None:
            user.full_name = data.full_name.strip()
        if data.phone is not None:
            user.phone = data.phone.strip() or None
        if data.bio is not None:
            user.bio = data.bio.strip() or None

        profile = user.student_profile or StudentProfile(user_id=user.id)
        if not user.student_profile:
            self.db.add(profile)
        if data.guardian_name is not None:
            profile.guardian_name = data.guardian_name.strip() or None
        if data.learning_goals is not None:
            profile.learning_goals = data.learning_goals.strip() or None

        record_activity(
            self.db,
            actor_user_id=student_id,
            action="student.profile.updated",
            entity_type="user",
            entity_id=user.id,
            summary=f"Updated student profile for {user.full_name}.",
        )
        self.db.commit()
        return self.user_repo.get(user.id) or user


