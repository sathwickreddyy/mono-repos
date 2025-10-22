"""
Response Models Module

This module defines Pydantic models for API responses.

Architectural Decisions:
1. **Why Separate Response Models?**
   - Consistent API response format
   - Hide internal implementation details
   - Version API responses independently
   - Auto-generate OpenAPI documentation

2. **Why Include Metadata?**
   - Request tracing (request_id)
   - Performance monitoring (processing_time)
   - Client-side caching (timestamp)
   - Debugging information

3. **Why Envelope Pattern?**
   - Consistent structure across all endpoints
   - Easy to add fields (metadata, pagination, etc.)
   - Clear distinction between data and metadata

Design Patterns:
- Envelope Pattern: Wrap data in metadata
- Data Transfer Object (DTO): Serialize domain objects
- Builder Pattern: Construct responses from domain models
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TaskResponse(BaseModel):
    """
    Response model for a single task.
    
    Represents task state and metadata.
    Includes all information clients need to track task progress.
    
    Attributes:
        task_id: Unique task identifier
        status: Task status (PENDING, STARTED, SUCCESS, FAILURE, RETRY)
        priority: Task priority level
        result: Task result (null until SUCCESS)
        error: Error message (null unless FAILURE)
        created_at: Task creation timestamp
        started_at: Task start timestamp (null if not started)
        completed_at: Task completion timestamp (null if not complete)
        processing_time_ms: Task processing time in milliseconds
    """
    
    task_id: str = Field(
        ...,
        description="Unique task identifier (UUID)",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    
    status: str = Field(
        ...,
        description="Task status",
        example="SUCCESS"
    )
    
    priority: str = Field(
        ...,
        description="Task priority level",
        example="high"
    )
    
    queue: str = Field(
        ...,
        description="Queue name where task is/was processed",
        example="high"
    )
    
    result: Optional[Any] = Field(
        default=None,
        description="Task result (available when status=SUCCESS)",
        example={"total": 10512.50, "calculation_type": "compound_interest"}
    )
    
    error: Optional[str] = Field(
        default=None,
        description="Error message (available when status=FAILURE)",
        example=None
    )
    
    created_at: datetime = Field(
        ...,
        description="Task creation timestamp (UTC)",
        example="2025-10-22T02:30:00Z"
    )
    
    started_at: Optional[datetime] = Field(
        default=None,
        description="Task start timestamp (UTC)",
        example="2025-10-22T02:30:05Z"
    )
    
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Task completion timestamp (UTC)",
        example="2025-10-22T02:30:11Z"
    )
    
    processing_time_ms: Optional[float] = Field(
        default=None,
        description="Task processing time in milliseconds",
        example=6000.0
    )
    
    class Config:
        """Pydantic model configuration."""
        
        schema_extra = {
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "SUCCESS",
                "priority": "high",
                "queue": "high",
                "result": {
                    "total": 10512.50,
                    "calculation_type": "compound_interest"
                },
                "error": None,
                "created_at": "2025-10-22T02:30:00Z",
                "started_at": "2025-10-22T02:30:05Z",
                "completed_at": "2025-10-22T02:30:11Z",
                "processing_time_ms": 6000.0
            }
        }


class TaskCreateResponse(BaseModel):
    """
    Response model for task creation.
    
    Returned when a new task is successfully created and queued.
    Includes minimal information needed to poll for results.
    
    Attributes:
        task_id: Unique task identifier
        status: Initial task status (always PENDING)
        queue: Queue where task was submitted
        message: Human-readable success message
    """
    
    task_id: str = Field(
        ...,
        description="Unique task identifier for polling",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    
    status: str = Field(
        default="PENDING",
        description="Initial task status",
        example="PENDING"
    )
    
    queue: str = Field(
        ...,
        description="Queue where task was submitted",
        example="high"
    )
    
    message: str = Field(
        default="Task created successfully",
        description="Success message",
        example="Task created successfully and queued for processing"
    )
    
    estimated_wait_time_seconds: Optional[int] = Field(
        default=None,
        description="Estimated time until task starts (based on queue depth)",
        example=12
    )
    
    class Config:
        """Pydantic model configuration."""
        
        schema_extra = {
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "PENDING",
                "queue": "high",
                "message": "Task created successfully and queued for processing",
                "estimated_wait_time_seconds": 12
            }
        }


class HealthResponse(BaseModel):
    """
    Response model for health check endpoint.
    
    Used by load balancers and monitoring systems to verify service health.
    Includes system status and dependencies.
    
    Attributes:
        status: Overall health status (healthy, degraded, unhealthy)
        version: API version
        timestamp: Current server time (UTC)
        dependencies: Status of external dependencies
    """
    
    status: str = Field(
        ...,
        description="Overall health status",
        example="healthy"
    )
    
    version: str = Field(
        ...,
        description="API version",
        example="1.0.0"
    )
    
    server_id: str = Field(
        ...,
        description="Server identifier (for multi-server deployments)",
        example="fastapi-1"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Current server time (UTC)",
        example="2025-10-22T02:30:00Z"
    )
    
    dependencies: Dict[str, str] = Field(
        ...,
        description="Status of external dependencies",
        example={
            "redis": "healthy",
            "celery_broker": "healthy",
            "celery_workers": "3 workers online"
        }
    )
    
    queue_stats: Optional[Dict[str, int]] = Field(
        default=None,
        description="Queue statistics",
        example={
            "high": 5,
            "medium": 12,
            "low": 3
        }
    )
    
    class Config:
        """Pydantic model configuration."""
        
        schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "server_id": "fastapi-1",
                "timestamp": "2025-10-22T02:30:00Z",
                "dependencies": {
                    "redis": "healthy",
                    "celery_broker": "healthy",
                    "celery_workers": "3 workers online"
                },
                "queue_stats": {
                    "high": 5,
                    "medium": 12,
                    "low": 3
                }
            }
        }


class ErrorResponse(BaseModel):
    """
    Response model for errors.
    
    Consistent error format across all API endpoints.
    Includes debugging information and recovery guidance.
    
    Attributes:
        code: Machine-readable error code
        message: Human-readable error message
        details: Additional error context
        request_id: Correlation ID for tracing
    """
    
    code: str = Field(
        ...,
        description="Machine-readable error code",
        example="QUEUE_FULL"
    )
    
    message: str = Field(
        ...,
        description="Human-readable error message",
        example="Task queue is at capacity. Please retry later."
    )
    
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional error context",
        example={"current_size": 500, "max_size": 500}
    )
    
    request_id: str = Field(
        ...,
        description="Correlation ID for tracing",
        example="abc123def456"
    )
    
    class Config:
        """Pydantic model configuration."""
        
        schema_extra = {
            "example": {
                "code": "QUEUE_FULL",
                "message": "Task queue is at capacity. Please retry later.",
                "details": {
                    "current_size": 500,
                    "max_size": 500,
                    "retry_after_seconds": 30
                },
                "request_id": "abc123def456"
            }
        }


class PaginatedTasksResponse(BaseModel):
    """
    Response model for paginated task list.
    
    Includes pagination metadata for client-side navigation.
    
    Attributes:
        tasks: List of task responses
        total: Total number of tasks
        limit: Maximum results per page
        offset: Current offset
        has_more: Whether more results exist
    """
    
    tasks: List[TaskResponse] = Field(
        ...,
        description="List of tasks in current page",
    )
    
    total: int = Field(
        ...,
        description="Total number of tasks matching filter",
        example=250
    )
    
    limit: int = Field(
        ...,
        description="Maximum results per page",
        example=100
    )
    
    offset: int = Field(
        ...,
        description="Current offset",
        example=0
    )
    
    has_more: bool = Field(
        ...,
        description="Whether more results exist",
        example=True
    )
    
    class Config:
        """Pydantic model configuration."""
        
        schema_extra = {
            "example": {
                "tasks": [
                    {
                        "task_id": "123e4567-e89b-12d3-a456-426614174000",
                        "status": "SUCCESS",
                        "priority": "high",
                        "queue": "high",
                        "result": {"total": 10512.50},
                        "error": None,
                        "created_at": "2025-10-22T02:30:00Z",
                        "started_at": "2025-10-22T02:30:05Z",
                        "completed_at": "2025-10-22T02:30:11Z",
                        "processing_time_ms": 6000.0
                    }
                ],
                "total": 250,
                "limit": 100,
                "offset": 0,
                "has_more": True
            }
        }
