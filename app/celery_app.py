from celery import Celery
import os
from app.core.config import settings
from celery.schedules import crontab

CELERY_BROKER_URL = settings.CELERY_BROKER_URL
CELERY_RESULT_BACKEND = settings.CELERY_RESULT_BACKEND

celery = Celery(
    "certificate_app",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.certificate_tasks",
        "app.tasks.cleanup_tasks"
          ],
    )

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    result_expires=3600,
)

celery.conf.beat_schedule.update({
    "cleanup-temp-files-every-12-hours": {
        "task": "tasks.cleanup_temp_files",
        "schedule": crontab(hour="0,12", minute=0),  # At 00:00 and 12:00
    }
})
