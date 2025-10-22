"""
Queue Service Module

Abstraction layer for Celery queue interactions.

Architectural Decision: Why abstraction layer?
- Decouple business logic from Celery implementation
- Easy to swap queue systems (Celery → RQ → SQS)
- Mockable for testing
- Single Responsibility: Only handles queue operations

Design Pattern: Adapter Pattern (wrap Celery API)
"""

import logging
from typing import Any, Dict, Optional

from celery import Celery
from celery.result import AsyncResult

from core.config import settings
from core.exceptions import BrokerConnectionException, TaskNotFoundException

logger = logging.getLogger("celery")


class QueueService:
    """
    Service for queue operations.
    
    Provides abstraction over Celery for task submission and monitoring.
    """
    
    def __init__(self):
        """Initialize Celery app with configuration."""
        self.app = Celery("tasks")
        self.app.config_from_object(settings.get_celery_config())
    
    def submit_task(
        self,
        task_name: str,
        task_data: Dict[str, Any],
        queue: str = "medium",
        priority: int = 5,
    ) -> str:
        """
        Submit task to queue.
        
        Args:
            task_name: Celery task name
            task_data: Task input data
            queue: Target queue name
            priority: Task priority (0-10, higher = more important)
            
        Returns:
            Task ID
            
        Raises:
            BrokerConnectionException: If cannot connect to Redis
        """
        try:
            # CRITICAL: Unpack task_data as **kwargs for Celery
            # Celery's send_task expects kwargs to be a dict that will be unpacked
            # Example: kwargs={'a': 1, 'b': 2} becomes task_func(a=1, b=2)
            logger.info(f"DEBUG - Submitting task {task_name} with kwargs: {list(task_data.keys())}")
            logger.info(f"DEBUG - Full kwargs: {task_data}")
            
            result = self.app.send_task(
                task_name,
                kwargs=task_data,  # This will be unpacked as **task_data
                queue=queue,
                priority=priority,
                serializer='json',
            )
            logger.info(f"Task submitted: {result.id} to queue '{queue}'")
            return result.id
        except Exception as e:
            logger.error(f"Failed to submit task: {e}", exc_info=True)
            raise BrokerConnectionException(str(e))
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get task status and result.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task status dictionary
            
        Raises:
            TaskNotFoundException: If task doesn't exist
        """
        try:
            result = AsyncResult(task_id, app=self.app)
            
            status_data = {
                "task_id": task_id,
                "status": result.state,
                "result": result.result if result.successful() else None,
                "error": str(result.info) if result.failed() else None,
            }
            
            return status_data
        except Exception as e:
            logger.error(f"Failed to get task status for {task_id}: {e}")
            raise TaskNotFoundException(task_id)
    
    def get_queue_length(self, queue: str) -> int:
        """Get number of tasks in queue."""
        try:
            inspect = self.app.control.inspect()
            stats = inspect.stats()
            
            if stats:
                # Sum tasks across all workers for this queue
                total = 0
                for worker, worker_stats in stats.items():
                    total += worker_stats.get("total", {}).get(queue, 0)
                return total
            return 0
        except Exception as e:
            logger.warning(f"Failed to get queue length: {e}")
            return 0


# Singleton instance
queue_service = QueueService()
