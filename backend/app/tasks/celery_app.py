"""Celery application configuration."""
from celery import Celery

from app.config import settings

celery_app = Celery(
    "novel_ai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.generation_tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Bangkok",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    # Task routing — match custom task names
    task_routes={
        "generate_novel": {"queue": "generation"},
    },
    # Task time limits
    task_soft_time_limit=3600,  # 1 hour soft limit
    task_time_limit=7200,  # 2 hour hard limit
)

