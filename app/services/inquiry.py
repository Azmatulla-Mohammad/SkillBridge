from __future__ import annotations

import re
from datetime import timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.core.utils import utcnow
from app.models import Inquiry, InquiryType
from app.repositories.public import PublicRepository


_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
_PHONE_RE = re.compile(r"^\d{10,15}$")


class InquiryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.public_repo = PublicRepository(db)

    def validate(
        self,
        *,
        inquiry_type: InquiryType,
        name: str,
        email: str,
        phone: str | None,
        message: str,
        course_interest: str | None,
    ) -> None:
        name = (name or "").strip()
        email = (email or "").strip()
        message = (message or "").strip()

        if not name:
            raise ValueError("Full name is required.")
        if not email:
            raise ValueError("Email is required.")
        if not _EMAIL_RE.match(email):
            raise ValueError("Please provide a valid email address.")

        if phone is None:
            raise ValueError("Phone number is required.")

        phone_clean = str(phone).strip()
        if not phone_clean:
            raise ValueError("Phone number is required.")
        if not _PHONE_RE.match(phone_clean):
            raise ValueError("Phone number must be 10–15 digits.")

        if not message:
            raise ValueError("Message is required.")

    def prevent_duplicate(
        self,
        *,
        inquiry_type: InquiryType,
        name: str,
        email: str,
        phone: str,
        message: str,
        course_interest: str | None,
        within: timedelta = timedelta(minutes=2),
    ) -> bool:
        """Return True if a duplicate exists and we should NOT insert a new row."""
        cutoff = utcnow() - within

        email_lc = email.lower().strip()
        phone_norm = str(phone).strip()
        message_trim = message.strip()

        stmt = (
            select(func.count(Inquiry.id))
            .where(
                and_(
                    Inquiry.inquiry_type == inquiry_type,
                    Inquiry.email == email_lc,
                    Inquiry.phone == phone_norm,
                    Inquiry.message == message_trim,
                    Inquiry.created_at >= cutoff,
                )
            )
            .limit(1)
        )
        existing_count = self.db.scalar(stmt) or 0
        return existing_count > 0

    def create_inquiry(
        self,
        *,
        inquiry_type: InquiryType,
        name: str,
        email: str,
        phone: str | None,
        message: str,
        course_interest: str | None,
    ) -> Inquiry:
        self.validate(
            inquiry_type=inquiry_type,
            name=name,
            email=email,
            phone=phone,
            message=message,
            course_interest=course_interest,
        )

        if self.prevent_duplicate(
            inquiry_type=inquiry_type,
            name=name,
            email=email,
            phone=str(phone),
            message=message,
            course_interest=course_interest,
        ):
            raise ValueError("Your enquiry has already been received.")

        inquiry = self.public_repo.create_inquiry(
            Inquiry(
                inquiry_type=inquiry_type,
                name=name.strip(),
                email=email.lower().strip(),
                phone=str(phone).strip(),
                message=message.strip(),
                course_interest=(course_interest or "").strip() or None,
                created_at=utcnow(),
            )
        )
        return inquiry

