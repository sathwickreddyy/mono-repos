"""Order consumer service for processing orders from Kafka."""
import logging
from app.core.kafka_consumer import BaseKafkaConsumer
from app.models.order import Order

logger = logging.getLogger(__name__)


class OrderConsumerService:
    """Service for consuming and processing order messages from Kafka."""
    
    ORDERS_TOPIC = "orders"
    CONSUMER_GROUP = "order-processing-group"
    
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        """
        Initialize the order consumer service.
        
        Args:
            bootstrap_servers: Kafka broker addresses
        """
        self.consumer = BaseKafkaConsumer(
            topics=[self.ORDERS_TOPIC],
            group_id=self.CONSUMER_GROUP,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset="earliest"
        )
        logger.info("OrderConsumerService initialized")
    
    def process_order(self, order_data: dict) -> None:
        """
        Process an order message.
        
        Args:
            order_data: Order data from Kafka
        """
        try:
            # Deserialize the order
            order = Order.from_dict(order_data)
            
            # Log the received order
            logger.info(
                f"📦 Received Order: ID={order.order_id}, "
                f"Customer={order.customer_id}, "
                f"Product={order.product_id}, "
                f"Quantity={order.quantity}, "
                f"Price=${order.price:.2f}, "
                f"Total=${order.total_amount:.2f}, "
                f"Status={order.status.value}"
            )
            
            # Here you would typically:
            # 1. Validate the order
            # 2. Update inventory
            # 3. Process payment
            # 4. Update order status
            # 5. Send notifications
            # For this demo, we just log it
            
            logger.info(f"✅ Successfully processed order {order.order_id}")
            
        except Exception as e:
            logger.error(f"❌ Error processing order: {e}", exc_info=True)
    
    def start_consuming(self) -> None:
        """Start consuming messages synchronously (blocking)."""
        logger.info(f"Starting to consume orders from topic: {self.ORDERS_TOPIC}")
        self.consumer.consume_messages(
            message_handler=self.process_order
        )
    
    def start_consuming_async(self):
        """Start consuming messages asynchronously (non-blocking)."""
        logger.info(f"Starting async consumer for topic: {self.ORDERS_TOPIC}")
        return self.consumer.start_async(
            message_handler=self.process_order,
            daemon=True
        )
    
    def stop_async(self) -> None:
        """Stop the async consumer."""
        self.consumer.stop_async()
        logger.info("Order consumer stopped")
    
    def close(self) -> None:
        """Close the consumer."""
        self.consumer.close()
        logger.info("Order consumer service closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
