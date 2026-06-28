from __future__ import annotations

import re
from datetime import timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.core.utils import utcnow
from app.models import Inquiry, InquiryType
from app.repositories.public import PublicRepository
from app.services.notification import NotificationService




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
        # 1) Validate
        self.validate(
            inquiry_type=inquiry_type,
            name=name,
            email=email,
            phone=phone,
            message=message,
            course_interest=course_interest,
        )

        # 2) Prevent duplicate
        if self.prevent_duplicate(
            inquiry_type=inquiry_type,
            name=name,
            email=email,
            phone=str(phone),
            message=message,
            course_interest=course_interest,
        ):
            raise ValueError("Your enquiry has already been received.")


        # Normalize values for email body
        name_clean = (name or "").strip()
        email_clean = (email or "").strip().lower()
        phone_clean = str(phone).strip() if phone is not None else ""
        message_clean = (message or "").strip()
        course_interest_clean = (course_interest or "").strip() or None
        submitted_time = utcnow()

        # 3) Create inquiry
        inquiry = self.public_repo.create_inquiry(
            Inquiry(
                inquiry_type=inquiry_type,
                name=name_clean,
                email=email_clean,
                phone=phone_clean,
                message=message_clean,
                course_interest=course_interest_clean,
                created_at=submitted_time,
            )
        )

        # 4) Commit database transaction
        # Must be committed before sending email.
        self.db.commit()

        # 5) Instantiate NotificationService
        notification_service = NotificationService()

        # 6) Build subject + professional HTML/plain text email
        if inquiry_type == InquiryType.DEMO:
            subject = "New SkillBridge Book Demo Request"
        else:
            subject = "New SkillBridge Contact Request"

        inquiry_type_label = "Demo" if inquiry_type == InquiryType.DEMO else "Contact"
        course_line = course_interest_clean or "N/A"

        html_body = f"""\
<html>
  <body style=\"font-family: Arial, sans-serif; color: #111;\">
    <h2 style=\"margin-bottom: 10px;\">{subject}</h2>
    <p style=\"margin-top: 0;\">A new inquiry has been submitted on SkillBridge.</p>

    <table style=\"border-collapse: collapse; width: 100%; max-width: 720px;\">
      <tr><td style=\"padding: 8px; border: 1px solid #e5e5e5; font-weight: bold;\">Name</td><td style=\"padding: 8px; border: 1px solid #e5e5e5;\">{name_clean}</td></tr>
      <tr><td style=\"padding: 8px; border: 1px solid #e5e5e5; font-weight: bold;\">Email</td><td style=\"padding: 8px; border: 1px solid #e5e5e5;\">{email_clean}</td></tr>
      <tr><td style=\"padding: 8px; border: 1px solid #e5e5e5; font-weight: bold;\">Phone</td><td style=\"padding: 8px; border: 1px solid #e5e5e5;\">{phone_clean}</td></tr>
      <tr><td style=\"padding: 8px; border: 1px solid #e5e5e5; font-weight: bold;\">Course</td><td style=\"padding: 8px; border: 1px solid #e5e5e5;\">{course_line}</td></tr>
      <tr><td style=\"padding: 8px; border: 1px solid #e5e5e5; font-weight: bold;\">Inquiry Type</td><td style=\"padding: 8px; border: 1px solid #e5e5e5;\">{inquiry_type_label}</td></tr>
      <tr><td style=\"padding: 8px; border: 1px solid #e5e5e5; font-weight: bold; vertical-align: top;\">Message</td><td style=\"padding: 8px; border: 1px solid #e5e5e5;\">{message_clean}</td></tr>
      <tr><td style=\"padding: 8px; border: 1px solid #e5e5e5; font-weight: bold;\">Submitted Time</td><td style=\"padding: 8px; border: 1px solid #e5e5e5;\">{submitted_time.isoformat()}</td></tr>
    </table>

    <p style=\"margin-top: 16px; color: #555;\">Please follow up with the requester.</p>
  </body>
</html>
"""

        text_body = (
            f"{subject}\n\n"
            f"Name: {name_clean}\n"
            f"Email: {email_clean}\n"
            f"Phone: {phone_clean}\n"
            f"Course: {course_line}\n"
            f"Inquiry Type: {inquiry_type_label}\n"
            f"Message: {message_clean}\n\n"
            f"Submitted Time: {submitted_time.isoformat()}\n"
        )

        # 7) send_email()
        # 8) If SMTP fails: never rollback DB, never show exception to user.
        # NotificationService already swallows exceptions; keep this guard to enforce the contract.
        try:
            notification_service.send_email(
                subject=subject,
                html_body=html_body,
                text_body=text_body,
            )
        except Exception:
            # Must log "Email failed" and continue.
            import logging as _logging
            _logging.getLogger(__name__).exception("Email failed")


        # 9) Return inquiry
        return inquiry


