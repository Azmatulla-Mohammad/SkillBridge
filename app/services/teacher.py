from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.storage import StorageError, SupabaseStorageService
from app.core.utils import utcnow
from app.models import Announcement, Assignment, Enrollment, Material, Meeting, TeacherProfile, User
from app.repositories.academic import AcademicRepository
from app.repositories.users import UserRepository
from app.schemas.teacher import (
    AnnouncementCreate,
    MeetingCreate,
    SubmissionReview,
    TeacherAssignmentCreate,
    TeacherAssignmentUpdate,
    TeacherMaterialCreate,
    TeacherProfileUpdate,
)
from app.services.common import record_activity, sync_enrollment_progress


class TeacherService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.academic_repo = AcademicRepository(db)
        self.storage = SupabaseStorageService()

    def _teacher_course_ids(self, teacher_id: int) -> set[int]:
        stmt = select(Enrollment.course_id).where(Enrollment.teacher_id == teacher_id)
        return {course_id for course_id in self.db.scalars(stmt).all()}

    def _validate_course_access(self, teacher_id: int, course_id: int) -> None:
        if course_id not in self._teacher_course_ids(teacher_id):
            raise PermissionError(
                "You can only manage materials and assignments for courses assigned to your students."
            )

    def dashboard(self, teacher_id: int) -> dict:
        enrollments, _ = self.academic_repo.list_enrollments(teacher_id=teacher_id, page=1, page_size=200)
        for enrollment in enrollments:
            sync_enrollment_progress(self.db, enrollment)

        student_count = len({enrollment.student_id for enrollment in enrollments})
        assignment_count = self.db.scalar(
            select(func.count(Assignment.id)).where(Assignment.teacher_id == teacher_id)
        ) or 0
        material_count = self.db.scalar(
            select(func.count(Material.id)).where(Material.teacher_id == teacher_id)
        ) or 0
        recent_submissions, _ = self.academic_repo.list_submissions(teacher_id=teacher_id, page_size=5, page=1)
        upcoming_meetings, _ = self.academic_repo.list_meetings(
            teacher_id=teacher_id,
            upcoming_only=True,
            page=1,
            page_size=5,
        )
        self.db.commit()
        return {
            "student_count": student_count,
            "assignment_count": assignment_count,
            "material_count": material_count,
            "enrollments": enrollments,
            "recent_submissions": recent_submissions,
            "upcoming_meetings": upcoming_meetings,
        }

    def list_students(self, teacher_id: int, *, search: str | None, page: int, page_size: int):
        enrollments, total = self.academic_repo.list_enrollments(
            teacher_id=teacher_id,
            search=search,
            page=page,
            page_size=page_size,
        )
        for enrollment in enrollments:
            sync_enrollment_progress(self.db, enrollment)
        self.db.commit()
        return enrollments, total

    async def create_material(
        self,
        teacher_id: int,
        data: TeacherMaterialCreate,
        upload,
    ) -> Material:
        self._validate_course_access(teacher_id, data.course_id)
        result = await self.storage.upload_file(upload, folder="materials", owner_id=teacher_id)
        material = self.academic_repo.create_material(
            Material(
                title=data.title.strip(),
                description=(data.description or "").strip() or None,
                course_id=data.course_id,
                teacher_id=teacher_id,
                file_url=result.file_url,
                original_filename=result.original_filename,
                content_type=result.content_type,
            )
        )
        record_activity(
            self.db,
            actor_user_id=teacher_id,
            action="teacher.material.created",
            entity_type="material",
            entity_id=material.id,
            summary=f"Uploaded material {material.title}.",
        )
        self.db.commit()
        return self.academic_repo.get_material(material.id) or material

    def list_materials(self, teacher_id: int, *, page: int, page_size: int):
        return self.academic_repo.list_materials(teacher_id=teacher_id, page=page, page_size=page_size)

    async def delete_material(self, teacher_id: int, material_id: int) -> None:
        material = self.academic_repo.get_material(material_id)
        if not material or material.teacher_id != teacher_id:
            raise LookupError("Material not found.")
        await self.storage.delete_file(material.file_url)
        title = material.title
        self.academic_repo.delete_material(material)
        record_activity(
            self.db,
            actor_user_id=teacher_id,
            action="teacher.material.deleted",
            entity_type="material",
            entity_id=material_id,
            summary=f"Deleted material {title}.",
        )
        self.db.commit()

    async def create_assignment(
        self,
        teacher_id: int,
        data: TeacherAssignmentCreate,
        upload=None,
    ) -> Assignment:
        self._validate_course_access(teacher_id, data.course_id)
        attachment_url = None
        if upload and getattr(upload, "filename", None):
            result = await self.storage.upload_file(upload, folder="assignments", owner_id=teacher_id)
            attachment_url = result.file_url

        assignment = self.academic_repo.create_assignment(
            Assignment(
                title=data.title.strip(),
                description=data.description.strip(),
                course_id=data.course_id,
                teacher_id=teacher_id,
                due_at=data.due_at,
                max_score=data.max_score,
                attachment_url=attachment_url,
            )
        )
        record_activity(
            self.db,
            actor_user_id=teacher_id,
            action="teacher.assignment.created",
            entity_type="assignment",
            entity_id=assignment.id,
            summary=f"Created assignment {assignment.title}.",
        )
        self.db.commit()
        return self.academic_repo.get_assignment(assignment.id) or assignment

    def list_assignments(
        self,
        teacher_id: int,
        *,
        search: str | None,
        page: int,
        page_size: int,
    ):
        return self.academic_repo.list_assignments(
            teacher_id=teacher_id,
            search=search,
            page=page,
            page_size=page_size,
        )

    async def update_assignment(
        self,
        teacher_id: int,
        assignment_id: int,
        data: TeacherAssignmentUpdate,
        upload=None,
    ) -> Assignment:
        assignment = self.academic_repo.get_assignment(assignment_id)
        if not assignment or assignment.teacher_id != teacher_id:
            raise LookupError("Assignment not found.")

        if data.title is not None:
            assignment.title = data.title.strip()
        if data.description is not None:
            assignment.description = data.description.strip()
        if data.due_at is not None:
            assignment.due_at = data.due_at
        if data.max_score is not None:
            assignment.max_score = data.max_score
        if upload and getattr(upload, "filename", None):
            if assignment.attachment_url:
                await self.storage.delete_file(assignment.attachment_url)
            result = await self.storage.upload_file(upload, folder="assignments", owner_id=teacher_id)
            assignment.attachment_url = result.file_url
        elif data.attachment_url is not None:
            assignment.attachment_url = data.attachment_url

        record_activity(
            self.db,
            actor_user_id=teacher_id,
            action="teacher.assignment.updated",
            entity_type="assignment",
            entity_id=assignment.id,
            summary=f"Updated assignment {assignment.title}.",
        )
        self.db.commit()
        return self.academic_repo.get_assignment(assignment.id) or assignment

    async def delete_assignment(self, teacher_id: int, assignment_id: int) -> None:
        assignment = self.academic_repo.get_assignment(assignment_id)
        if not assignment or assignment.teacher_id != teacher_id:
            raise LookupError("Assignment not found.")
        if assignment.attachment_url:
            await self.storage.delete_file(assignment.attachment_url)
        title = assignment.title
        self.academic_repo.delete_assignment(assignment)
        record_activity(
            self.db,
            actor_user_id=teacher_id,
            action="teacher.assignment.deleted",
            entity_type="assignment",
            entity_id=assignment_id,
            summary=f"Deleted assignment {title}.",
        )
        self.db.commit()

    def list_submissions(self, teacher_id: int, *, page: int, page_size: int):
        return self.academic_repo.list_submissions(teacher_id=teacher_id, page=page, page_size=page_size)

    def review_submission(self, teacher_id: int, submission_id: int, data: SubmissionReview):
        submission = self.academic_repo.get_submission(submission_id)
        if not submission or submission.assignment.teacher_id != teacher_id:
            raise LookupError("Submission not found.")

        submission.score = data.score
        submission.feedback = data.feedback.strip()
        submission.reviewed_at = utcnow()
        enrollment = self.academic_repo.find_enrollment(
            student_id=submission.student_id,
            course_id=submission.assignment.course_id,
        )
        if enrollment:
            sync_enrollment_progress(self.db, enrollment)

        record_activity(
            self.db,
            actor_user_id=teacher_id,
            action="teacher.submission.reviewed",
            entity_type="submission",
            entity_id=submission.id,
            summary=f"Reviewed submission #{submission.id} for {submission.student.full_name}.",
        )
        self.db.commit()
        return self.academic_repo.get_submission(submission.id) or submission

    def create_announcement(self, teacher_id: int, data: AnnouncementCreate) -> Announcement:
        self._validate_course_access(teacher_id, data.course_id)
        announcement = self.academic_repo.create_announcement(
            Announcement(
                course_id=data.course_id,
                teacher_id=teacher_id,
                title=data.title.strip(),
                content=data.content.strip(),
            )
        )
        record_activity(
            self.db,
            actor_user_id=teacher_id,
            action="teacher.announcement.created",
            entity_type="announcement",
            entity_id=announcement.id,
            summary=f"Posted announcement {announcement.title}.",
        )
        self.db.commit()
        return self.academic_repo.get_announcement(announcement.id) or announcement

    def list_announcements(self, teacher_id: int, *, page: int, page_size: int):
        return self.academic_repo.list_announcements(teacher_id=teacher_id, page=page, page_size=page_size)

    def delete_announcement(self, teacher_id: int, announcement_id: int) -> None:
        announcement = self.academic_repo.get_announcement(announcement_id)
        if not announcement or announcement.teacher_id != teacher_id:
            raise LookupError("Announcement not found.")
        title = announcement.title
        self.academic_repo.delete_announcement(announcement)
        record_activity(
            self.db,
            actor_user_id=teacher_id,
            action="teacher.announcement.deleted",
            entity_type="announcement",
            entity_id=announcement_id,
            summary=f"Deleted announcement {title}.",
        )
        self.db.commit()

    def create_meeting(self, teacher_id: int, data: MeetingCreate) -> Meeting:
        enrollment = self.academic_repo.get_enrollment(data.enrollment_id)
        if not enrollment or enrollment.teacher_id != teacher_id:
            raise LookupError("Enrollment not found.")

        enrollment.meeting_link = data.meeting_url
        meeting = self.academic_repo.create_meeting(
            Meeting(
                enrollment_id=enrollment.id,
                teacher_id=teacher_id,
                title=data.title.strip(),
                meeting_url=data.meeting_url.strip(),
                scheduled_at=data.scheduled_at,
                notes=(data.notes or "").strip() or None,
            )
        )
        record_activity(
            self.db,
            actor_user_id=teacher_id,
            action="teacher.meeting.created",
            entity_type="meeting",
            entity_id=meeting.id,
            summary=f"Scheduled meeting {meeting.title}.",
        )
        self.db.commit()
        return self.academic_repo.get_meeting(meeting.id) or meeting

    def list_meetings(self, teacher_id: int, *, page: int, page_size: int):
        return self.academic_repo.list_meetings(teacher_id=teacher_id, page=page, page_size=page_size)

    def delete_meeting(self, teacher_id: int, meeting_id: int) -> None:
        meeting = self.academic_repo.get_meeting(meeting_id)
        if not meeting or meeting.teacher_id != teacher_id:
            raise LookupError("Meeting not found.")
        title = meeting.title
        self.academic_repo.delete_meeting(meeting)
        record_activity(
            self.db,
            actor_user_id=teacher_id,
            action="teacher.meeting.deleted",
            entity_type="meeting",
            entity_id=meeting_id,
            summary=f"Deleted meeting {title}.",
        )
        self.db.commit()

    def update_profile(self, teacher_id: int, data: TeacherProfileUpdate) -> User:
        user = self.user_repo.get(teacher_id)
        if not user:
            raise LookupError("User not found.")

        if data.full_name is not None:
            user.full_name = data.full_name.strip()
        if data.phone is not None:
            user.phone = data.phone.strip() or None
        if data.bio is not None:
            user.bio = data.bio.strip() or None
        profile = user.teacher_profile or TeacherProfile(user_id=user.id)
        if not user.teacher_profile:
            self.db.add(profile)
        if data.headline is not None:
            profile.headline = data.headline.strip() or None
        if data.expertise is not None:
            profile.expertise = data.expertise.strip() or None
        if data.meeting_link is not None:
            profile.meeting_link = data.meeting_link.strip() or None

        record_activity(
            self.db,
            actor_user_id=teacher_id,
            action="teacher.profile.updated",
            entity_type="user",
            entity_id=user.id,
            summary=f"Updated teacher profile for {user.full_name}.",
        )
        self.db.commit()
        return self.user_repo.get(user.id) or user

    def course_options(self, teacher_id: int):
        course_ids = self._teacher_course_ids(teacher_id)
        return [self.academic_repo.get_course(course_id) for course_id in sorted(course_ids) if course_id]


