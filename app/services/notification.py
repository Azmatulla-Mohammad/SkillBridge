from __future__ import annotations

import logging
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _get_smtp_config(
        self,
    ) -> tuple[str, int, str | None, str | None, str, str] | tuple[None, None, None, None, None, None]:
        host = self.settings.smtp_host
        port = self.settings.smtp_port
        username = self.settings.smtp_username
        password = self.settings.smtp_password
        smtp_from = self.settings.smtp_from
        smtp_to = self.settings.smtp_to

        if not host or port is None or not smtp_from or not smtp_to:
            return None, None, None, None, None, None

        return host, int(port), username, password, smtp_from, smtp_to



    def send_email(self, subject: str, html_body: str, text_body: Optional[str] = None) -> None:
        smtp_host, smtp_port, smtp_username, smtp_password, smtp_from, smtp_to = self._get_smtp_config()  # type: ignore[misc]

        if not smtp_host:
            logger.warning("SMTP not configured. Skipping email notification.")
            return

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_from
        msg["To"] = smtp_to

        if text_body:
            msg.attach(MIMEText(text_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                server.ehlo()
                if smtp_username and smtp_password:
                    try:
                        server.starttls()
                    except smtplib.SMTPException:
                        # If STARTTLS is not supported, continue; auth may still work.
                        pass
                    if smtp_username and smtp_password:
                        server.login(smtp_username, smtp_password)

                server.sendmail(smtp_from, [smtp_to], msg.as_string())

            logger.info("Email sent successfully")
        except Exception:
            logger.exception("Email failed")
            # Must not raise: caller will handle success to the user.
            return


