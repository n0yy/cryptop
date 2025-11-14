from twilio.rest import Client
from typing import Optional

from app.config import settings
from app.utils.logger import logger


class TwilioClient:
    def __init__(self):
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.from_phone = settings.TWILIO_PHONE_NUMBER
        else:
            self.client = None
            logger.warning("Twilio credentials not configured")
    
    async def send_sms(self, to_phone: str, body: str) -> bool:
        if not self.client:
            logger.warning("Twilio client not initialized")
            return False
        
        try:
            message = self.client.messages.create(
                body=body,
                from_=self.from_phone,
                to=to_phone
            )
            
            logger.info(f"SMS sent successfully: {message.sid}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
