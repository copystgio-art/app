from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "fb_automation",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.search_task", "app.tasks.message_task"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Rome",
    enable_utc=True,
    task_track_started=True,
)
