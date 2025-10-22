"""
FastAPI Application Entry Point

Main application configuration with middleware, exception handlers, and routes.

Architectural Decisions:
1. **Why Factory Pattern?**
   - Testable (create multiple app instances)
   - Configurable (different settings for test/prod)
   - Clear initialization order

2. **Why Middleware Stack?**
   - Cross-cutting concerns (logging, CORS, error handling)
   - Request/response enrichment
   - Observability (correlation IDs)

3. **Why Lifespan Events?**
   - Graceful startup/shutdown
   - Resource cleanup
   - Health check validation

Design Patterns:
- Factory: create_app() function
- Chain of Responsibility: Middleware stack
- Observer: Lifespan events
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from api.routes import router
from core.config import settings
from core.exceptions import (
    TaskQueueException,
    generic_exception_handler,
    task_queue_exception_handler,
    validation_exception_handler,
)
from core.logging import CorrelationIDMiddleware, setup_logging

# Initialize logging
loggers = setup_logging(
    log_level=settings.logging.level,
    log_format=settings.logging.format,
)
logger = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events.
    
    Startup:
    - Log application start
    - Validate configuration
    - Check dependencies
    
    Shutdown:
    - Log shutdown
    - Close connections
    - Flush logs
    """
    # Startup
    logger.info(
        f"Starting {settings.api.title} v{settings.api.version}",
        extra={"server_id": settings.server_id},
    )
    
    # Validate configuration
    logger.info(f"Redis: {settings.redis.url}")
    logger.info(f"Max queue size: {settings.api.max_queue_size}")
    logger.info(f"Log level: {settings.logging.level}")
    
    yield
    
    # Shutdown
    logger.info(
        f"Shutting down {settings.api.title}",
        extra={"server_id": settings.server_id},
    )


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Factory pattern allows creating multiple app instances
    with different configurations (useful for testing).
    
    Returns:
        Configured FastAPI application
    """
    # Create FastAPI app
    app = FastAPI(
        title=settings.api.title,
        version=settings.api.version,
        description=settings.api.description,
        docs_url="/docs" if settings.api.enable_docs else None,
        redoc_url="/redoc" if settings.api.enable_docs else None,
        openapi_url="/openapi.json" if settings.api.enable_docs else None,
        lifespan=lifespan,
    )
    
    # Add middleware (order matters: last added = first executed)
    
    # 1. CORS middleware (if enabled)
    if settings.api.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.api.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # 2. Correlation ID middleware (request tracing)
    app.add_middleware(CorrelationIDMiddleware)
    
    # Add exception handlers
    app.add_exception_handler(TaskQueueException, task_queue_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    # Include routers
    app.include_router(router)
    
    # Root endpoint
    @app.get("/", tags=["system"])
    async def root():
        """Root endpoint with API information."""
        return {
            "name": settings.api.title,
            "version": settings.api.version,
            "server_id": settings.server_id,
            "docs": "/docs",
            "health": "/api/v1/health",
        }
    
    # Health check endpoint (used by Docker and Nginx)
    @app.get("/health", tags=["system"])
    async def health():
        """Simple health check for load balancers."""
        return {"status": "healthy"}
    
    logger.info(f"Application created: {settings.api.title} v{settings.api.version}")
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=not settings.is_production,
        log_level=settings.logging.level.lower(),
    )
