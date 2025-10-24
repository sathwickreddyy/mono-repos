#!/usr/bin/env python3
"""
Sample script to send test orders to Kafka.
"""
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.order import Order, OrderStatus
from app.services.order_producer import OrderProducerService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


def main():
    """Send sample orders to Kafka."""
    logger.info("Starting order producer...")
    
    try:
        producer = OrderProducerService(bootstrap_servers="localhost:9092")
        
        # Create sample orders
        orders = [
            Order(
                order_id="ORD-001",
                customer_id="CUST-123",
                product_id="PROD-456",
                quantity=2,
                price=29.99,
                status=OrderStatus.PENDING
            ),
            Order(
                order_id="ORD-002",
                customer_id="CUST-124",
                product_id="PROD-457",
                quantity=1,
                price=49.99,
                status=OrderStatus.PENDING
            ),
            Order(
                order_id="ORD-003",
                customer_id="CUST-125",
                product_id="PROD-458",
                quantity=5,
                price=9.99,
                status=OrderStatus.PENDING
            ),
        ]
        
        # Send orders
        for order in orders:
            logger.info(f"Sending order: {order.order_id}")
            producer.send_order(order)
        
        producer.flush()
        logger.info(f"Successfully sent {len(orders)} orders to Kafka")
        
        producer.close()
        
    except Exception as e:
        logger.error(f"Error sending orders: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
