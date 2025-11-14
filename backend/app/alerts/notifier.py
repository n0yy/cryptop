from typing import List, Dict
import json

from app.integrations.twilio import TwilioClient
from app.integrations.sendgrid import SendGridClient
from app.utils.logger import logger
from app.utils.cache import get_redis_client


class AlertNotifier:
    def __init__(self):
        self.twilio = TwilioClient()
        self.sendgrid = SendGridClient()
    
    async def send_notification(self, user_id: int, channels: List[str], message: Dict):
        for channel in channels:
            try:
                if channel == "EMAIL":
                    await self._send_email(user_id, message)
                elif channel == "SMS":
                    await self._send_sms(user_id, message)
                elif channel == "DISCORD":
                    await self._send_discord(user_id, message)
                elif channel == "PUSH":
                    await self._send_push(user_id, message)
                
                logger.info(f"Sent {channel} notification to user {user_id}")
            
            except Exception as e:
                logger.error(f"Error sending {channel} notification: {e}")
    
    async def _send_email(self, user_id: int, message: Dict):
        subject = f"Alert Triggered: {message['symbol']}"
        body = f"""
        Your alert has been triggered!
        
        Symbol: {message['symbol']}
        Condition: {message['condition']}
        Threshold: {message['threshold']}
        Current Price: {message['currentPrice']}
        
        Message: {message['message']}
        """
        
        await self.sendgrid.send_email(
            to_email=f"user{user_id}@example.com",
            subject=subject,
            body=body
        )
    
    async def _send_sms(self, user_id: int, message: Dict):
        sms_body = f"Alert: {message['symbol']} {message['condition']} {message['threshold']} (Current: {message['currentPrice']})"
        
        await self.twilio.send_sms(
            to_phone="+1234567890",
            body=sms_body
        )
    
    async def _send_discord(self, user_id: int, message: Dict):
        redis_client = await get_redis_client()
        await redis_client.publish(
            "discord_notifications",
            json.dumps({
                "user_id": user_id,
                "message": message
            })
        )
    
    async def _send_push(self, user_id: int, message: Dict):
        redis_client = await get_redis_client()
        await redis_client.publish(
            "push_notifications",
            json.dumps({
                "user_id": user_id,
                "message": message
            })
        )
