"""
Structured Logging Module

This module provides production-ready logging with:
- Structured JSON output for log aggregation tools
- Correlation IDs for distributed tracing
- Request/response logging with performance metrics
- Separate loggers for different concerns

Architectural Decisions:
1. **Why Structured (JSON) Logging?**
   - Machine-parseable by ELK, Splunk, CloudWatch
   - Searchable by any field (request_id, user_id, etc.)
   - Aggregatable for metrics and dashboards
   
2. **Why Correlation IDs?**
   - Trace requests across API → Workers → Database
   - Debug distributed systems effectively
   - Performance analysis (find slow requests)
   
3. **Why Middleware for Logging?**
   - Centralized request/response logging
   - Automatic performance metrics
   - No manual logging in each route

Design Patterns:
- Middleware Pattern: Cross-cutting concerns
- Decorator Pattern: Enrich log records
- Observer Pattern: Multiple handlers per logger
"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class JSONFormatter(logging.Formatter):
    """
    Format log records as JSON for structured logging.
    
    Converts Python log records to JSON format suitable for:
    - Log aggregation tools (ELK, Splunk, CloudWatch)
    - Metrics extraction (Prometheus, Grafana)
    - Distributed tracing (Jaeger, Zipkin)
    
    Why JSON over plain text?
    - Searchable by any field without regex
    - No parsing errors from multi-line exceptions
    - Direct ingestion into NoSQL databases
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON.
        
        Args:
            record: Python logging record
            
        Returns:
            JSON string with log data
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add correlation ID if present (set by middleware)
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        # Add user ID if present (set by auth middleware)
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        # Add server ID for multi-server deployments
        if hasattr(record, "server_id"):
            log_data["server_id"] = record.server_id
        
        # Add performance metrics if present
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }
        
        # Add extra fields (anything passed via extra={} in logging calls)
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName", "relativeCreated",
                "thread", "threadName", "exc_info", "exc_text", "stack_info",
                "request_id", "user_id", "server_id", "duration_ms", "status_code"
            ]:
                log_data[key] = value
        
        return json.dumps(log_data)


class PrettyFormatter(logging.Formatter):
    """
    Human-readable log formatter for development.
    
    Use in local development for better readability.
    Switch to JSONFormatter in production.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record for human readability."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        # Build base message
        message = f"{timestamp} | {record.levelname:8} | {record.name:15} | {record.getMessage()}"
        
        # Add request ID if present
        if hasattr(record, "request_id"):
            message = f"[{record.request_id[:8]}] {message}"
        
        # Add exception if present
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"
        
        return message


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add correlation IDs to all HTTP requests.
    
    Correlation IDs enable:
    - Tracing requests across multiple services
    - Debugging distributed systems
    - Performance analysis (identify slow requests)
    
    The correlation ID:
    - Is extracted from X-Request-ID header (if provided)
    - Is generated as UUID v4 if not provided
    - Is added to request.state for access in routes
    - Is added to response headers for client-side tracing
    - Is included in all log messages via LoggerAdapter
    
    Design Pattern: Chain of Responsibility
    - Request flows through middleware chain
    - Each middleware enriches request/response
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process HTTP request with correlation ID tracking.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler
            
        Returns:
            HTTP response with correlation ID header
        """
        # Get or generate correlation ID
        correlation_id = request.headers.get(
            "X-Request-ID",
            str(uuid.uuid4())
        )
        
        # Add to request state for access in routes
        request.state.correlation_id = correlation_id
        
        # Get logger
        logger = logging.getLogger("api")
        
        # Log request start
        start_time = time.time()
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else None,
            },
        )
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as exc:
            # Log unexpected exceptions
            duration = time.time() - start_time
            logger.error(
                f"Request failed with exception: {exc}",
                extra={
                    "request_id": correlation_id,
                    "duration_ms": round(duration * 1000, 2),
                    "exception_type": type(exc).__name__,
                },
                exc_info=True,
            )
            raise
        
        # Calculate request duration
        duration = time.time() - start_time
        
        # Log request completion
        logger.info(
            f"Request completed: {response.status_code} in {duration:.3f}s",
            extra={
                "request_id": correlation_id,
                "duration_ms": round(duration * 1000, 2),
                "status_code": response.status_code,
                "method": request.method,
                "path": request.url.path,
            },
        )
        
        # Add correlation ID to response headers
        response.headers["X-Request-ID"] = correlation_id
        
        # Add performance header (for client-side monitoring)
        response.headers["X-Response-Time"] = f"{round(duration * 1000, 2)}ms"
        
        return response


def setup_logging(log_level: str = "INFO", log_format: str = "json") -> dict:
    """
    Configure application logging.
    
    Sets up:
    - Root logger with specified level
    - Formatters (JSON or Pretty)
    - Console handler with rotation
    - Named loggers for different components
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format ("json" for production, "pretty" for development)
        
    Returns:
        Dictionary of configured loggers
        
    Usage:
        >>> loggers = setup_logging(log_level="INFO", log_format="json")
        >>> loggers["api"].info("API started")
    """
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers (avoid duplicate logs)
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Set formatter based on environment
    if log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = PrettyFormatter()
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    
    # Create named loggers for different concerns
    loggers = {
        "api": logging.getLogger("api"),
        "celery": logging.getLogger("celery"),
        "database": logging.getLogger("database"),
        "security": logging.getLogger("security"),
    }
    
    # Set levels for specific loggers (override root level if needed)
    loggers["api"].setLevel(log_level)
    loggers["celery"].setLevel(log_level)
    loggers["database"].setLevel(logging.WARNING)  # Less verbose for DB queries
    loggers["security"].setLevel(logging.INFO)  # Always log security events
    
    return loggers


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger instance.
    
    Args:
        name: Logger name (e.g., "api", "celery", "database")
        
    Returns:
        Configured logger instance
        
    Usage:
        >>> logger = get_logger("api")
        >>> logger.info("Hello world", extra={"request_id": "123"})
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter to automatically include correlation ID.
    
    Simplifies logging by automatically adding request_id to all log calls.
    
    Usage:
        >>> logger = LoggerAdapter(logging.getLogger("api"), {"request_id": "123"})
        >>> logger.info("Message")  # Automatically includes request_id
    """
    
    def process(self, msg: str, kwargs: dict) -> tuple:
        """
        Process log message and add extra fields.
        
        Args:
            msg: Log message
            kwargs: Keyword arguments
            
        Returns:
            Tuple of (message, kwargs with extra fields)
        """
        # Merge adapter's extra fields with call-specific extra fields
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs
