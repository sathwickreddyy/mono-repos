"""Main FastAPI application with Kafka integration."""
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import orders_router, health_router
from app.api.orders import set_order_producer
from app.services.order_producer import OrderProducerService
from app.consumers.order_consumer import OrderConsumerService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Global instances
order_producer: OrderProducerService | None = None
order_consumer: OrderConsumerService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    This handles:
    - Starting Kafka producer and consumer on startup
    - Gracefully shutting down on application exit
    """
    global order_producer, order_consumer
    
    # Startup
    logger.info("🚀 Starting Order Processing System...")
    
    try:
        # Initialize Kafka producer
        logger.info("Initializing Kafka producer...")
        order_producer = OrderProducerService(bootstrap_servers="localhost:9092")
        set_order_producer(order_producer)
        logger.info("✅ Kafka producer initialized")
        
        # Initialize and start Kafka consumer in background
        logger.info("Initializing Kafka consumer...")
        order_consumer = OrderConsumerService(bootstrap_servers="localhost:9092")
        order_consumer.start_consuming_async()
        logger.info("✅ Kafka consumer started in background")
        
        logger.info("🎉 Order Processing System started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Kafka services: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Order Processing System...")
    
    if order_consumer:
        try:
            order_consumer.stop_async()
            order_consumer.close()
            logger.info("✅ Kafka consumer stopped")
        except Exception as e:
            logger.error(f"Error stopping consumer: {e}")
    
    if order_producer:
        try:
            order_producer.close()
            logger.info("✅ Kafka producer closed")
        except Exception as e:
            logger.error(f"Error closing producer: {e}")
    
    logger.info("👋 Order Processing System shut down successfully")


# Create FastAPI application
app = FastAPI(
    title="Kafka Order Processing System",
    description="A FastAPI application demonstrating Kafka producer-consumer pattern with order processing",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(orders_router)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
