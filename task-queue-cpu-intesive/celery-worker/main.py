"""
Celery Application Initialization

Configures Celery for distributed task processing with:
- Redis broker for task queue
- Result backend for task state storage
- Production-ready settings (prefetch, concurrency, timeouts)
- Structured logging
"""

import os
import logging
from celery import Celery
from celery.signals import setup_logging

# Configure logging
@setup_logging.connect
def config_loggers(*args, **kwargs):
    """Configure structured logging for Celery workers."""
    from logging.config import dictConfig
    
    dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'json',
                'stream': 'ext://sys.stdout'
            }
        },
        'root': {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'handlers': ['console']
        },
        'loggers': {
            'celery': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False
            }
        }
    })


# Celery configuration
BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis-broker:6379/0')
RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis-broker:6379/0')

app = Celery('tasks')

# Production-optimized settings
app.conf.update(
    # Broker settings
    broker_url=BROKER_URL,
    result_backend=RESULT_BACKEND,
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    
    # Task settings
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    
    # Performance settings
    task_acks_late=True,  # Acknowledge after completion
    worker_prefetch_multiplier=1,  # Fetch one task at a time (CPU-bound)
    worker_max_tasks_per_child=100,  # Restart after 100 tasks (prevent memory leaks)
    
    # Result settings
    result_expires=3600,  # Results expire after 1 hour
    result_extended=True,  # Include args/kwargs in result
    
    # Time limits (safety net for runaway tasks)
    task_soft_time_limit=300,  # 5 minutes soft limit
    task_time_limit=360,  # 6 minutes hard limit
    
    # Reliability settings
    task_reject_on_worker_lost=True,
    task_track_started=True,
    
    # Rate limiting (prevent broker overload)
    task_default_rate_limit='100/s',
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Auto-discover tasks from tasks.py
app.autodiscover_tasks(['tasks'], force=True)

logger = logging.getLogger(__name__)
logger.info(
    f"Celery app initialized - Broker: {BROKER_URL}, "
    f"Prefetch: {app.conf.worker_prefetch_multiplier}"
)
