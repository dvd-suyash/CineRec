from celery import Celery
from cinerec.core.config import settings

celery_app = Celery(
    "cinerec_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["apps.worker.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
)
