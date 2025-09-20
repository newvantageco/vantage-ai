"""
Celery application configuration for VANTAGE AI
Handles background tasks, scheduled jobs, and async processing
"""

from celery import Celery
from celery.schedules import crontab
import os

# Get Redis URL from environment
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

# Create Celery instance
celery_app = Celery(
    "vantage_ai",
    broker=redis_url,
    backend=redis_url,
    include=[
        "app.workers.tasks.content_tasks",
        "app.workers.tasks.publishing_tasks",
        "app.workers.tasks.analytics_tasks",
        "app.workers.tasks.integration_tasks",
        "app.workers.tasks.scheduler_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
    task_always_eager=False,  # Set to True for testing
    task_eager_propagates=True,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Sync integrations every hour
    "sync-integrations": {
        "task": "app.workers.tasks.integration_tasks.sync_all_integrations",
        "schedule": crontab(minute=0),  # Every hour
    },
    # Update analytics every 6 hours
    "update-analytics": {
        "task": "app.workers.tasks.analytics_tasks.update_analytics",
        "schedule": crontab(minute=0, hour="*/6"),  # Every 6 hours
    },
    # Process scheduled content every 5 minutes
    "process-scheduled-content": {
        "task": "app.workers.tasks.scheduler_tasks.process_scheduled_content",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
    # Clean up old data daily
    "cleanup-old-data": {
        "task": "app.workers.tasks.analytics_tasks.cleanup_old_data",
        "schedule": crontab(minute=0, hour=2),  # Daily at 2 AM
    },
    # Send daily reports
    "send-daily-reports": {
        "task": "app.workers.tasks.analytics_tasks.send_daily_reports",
        "schedule": crontab(minute=0, hour=9),  # Daily at 9 AM
    },
}

# Task routing
celery_app.conf.task_routes = {
    "app.workers.tasks.content_tasks.*": {"queue": "content"},
    "app.workers.tasks.publishing_tasks.*": {"queue": "publishing"},
    "app.workers.tasks.analytics_tasks.*": {"queue": "analytics"},
    "app.workers.tasks.integration_tasks.*": {"queue": "integrations"},
    "app.workers.tasks.scheduler_tasks.*": {"queue": "scheduler"},
}

if __name__ == "__main__":
    celery_app.start()
