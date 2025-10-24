"""API routes for order management."""
import logging
from typing import List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.models.order import Order
from app.services.order_producer import OrderProducerService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/orders", tags=["orders"])

# Global producer instance (will be initialized in main.py)
order_producer: OrderProducerService | None = None


class OrderResponse(BaseModel):
    """Response model for order creation."""
    success: bool
    message: str
    order_id: str


class BulkOrderResponse(BaseModel):
    """Response model for bulk order creation."""
    success: bool
    message: str
    total_orders: int
    order_ids: List[str]


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order: Order):
    """
    Create a new order and send it to Kafka.
    
    Args:
        order: Order details
        
    Returns:
        OrderResponse with success status and order ID
    """
    try:
        if not order_producer:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Order producer service is not available"
            )
        
        logger.info(f"Received order creation request: {order.order_id}")
        
        # Send order to Kafka
        order_producer.send_order(order)
        order_producer.flush()
        
        return OrderResponse(
            success=True,
            message=f"Order {order.order_id} has been submitted for processing",
            order_id=order.order_id
        )
        
    except Exception as e:
        logger.error(f"Error creating order: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}"
        )


@router.post("/bulk", response_model=BulkOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_bulk_orders(orders: List[Order]):
    """
    Create multiple orders in bulk and send them to Kafka.
    
    Args:
        orders: List of order details
        
    Returns:
        BulkOrderResponse with success status and order IDs
    """
    try:
        if not order_producer:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Order producer service is not available"
            )
        
        if not orders:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one order is required"
            )
        
        logger.info(f"Received bulk order creation request: {len(orders)} orders")
        
        order_ids = []
        for order in orders:
            order_producer.send_order(order)
            order_ids.append(order.order_id)
        
        order_producer.flush()
        
        return BulkOrderResponse(
            success=True,
            message=f"{len(orders)} orders have been submitted for processing",
            total_orders=len(orders),
            order_ids=order_ids
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating bulk orders: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create bulk orders: {str(e)}"
        )


def set_order_producer(producer: OrderProducerService):
    """Set the global order producer instance."""
    global order_producer
    order_producer = producer
