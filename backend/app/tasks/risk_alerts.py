from celery import shared_task
from app.celery_app import celery_app
from app.services.alert_service import AlertService
from app.core.database import async_session
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio


@shared_task(bind=True)
def check_risk_alerts(self):
    """Periodic task to check and trigger risk-related alerts."""
    async def run_check():
        async with async_session() as db:
            async with db.begin():
                alert_service = AlertService(db)
                triggered = await alert_service.check_and_trigger_all_risk_alerts()
                return triggered
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(run_check())
        return result
    finally:
        loop.close()

# Schedule this task to run every 5 minutes (adjust as needed)
# This can be configured in Celery Beat schedule
