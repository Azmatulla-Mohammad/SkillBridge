from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class EnrollmentStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class InquiryType(str, Enum):
    CONTACT = "contact"
    DEMO = "demo"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role", values_callable=lambda enum: [e.value for e in enum]),
        index=True,
    )
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # If True, user must change password after successful login.
    temporary_password_required: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="0", nullable=False
    )
    password_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    teacher_profile: Mapped[TeacherProfile | None] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    student_profile: Mapped[StudentProfile | None] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    teacher_enrollments: Mapped[list[Enrollment]] = relationship(
        back_populates="teacher",
        foreign_keys="Enrollment.teacher_id",
    )
    student_enrollments: Mapped[list[Enrollment]] = relationship(
        back_populates="student",
        foreign_keys="Enrollment.student_id",
    )
    teaching_materials: Mapped[list[Material]] = relationship(back_populates="teacher")
    teaching_assignments: Mapped[list[Assignment]] = relationship(back_populates="teacher")
    created_announcements: Mapped[list[Announcement]] = relationship(back_populates="teacher")
    hosted_meetings: Mapped[list[Meeting]] = relationship(back_populates="teacher")
    activity_logs: Mapped[list[ActivityLog]] = relationship(back_populates="actor")


class TeacherProfile(TimestampMixin, Base):
    __tablename__ = "teacher_profiles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    headline: Mapped[str | None] = mapped_column(String(160), nullable=True)
    expertise: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meeting_link: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user: Mapped[User] = relationship(back_populates="teacher_profile")


class StudentProfile(TimestampMixin, Base):
    __tablename__ = "student_profiles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    guardian_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    learning_goals: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped[User] = relationship(back_populates="student_profile")


class Course(TimestampMixin, Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text)
    duration_weeks: Mapped[int] = mapped_column(Integer, default=12, server_default="12")
    price: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")

    enrollments: Mapped[list[Enrollment]] = relationship(back_populates="course")
    materials: Mapped[list[Material]] = relationship(back_populates="course")
    assignments: Mapped[list[Assignment]] = relationship(back_populates="course")
    announcements: Mapped[list[Announcement]] = relationship(back_populates="course")


class Enrollment(TimestampMixin, Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_enrollments_student_id_course_id"),
        Index("ix_enrollments_teacher_status", "teacher_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="RESTRICT"))
    status: Mapped[EnrollmentStatus] = mapped_column(
        SAEnum(
            EnrollmentStatus,
            name="enrollment_status",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=EnrollmentStatus.ACTIVE,
        server_default=EnrollmentStatus.ACTIVE.value,
    )
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    meeting_link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    student: Mapped[User] = relationship(
        back_populates="student_enrollments",
        foreign_keys=[student_id],
    )
    teacher: Mapped[User] = relationship(
        back_populates="teacher_enrollments",
        foreign_keys=[teacher_id],
    )
    course: Mapped[Course] = relationship(back_populates="enrollments")
    meetings: Mapped[list[Meeting]] = relationship(back_populates="enrollment")


class Material(TimestampMixin, Base):
    __tablename__ = "materials"
    __table_args__ = (Index("ix_materials_course_created", "course_id", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_url: Mapped[str] = mapped_column(String(500))
    original_filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(120))

    course: Mapped[Course] = relationship(back_populates="materials")
    teacher: Mapped[User] = relationship(back_populates="teaching_materials")


class Assignment(TimestampMixin, Base):
    __tablename__ = "assignments"
    __table_args__ = (Index("ix_assignments_course_due", "course_id", "due_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attachment_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    max_score: Mapped[int] = mapped_column(Integer, default=100, server_default="100")

    course: Mapped[Course] = relationship(back_populates="assignments")
    teacher: Mapped[User] = relationship(back_populates="teaching_assignments")
    submissions: Mapped[list[Submission]] = relationship(
        back_populates="assignment",
        cascade="all, delete-orphan",
    )


class Submission(TimestampMixin, Base):
    __tablename__ = "submissions"
    __table_args__ = (
        UniqueConstraint("assignment_id", "student_id", name="uq_submissions_assignment_id_student_id"),
        Index("ix_submissions_student_created", "student_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    assignment_id: Mapped[int] = mapped_column(ForeignKey("assignments.id", ondelete="CASCADE"))
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    file_url: Mapped[str] = mapped_column(String(500))
    original_filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(120))
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    assignment: Mapped[Assignment] = relationship(back_populates="submissions")
    student: Mapped[User] = relationship()


class Announcement(TimestampMixin, Base):
    __tablename__ = "announcements"
    __table_args__ = (Index("ix_announcements_course_created", "course_id", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    title: Mapped[str] = mapped_column(String(160))
    content: Mapped[str] = mapped_column(Text)

    course: Mapped[Course] = relationship(back_populates="announcements")
    teacher: Mapped[User] = relationship(back_populates="created_announcements")


class Meeting(TimestampMixin, Base):
    __tablename__ = "meetings"
    __table_args__ = (Index("ix_meetings_enrollment_scheduled", "enrollment_id", "scheduled_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    enrollment_id: Mapped[int] = mapped_column(ForeignKey("enrollments.id", ondelete="CASCADE"))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    title: Mapped[str] = mapped_column(String(160))
    meeting_url: Mapped[str] = mapped_column(String(500))
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    enrollment: Mapped[Enrollment] = relationship(back_populates="meetings")
    teacher: Mapped[User] = relationship(back_populates="hosted_meetings")


class Inquiry(Base):
    __tablename__ = "inquiries"
    __table_args__ = (Index("ix_inquiries_type_created", "inquiry_type", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    inquiry_type: Mapped[InquiryType] = mapped_column(
        SAEnum(
            InquiryType,
            name="inquiry_type",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=InquiryType.CONTACT,
        server_default=InquiryType.CONTACT.value,
    )
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    message: Mapped[str] = mapped_column(Text)
    course_interest: Mapped[str | None] = mapped_column(String(160), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    __table_args__ = (Index("ix_activity_logs_created_at", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    action: Mapped[str] = mapped_column(String(120), index=True)
    entity_type: Mapped[str] = mapped_column(String(120))
    entity_id: Mapped[int | None] = mapped_column(nullable=True)
    summary: Mapped[str] = mapped_column(String(255))
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    actor: Mapped[User | None] = relationship(back_populates="activity_logs")

