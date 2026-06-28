from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.utils import utcnow
from app.models import Course, Inquiry, InquiryType, User, UserRole
from app.repositories.academic import AcademicRepository
from app.repositories.public import PublicRepository
from app.services.common import record_activity


settings = get_settings()


FAQ_ITEMS = [
    {
        "question": "How does SkillBridge work?",
        "answer": "An admin verifies payment, creates student and teacher accounts, and assigns the one-to-one learning schedule inside the platform.",
    },
    {
        "question": "Can students sign up on their own?",
        "answer": "No. SkillBridge is a managed platform. Accounts are created only by the admin after verification.",
    },
    {
        "question": "What happens after a free demo request?",
        "answer": "Your request is stored in the CRM queue so the team can contact you, verify your goals, and schedule the first conversation.",
    },
    {
        "question": "How are classes conducted?",
        "answer": "Teachers share and update Google Meet links inside the student dashboard, alongside assignments, materials, and feedback.",
    },
]


TESTIMONIALS = [
    {
        "name": "Aarav Sharma",
        "role": "Parent",
        "quote": "The one-to-one structure feels premium. We always know what was taught, what was assigned, and what progress was made.",
    },
    {
        "name": "Naina Verma",
        "role": "Working Professional",
        "quote": "It feels much more focused than a marketplace platform. Every class builds directly on my goals.",
    },
    {
        "name": "Rahul Mehta",
        "role": "Student",
        "quote": "Assignments, feedback, materials, and meetings are all in one place. It makes learning smoother and less stressful.",
    },
]


FEATURES = [
    {
        "title": "One-to-One Live Classes",
        "description": "Every student is assigned directly to a teacher for structured live mentorship, not an open marketplace experience.",
    },
    {
        "title": "Admin-Controlled Operations",
        "description": "Account creation, teacher assignment, and course access stay tightly managed so the learning experience remains clean and reliable.",
    },
    {
        "title": "Assignments and Feedback",
        "description": "Teachers upload materials, create assignments, review submissions, and leave clear feedback from the same workflow.",
    },
    {
        "title": "Production-Ready Dashboards",
        "description": "Role-based dashboards keep admin operations, teacher work, and student progress separated and easy to navigate.",
    },
]


class PublicService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.academic_repo = AcademicRepository(db)
        self.public_repo = PublicRepository(db)

    def site_context(self) -> dict:
        courses, _ = self.academic_repo.list_courses(is_active=True, page=1, page_size=20)
        teacher_count = self.db.scalar(
            select(func.count(User.id)).where(User.role == UserRole.TEACHER)
        ) or 0
        student_count = self.db.scalar(
            select(func.count(User.id)).where(User.role == UserRole.STUDENT)
        ) or 0
        return {
            "courses": courses,
            "faqs": FAQ_ITEMS,
            "features": FEATURES,
            "testimonials": TESTIMONIALS,
            "stats": {
                "teachers": teacher_count,
                "students": student_count,
                "courses": len(courses),
            },
            "whatsapp_number": settings.public_whatsapp_number,
            "has_whatsapp_number": bool(settings.public_whatsapp_number),
        }

    def submit_inquiry(
        self,
        *,
        inquiry_type: InquiryType,
        name: str,
        email: str,
        phone: str | None,
        message: str,
        course_interest: str | None,
    ) -> Inquiry:
        inquiry = self.public_repo.create_inquiry(
            Inquiry(
                inquiry_type=inquiry_type,
                name=name.strip(),
                email=email.lower().strip(),
                phone=(phone or "").strip() or None,
                message=message.strip(),
                course_interest=(course_interest or "").strip() or None,
                created_at=utcnow(),
            )
        )
        record_activity(
            self.db,
            actor_user_id=None,
            action=f"public.{inquiry_type.value}.created",
            entity_type="inquiry",
            entity_id=inquiry.id,
            summary=f"Received a {inquiry_type.value} request from {inquiry.name}.",
        )
        self.db.commit()
        return inquiry
