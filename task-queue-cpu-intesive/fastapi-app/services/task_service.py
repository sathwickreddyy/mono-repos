"""
Task Service Module

Business logic for task management.

Architectural Decision: Why service layer?
- Separate business logic from HTTP layer
- Reusable across different interfaces (API, CLI, tests)
- Circuit breaker pattern for backpressure
- Single Responsibility Principle

Design Patterns:
- Service Layer: Orchestrates business operations
- Circuit Breaker: Prevents system overload
- Dependency Injection: Loose coupling for testing
"""

import logging
from datetime import datetime
from typing import Any, Dict

from core.config import settings
from core.exceptions import QueueFullException, TaskNotFoundException
from services.queue_service import queue_service

logger = logging.getLogger("api")


class TaskService:
    """
    Service for task management operations.
    
    Handles task creation, status checking, and queue monitoring.
    Implements circuit breaker pattern for backpressure.
    """
    
    def __init__(self):
        """Initialize task service."""
        self.queue_service = queue_service
        self.max_queue_size = settings.api.max_queue_size
    
    def create_task(
        self,
        task_data: Dict[str, Any],
        priority: str = "medium",
        queue: str = None,
    ) -> Dict[str, Any]:
        """
        Create and submit a new task.
        
        Implements circuit breaker: Rejects tasks when queue is full.
        
        Args:
            task_data: Task input data
            priority: Task priority (high, medium, low)
            queue: Target queue (auto-assigned if None)
            
        Returns:
            Task creation response
            
        Raises:
            QueueFullException: If queue is at capacity
        """
        # Auto-assign queue from priority if not specified
        if queue is None:
            queue = priority
        
        # Circuit breaker: Check queue depth
        queue_length = self.queue_service.get_queue_length(queue)
        if queue_length >= self.max_queue_size:
            logger.warning(
                f"Queue '{queue}' is full: {queue_length}/{self.max_queue_size}"
            )
            raise QueueFullException(queue_length, self.max_queue_size)
        
        # Submit task to queue
        # Default to VaR calculation - the most common CPU-intensive task
        task_name = task_data.get("task_type", "calculate_var")
        
        # Map task types to Celery task names
        task_map = {
            "calculate_var": "tasks.calculate_var",
            "monte_carlo": "tasks.monte_carlo_pricing",
            "optimize": "tasks.portfolio_optimization",
            "stress_test": "tasks.stress_test",
        }
        
        celery_task_name = task_map.get(task_name, "tasks.calculate_var")
        
        task_id = self.queue_service.submit_task(
            task_name=celery_task_name,
            task_data=task_data,
            queue=queue,
            priority=self._get_priority_value(priority),
        )
        
        # Estimate wait time based on queue depth
        estimated_wait = self._estimate_wait_time(queue_length)
        
        logger.info(
            f"Task created: {task_id} in queue '{queue}' (depth: {queue_length})"
        )
        
        return {
            "task_id": task_id,
            "status": "PENDING",
            "queue": queue,
            "message": "Task created successfully and queued for processing",
            "estimated_wait_time_seconds": estimated_wait,
        }
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get task status and result.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task status information
            
        Raises:
            TaskNotFoundException: If task doesn't exist
        """
        status_data = self.queue_service.get_task_status(task_id)
        
        # Enrich with timestamps (mock for now - actual timestamps from Celery)
        status_data.update({
            "created_at": datetime.utcnow(),
            "started_at": datetime.utcnow() if status_data["status"] != "PENDING" else None,
            "completed_at": datetime.utcnow() if status_data["status"] in ["SUCCESS", "FAILURE"] else None,
            "processing_time_ms": 6000.0 if status_data["status"] == "SUCCESS" else None,
        })
        
        return status_data
    
    def _get_priority_value(self, priority: str) -> int:
        """
        Convert priority string to Celery priority value.
        
        Args:
            priority: Priority level (high, medium, low)
            
        Returns:
            Priority value (0-10, higher = more important)
        """
        priority_map = {
            "high": 9,
            "medium": 5,
            "low": 1,
        }
        return priority_map.get(priority, 5)
    
    def _estimate_wait_time(self, queue_length: int) -> int:
        """
        Estimate task wait time based on queue depth.
        
        Assumes:
        - 12 parallel tasks (3 workers × 4 concurrency)
        - 6 seconds per task
        
        Args:
            queue_length: Number of tasks in queue
            
        Returns:
            Estimated wait time in seconds
        """
        parallel_capacity = 12  # 3 workers × 4 concurrency
        task_duration = 6  # seconds
        
        if queue_length == 0:
            return 0
        
        # Calculate how many "batches" ahead in queue
        batches = (queue_length // parallel_capacity) + 1
        return batches * task_duration


# Singleton instance
task_service = TaskService()
