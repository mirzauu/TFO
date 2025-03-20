# celery.py

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tfo_backend.settings')

celery_app = Celery('tfo_backend')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()

# Ensure broker connection retries on startup (for Celery 6.0+)
celery_app.conf.broker_connection_retry_on_startup = True