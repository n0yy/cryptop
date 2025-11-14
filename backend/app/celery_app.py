from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    'cryptop',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Celery Beat schedule for risk alerts check every 5 minutes
celery_app.conf.beat_schedule = {
    'check-risk-alerts-every-5-minutes': {
        'task': 'app.tasks.risk_alerts.check_risk_alerts',
        'schedule': 300.0,  # 5 minutes in seconds
    },
}
