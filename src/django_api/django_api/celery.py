"""
Celery application configuration for django_api project.

This module configures Celery for asynchronous task processing.
Tasks are defined in each Django app's tasks.py file and auto-discovered.

Usage:
    # Start worker (development)
    celery -A django_api worker -l info

    # Start worker with beat scheduler (for periodic tasks)
    celery -A django_api worker -B -l info

    # Production (multiple workers)
    celery -A django_api worker -l info -c 2
"""

import os

from celery import Celery

from observability import get_logger

logger = get_logger(__name__)

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_api.settings")

app = Celery("django_api")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix in Django settings.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self) -> None:
    """Debug task to verify Celery is working correctly."""
    logger.info("Celery debug task executed: %r", self.request)
