import logging
import os

logger = logging.getLogger(__name__)

class EmailSender:
    """Minimal email sender abstraction.

    In production this would integrate with SES/Resend/etc. For now it logs the outbound
    verification intent. Future enhancement: queue dispatch, retry, HTML templates.
    """
    def __init__(self):
        self.env = os.getenv("ENV", "development")

    async def send_email_verification(self, to_email: str, token: str):
        # In production you'd build a proper verification URL.
        base = os.getenv("PUBLIC_APP_URL", "http://localhost:3000")
        verify_url = f"{base}/verify-email?token={token}"  # front-end can call confirm endpoint
        if self.env != "production":
            logger.info(f"[DEV EMAIL] To:{to_email} Verify URL: {verify_url} token={token}")
        else:
            # Placeholder production path
            logger.info(f"Email verification dispatched to {to_email}")

email_sender = EmailSender()
