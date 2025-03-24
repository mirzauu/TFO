# celery.py

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tfo_backend.settings')

celery_app = Celery('tfo_backend')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.conf.task_time_limit = 500  # Hard limit (force kill)
celery_app.conf.task_soft_time_limit = 300  # Grace period (warning)

print(celery_app.conf.task_time_limit)
celery_app.autodiscover_tasks()
# Ensure broker connection retries on startup (for Celery 6.0+)
