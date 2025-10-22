"""
Custom Exception Handling Module

This module provides domain-specific exceptions and error handlers for the task queue system.

Architectural Decisions:
1. **Why Custom Exceptions over HTTPException?**
   - Domain semantics (QueueFullException vs HTTPException(503))
   - Consistent error responses across the API
   - Error tracking and metrics by exception type
   - Business logic validation separate from HTTP layer

2. **Why Structured Error Responses?**
   - Client-friendly error messages
   - Machine-readable error codes for programmatic handling
   - Debugging information (request_id, details)
   - Consistent format across all errors

3. **Why Exception Handlers?**
   - Centralized error handling (DRY principle)
   - Automatic logging of errors
   - Hide internal details in production
   - Add retry-after headers for backpressure

Design Patterns:
- Exception Hierarchy: Base exception with specialized subclasses
- Template Method: Common error handling logic in base class
- Strategy Pattern: Different handlers for different exception types
"""

import logging
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = logging.getLogger("api")


class TaskQueueException(Exception):
    """
    Base exception for all task queue domain errors.
    
    All custom exceptions should inherit from this class.
    Provides consistent interface for error handling.
    
    Attributes:
        message: Human-readable error message
        status_code: HTTP status code
        error_code: Machine-readable error code
        details: Additional error context
    """
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize base exception.
        
        Args:
            message: Error message for users
            status_code: HTTP status code (default 500)
            error_code: Machine-readable code (default INTERNAL_ERROR)
            details: Additional context dictionary
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class QueueFullException(TaskQueueException):
    """
    Raised when task queue has reached maximum capacity.
    
    This implements the circuit breaker pattern:
    - When queue is full, stop accepting new tasks
    - Return 503 (Service Unavailable) with Retry-After header
    - Prevents system overload and cascading failures
    
    Why 503 (not 429)?
    - 429 = Too many requests from client (rate limiting)
    - 503 = Service temporarily unavailable (system overload)
    
    Design Pattern: Circuit Breaker
    """
    
    def __init__(self, current_size: int, max_size: int):
        """
        Initialize queue full exception.
        
        Args:
            current_size: Current number of tasks in queue
            max_size: Maximum allowed queue size
        """
        super().__init__(
            message=f"Task queue is at capacity ({current_size}/{max_size}). System under heavy load. Please retry later.",
            status_code=503,  # Service Unavailable
            error_code="QUEUE_FULL",
            details={
                "current_size": current_size,
                "max_size": max_size,
                "retry_after_seconds": 30,
            },
        )


class TaskNotFoundException(TaskQueueException):
    """
    Raised when requested task ID doesn't exist in the system.
    
    Possible causes:
    - Invalid task ID
    - Task result expired (cleaned up after 7 days)
    - Task was never created
    
    Why 404 (not 400)?
    - 400 = Bad request (client error in request format)
    - 404 = Resource not found (valid request, resource doesn't exist)
    """
    
    def __init__(self, task_id: str):
        """
        Initialize task not found exception.
        
        Args:
            task_id: The task ID that was not found
        """
        super().__init__(
            message=f"Task not found: {task_id}. Task may have expired (7-day retention) or never existed.",
            status_code=404,  # Not Found
            error_code="TASK_NOT_FOUND",
            details={"task_id": task_id},
        )


class InvalidTaskException(TaskQueueException):
    """
    Raised when task parameters fail business validation.
    
    Distinct from Pydantic ValidationError:
    - ValidationError: Type/format errors (caught automatically)
    - InvalidTaskException: Business logic errors (domain-specific)
    
    Examples:
    - Amount must be positive
    - Rate must be between 0 and 1
    - Date must be in the future
    
    Why 400 (not 422)?
    - 422 = Unprocessable Entity (Pydantic validation failures)
    - 400 = Bad Request (business logic validation failures)
    """
    
    def __init__(self, message: str, details: Dict[str, Any]):
        """
        Initialize invalid task exception.
        
        Args:
            message: Description of validation failure
            details: Field-specific validation errors
        """
        super().__init__(
            message=message,
            status_code=400,  # Bad Request
            error_code="INVALID_TASK",
            details=details,
        )


class TaskTimeoutException(TaskQueueException):
    """
    Raised when task execution exceeds time limit.
    
    Task time limits:
    - Soft limit (540s): Raises exception, allows cleanup
    - Hard limit (600s): Kills process immediately
    
    This exception is raised when soft limit is exceeded.
    """
    
    def __init__(self, task_id: str, time_limit: int):
        """
        Initialize task timeout exception.
        
        Args:
            task_id: Task that timed out
            time_limit: Time limit that was exceeded (seconds)
        """
        super().__init__(
            message=f"Task {task_id} exceeded time limit of {time_limit} seconds",
            status_code=504,  # Gateway Timeout
            error_code="TASK_TIMEOUT",
            details={
                "task_id": task_id,
                "time_limit_seconds": time_limit,
            },
        )


class BrokerConnectionException(TaskQueueException):
    """
    Raised when cannot connect to Redis broker.
    
    Possible causes:
    - Redis container not running
    - Network issues
    - Redis auth failure
    - Redis out of memory
    
    Why 503 (not 500)?
    - 503 = Service temporarily unavailable (can retry)
    - 500 = Internal server error (permanent failure)
    """
    
    def __init__(self, error: str):
        """
        Initialize broker connection exception.
        
        Args:
            error: Error message from Redis client
        """
        super().__init__(
            message="Cannot connect to task broker. Service temporarily unavailable.",
            status_code=503,  # Service Unavailable
            error_code="BROKER_CONNECTION_ERROR",
            details={"error": error},
        )


# ============================================================================
# Exception Handlers
# ============================================================================

async def task_queue_exception_handler(
    request: Request,
    exc: TaskQueueException,
) -> JSONResponse:
    """
    Handle custom task queue exceptions.
    
    Converts domain exceptions into consistent HTTP error responses.
    Logs errors for monitoring and debugging.
    
    Args:
        request: FastAPI request object
        exc: Custom exception instance
        
    Returns:
        JSON error response
    """
    # Get correlation ID from request state (set by middleware)
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    
    # Log error with context
    logger.error(
        f"TaskQueueException: {exc.error_code} - {exc.message}",
        extra={
            "request_id": correlation_id,
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=True if exc.status_code >= 500 else False,
    )
    
    # Build error response
    error_response = {
        "error": {
            "code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "request_id": correlation_id,
        }
    }
    
    # Add Retry-After header for 503 responses (backpressure)
    headers = {}
    if exc.status_code == 503:
        retry_after = exc.details.get("retry_after_seconds", 30)
        headers["Retry-After"] = str(retry_after)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
        headers=headers,
    )


async def validation_exception_handler(
    request: Request,
    exc: ValidationError,
) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    
    Converts Pydantic validation errors into user-friendly format.
    
    Args:
        request: FastAPI request object
        exc: Pydantic validation error
        
    Returns:
        JSON error response with field-specific errors
    """
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    
    # Convert Pydantic errors to simplified format
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
        })
    
    logger.warning(
        f"Validation error: {len(errors)} field(s) invalid",
        extra={
            "request_id": correlation_id,
            "validation_errors": errors,
            "path": request.url.path,
        },
    )
    
    return JSONResponse(
        status_code=422,  # Unprocessable Entity
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"validation_errors": errors},
                "request_id": correlation_id,
            }
        },
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Handle unexpected exceptions.
    
    Catches all unhandled exceptions to prevent exposing internal details.
    Logs full stack trace for debugging.
    
    Args:
        request: FastAPI request object
        exc: Any unhandled exception
        
    Returns:
        Generic error response (hides internal details)
    """
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    
    # Log full error details
    logger.critical(
        f"Unhandled exception: {type(exc).__name__} - {str(exc)}",
        extra={
            "request_id": correlation_id,
            "exception_type": type(exc).__name__,
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=True,
    )
    
    # Return generic error (don't expose internal details)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "details": {},
                "request_id": correlation_id,
            }
        },
    )
