"""Health check and status routes."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    message: str
    service: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status of the application
    """
    return HealthResponse(
        status="healthy",
        message="Order processing system is running",
        service="kafka-order-processor"
    )


@router.get("/")
async def root():
    """
    Root endpoint.
    
    Returns:
        Welcome message
    """
    return {
        "message": "Kafka Order Processing System",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }
