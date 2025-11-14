from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "crypto_monitoring",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.alert_tasks",
        "app.tasks.report_tasks",
        "app.tasks.digest_tasks"
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
)

celery_app.conf.beat_schedule = {
    "check-alerts-every-5-seconds": {
        "task": "app.tasks.alert_tasks.check_all_alerts",
        "schedule": 5.0,
    },
    "generate-daily-digests": {
        "task": "app.tasks.digest_tasks.generate_daily_digests",
        "schedule": crontab(hour=8, minute=0),
    },
    "cleanup-old-data": {
        "task": "app.tasks.digest_tasks.cleanup_old_data",
        "schedule": crontab(hour=2, minute=0),
    },
}

if __name__ == "__main__":
    celery_app.start()
