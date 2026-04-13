"""Celery background task queue configuration.

Configures Celery with Redis broker/backend and scheduled tasks.
"""
from celery import Celery

from src.lib.utils.config import REDIS_URL


def make_celery() -> Celery:
    """Create and configure Celery application instance.

    Configures:
    - Redis broker and backend
    - UTC timezone
    - Task modules to include
    - Scheduled tasks (daily knowledge sync at midnight)

    Returns:
        Configured Celery application instance
    """
    celery_app = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)

    celery_app.conf.update(
        timezone='UTC',
        enable_utc=True,
        include=[
            "src.tasks.send_mail",
            "src.tasks.sync_knowledge",
            "src.tasks.run_simulation"
        ]
    )

    celery_app.conf.beat_schedule = {
        # 'sync_knowledge': {
        #     'task': 'sync_knowledge',
        #     'schedule': crontab(hour=0, minute=0)
        # }
    }

    return celery_app

celery_app = make_celery()

