from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

from .cache import REDIS_URL

celery_app = Celery('tasks', broker=f'{REDIS_URL}/1', backend=f'{REDIS_URL}/1')

celery_app.conf.update(
    timezone='Africa/Lagos',
    enable_utc=True,
    include=[
        "src.tasks.mailer",
        "src.tasks.sync_knowledge",
        "src.tasks.simulations"
    ]
)

celery_app.conf.beat_schedule = {
    'sync_knowledge': {
        'task': 'sync_knowledge',
        'schedule': crontab(hour=0, minute=0)
    }
}