from datetime import date, datetime

from pydantic import BaseModel

from app.models import EnrollmentStatus, UserRole


class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    role: UserRole
    phone: str | None = None
    bio: str | None = None
    headline: str | None = None
    expertise: str | None = None
    guardian_name: str | None = None
    learning_goals: str | None = None


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    password: str | None = None
    phone: str | None = None
    bio: str | None = None
    is_active: bool | None = None
    headline: str | None = None
    expertise: str | None = None
    guardian_name: str | None = None
    learning_goals: str | None = None


class CourseCreate(BaseModel):
    title: str
    slug: str | None = None
    description: str
    duration_weeks: int = 12
    price: int = 0
    is_active: bool = True


class CourseUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    description: str | None = None
    duration_weeks: int | None = None
    price: int | None = None
    is_active: bool | None = None


class EnrollmentCreate(BaseModel):
    student_id: int
    teacher_id: int
    course_id: int
    status: EnrollmentStatus = EnrollmentStatus.ACTIVE
    start_date: date | None = None
    meeting_link: str | None = None
    notes: str | None = None


class EnrollmentUpdate(BaseModel):
    teacher_id: int | None = None
    course_id: int | None = None
    status: EnrollmentStatus | None = None
    start_date: date | None = None
    meeting_link: str | None = None
    notes: str | None = None
    progress_percent: int | None = None


class AssignmentAdminCreate(BaseModel):
    title: str
    description: str
    course_id: int
    teacher_id: int
    due_at: datetime | None = None
    max_score: int = 100
    attachment_url: str | None = None


class AssignmentAdminUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    course_id: int | None = None
    teacher_id: int | None = None
    due_at: datetime | None = None
    max_score: int | None = None
    attachment_url: str | None = None

