from datetime import datetime

from pydantic import BaseModel


class TeacherMaterialCreate(BaseModel):
    title: str
    description: str | None = None
    course_id: int


class TeacherAssignmentCreate(BaseModel):
    title: str
    description: str
    course_id: int
    due_at: datetime | None = None
    max_score: int = 100


class TeacherAssignmentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_at: datetime | None = None
    max_score: int | None = None
    attachment_url: str | None = None


class SubmissionReview(BaseModel):
    score: int
    feedback: str


class AnnouncementCreate(BaseModel):
    course_id: int
    title: str
    content: str


class MeetingCreate(BaseModel):
    enrollment_id: int
    title: str
    meeting_url: str
    scheduled_at: datetime
    notes: str | None = None


class TeacherProfileUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    bio: str | None = None
    headline: str | None = None
    expertise: str | None = None
    meeting_link: str | None = None

