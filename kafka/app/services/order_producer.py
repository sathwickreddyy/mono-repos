"""Order producer service for sending orders to Kafka."""
import logging
from typing import Optional
from app.core.kafka_producer import BaseKafkaProducer
from app.models.order import Order

logger = logging.getLogger(__name__)


class OrderProducerService:
    """Service for producing order messages to Kafka."""
    
    ORDERS_TOPIC = "orders"
    
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        """
        Initialize the order producer service.
        
        Args:
            bootstrap_servers: Kafka broker addresses
        """
        self.producer = BaseKafkaProducer(bootstrap_servers=bootstrap_servers)
        logger.info("OrderProducerService initialized")
    
    def send_order(self, order: Order, key: Optional[str] = None) -> None:
        """
        Send an order to the Kafka topic.
        
        Args:
            order: Order object to send
            key: Optional message key (defaults to order_id)
        """
        message_key = key or order.order_id
        order_data = order.to_dict()
        
        logger.info(f"Sending order {order.order_id} to topic {self.ORDERS_TOPIC}")
        
        self.producer.send_message(
            topic=self.ORDERS_TOPIC,
            value=order_data,
            key=message_key,
            on_success=lambda metadata: logger.info(
                f"Order {order.order_id} successfully sent to "
                f"partition {metadata.partition} at offset {metadata.offset}"
            ),
            on_error=lambda exc: logger.error(
                f"Failed to send order {order.order_id}: {exc}"
            )
        )
    
    def flush(self) -> None:
        """Ensure all pending messages are sent."""
        self.producer.flush()
        logger.info("Order producer flushed")
    
    def close(self) -> None:
        """Close the producer."""
        self.producer.close()
        logger.info("Order producer service closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
