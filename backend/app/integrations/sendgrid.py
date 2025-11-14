from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typing import Optional

from app.config import settings
from app.utils.logger import logger


class SendGridClient:
    def __init__(self):
        if settings.SENDGRID_API_KEY:
            self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)
            self.from_email = settings.SENDGRID_FROM_EMAIL
        else:
            self.client = None
            logger.warning("SendGrid API key not configured")
    
    async def send_email(self, to_email: str, subject: str, body: str) -> bool:
        if not self.client:
            logger.warning("SendGrid client not initialized")
            return False
        
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                plain_text_content=body
            )
            
            response = self.client.send(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
