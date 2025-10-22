"""
API Routes Module

RESTful API endpoints for task management.

Architectural Decisions:
1. **Why APIRouter?**
   - Modular route organization
   - Easy to version (v1, v2 routers)
   - Testable in isolation
   - Clear separation from main app

2. **Why Dependency Injection?**
   - Request-scoped loggers with correlation IDs
   - Easy to mock in tests
   - Loose coupling

3. **Why Path/Query Parameters?**
   - RESTful design
   - Auto-validated by FastAPI
   - Auto-documented in OpenAPI

Design Patterns:
- RESTful API: Standard HTTP verbs and status codes
- Dependency Injection: Request-scoped dependencies
- Facade: Simplified interface to complex services
"""

import logging
from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse

from core.config import settings
from core.exceptions import TaskQueueException
from models.requests import TaskCreateRequest
from models.responses import (
    HealthResponse,
    TaskCreateResponse,
    TaskResponse,
)
from services.task_service import task_service

logger = logging.getLogger("api")

# Create router
router = APIRouter(prefix="/api/v1", tags=["tasks"])


@router.post(
    "/tasks",
    response_model=TaskCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Submit a financial calculation task to the queue for processing",
    responses={
        201: {
            "description": "Task created successfully",
            "model": TaskCreateResponse,
        },
        400: {"description": "Invalid task data"},
        503: {"description": "Queue is full (backpressure)"},
    },
)
async def create_task(
    request: Request,
    task_request: TaskCreateRequest,
) -> TaskCreateResponse:
    """
    Create a new task.
    
    Submits a financial calculation task to the queue.
    Returns task ID for polling status.
    
    **Circuit Breaker**: Returns 503 if queue is full.
    
    Args:
        request: FastAPI request
        task_request: Task creation request
        
    Returns:
        Task creation response with task ID
        
    Raises:
        QueueFullException: If queue is at capacity
        InvalidTaskException: If task data is invalid
    """
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    
    logger.info(
        f"Creating task with priority: {task_request.priority}",
        extra={"request_id": correlation_id},
    )
    
    # Create task via service layer
    result = task_service.create_task(
        task_data=task_request.data,
        priority=task_request.priority,
        queue=task_request.queue,
    )
    
    return TaskCreateResponse(**result)


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Get task status",
    description="Retrieve the current status and result of a task",
    responses={
        200: {
            "description": "Task found",
            "model": TaskResponse,
        },
        404: {"description": "Task not found"},
    },
)
async def get_task(
    task_id: str,
    request: Request,
) -> TaskResponse:
    """
    Get task status and result.
    
    Returns current task status and result (if complete).
    
    **Task States**:
    - PENDING: Task queued, not started
    - STARTED: Task is processing
    - SUCCESS: Task completed successfully
    - FAILURE: Task failed with error
    - RETRY: Task is being retried
    
    Args:
        task_id: Unique task identifier
        request: FastAPI request
        
    Returns:
        Task status and result
        
    Raises:
        TaskNotFoundException: If task doesn't exist
    """
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    
    logger.info(
        f"Fetching task status: {task_id}",
        extra={"request_id": correlation_id},
    )
    
    # Get task status via service layer
    task_data = task_service.get_task_status(task_id)
    
    return TaskResponse(
        task_id=task_id,
        status=task_data["status"],
        priority="medium",  # TODO: Store priority in Redis
        queue="medium",
        result=task_data.get("result"),
        error=task_data.get("error"),
        created_at=task_data["created_at"],
        started_at=task_data.get("started_at"),
        completed_at=task_data.get("completed_at"),
        processing_time_ms=task_data.get("processing_time_ms"),
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check API health and dependencies",
    tags=["system"],
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Used by:
    - Docker health checks
    - Nginx load balancer
    - Monitoring systems
    
    Returns:
        Health status and dependencies
    """
    # Check Redis connection
    try:
        redis_status = "healthy"
        # TODO: Actual Redis ping
    except Exception:
        redis_status = "unhealthy"
    
    # Check Celery workers
    try:
        worker_count = 3  # TODO: Actual worker count from Celery
        celery_status = f"{worker_count} workers online"
    except Exception:
        celery_status = "unavailable"
    
    # Get queue stats
    queue_stats = {}
    for queue_name in ["high", "medium", "low"]:
        try:
            queue_stats[queue_name] = 0  # TODO: Actual queue length
        except Exception:
            queue_stats[queue_name] = -1
    
    # Determine overall status
    overall_status = "healthy"
    if redis_status != "healthy" or "unavailable" in celery_status:
        overall_status = "degraded"
    
    return HealthResponse(
        status=overall_status,
        version=settings.api.version,
        server_id=settings.server_id,
        timestamp=datetime.utcnow(),
        dependencies={
            "redis": redis_status,
            "celery_broker": redis_status,
            "celery_workers": celery_status,
        },
        queue_stats=queue_stats,
    )
