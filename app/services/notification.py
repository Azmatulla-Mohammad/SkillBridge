from __future__ import annotations

import logging
from typing import Optional

import resend

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self) -> None:
        self.settings = get_settings()
        
        # Initialize Resend API key if configured
        if self.settings.resend_api_key:
            resend.api_key = self.settings.resend_api_key
        else:
            logger.warning("RESEND_API_KEY not configured. Email notifications will be skipped.")

    def send_email(self, subject: str, html_body: str, text_body: Optional[str] = None) -> None:
        # Skip if Resend API key is not configured
        if not self.settings.resend_api_key:
            logger.warning("RESEND_API_KEY not configured. Skipping email notification.")
            return

        # Skip if email_from or email_to is not configured
        if not self.settings.email_from or not self.settings.email_to:
            logger.warning("EMAIL_FROM or EMAIL_TO not configured. Skipping email notification.")
            return

        try:
            params: dict = {
                "from": self.settings.email_from,
                "to": [self.settings.email_to],
                "subject": subject,
                "html": html_body,
            }

            # Add text body if provided
            if text_body:
                params["text"] = text_body

            resend.Emails.send(params)
            logger.info("Email sent successfully via Resend")
        except Exception:
            logger.exception("Failed to send email using Resend")
            # Must not raise: caller will handle success to the user.
            return