"""
Examples demonstrating how to use the reusable Kafka components.
"""
import logging
import time
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Example 1: Basic Producer Usage
# ============================================================================

def example_basic_producer():
    """Example of basic producer usage."""
    from app.core.kafka_producer import BaseKafkaProducer
    
    print("\n" + "="*70)
    print("Example 1: Basic Producer Usage")
    print("="*70)
    
    # Create producer
    producer = BaseKafkaProducer(bootstrap_servers="localhost:9092")
    
    # Send a simple message
    producer.send_message(
        topic="test-topic",
        value={"message": "Hello Kafka!", "timestamp": time.time()},
        key="msg-1"
    )
    
    # Flush to ensure delivery
    producer.flush()
    
    # Clean up
    producer.close()
    
    print("✅ Message sent successfully!")


# ============================================================================
# Example 2: Producer with Context Manager
# ============================================================================

def example_producer_context_manager():
    """Example of producer with context manager."""
    from app.core.kafka_producer import BaseKafkaProducer
    
    print("\n" + "="*70)
    print("Example 2: Producer with Context Manager")
    print("="*70)
    
    # Using context manager (automatic cleanup)
    with BaseKafkaProducer(bootstrap_servers="localhost:9092") as producer:
        for i in range(5):
            producer.send_message(
                topic="test-topic",
                value={"message": f"Message {i}", "index": i},
                key=f"msg-{i}"
            )
        producer.flush()
    
    print("✅ 5 messages sent successfully!")


# ============================================================================
# Example 3: Producer with Callbacks
# ============================================================================

def example_producer_with_callbacks():
    """Example of producer with success/error callbacks."""
    from app.core.kafka_producer import BaseKafkaProducer
    
    print("\n" + "="*70)
    print("Example 3: Producer with Callbacks")
    print("="*70)
    
    success_count = [0]  # Using list to modify in closure
    error_count = [0]
    
    def on_success(metadata):
        success_count[0] += 1
        logger.info(f"✅ Success #{success_count[0]}: {metadata.topic}[{metadata.partition}]@{metadata.offset}")
    
    def on_error(exc):
        error_count[0] += 1
        logger.error(f"❌ Error #{error_count[0]}: {exc}")
    
    with BaseKafkaProducer(bootstrap_servers="localhost:9092") as producer:
        producer.send_message(
            topic="test-topic",
            value={"status": "processing"},
            key="callback-test",
            on_success=on_success,
            on_error=on_error
        )
        producer.flush()
    
    print(f"✅ Sent with {success_count[0]} successes and {error_count[0]} errors")


# ============================================================================
# Example 4: Basic Consumer Usage
# ============================================================================

def example_basic_consumer():
    """Example of basic consumer usage."""
    from app.core.kafka_consumer import BaseKafkaConsumer
    
    print("\n" + "="*70)
    print("Example 4: Basic Consumer Usage (will consume 5 messages)")
    print("="*70)
    
    def handle_message(message: Dict[Any, Any]):
        logger.info(f"📨 Received: {message}")
    
    with BaseKafkaConsumer(
        topics=["test-topic"],
        group_id="example-group",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="earliest"
    ) as consumer:
        # Consume only 5 messages
        consumer.consume_messages(
            message_handler=handle_message,
            max_messages=5
        )
    
    print("✅ Consumed 5 messages successfully!")


# ============================================================================
# Example 5: Async Consumer Usage
# ============================================================================

def example_async_consumer():
    """Example of async consumer usage."""
    from app.core.kafka_consumer import BaseKafkaConsumer
    
    print("\n" + "="*70)
    print("Example 5: Async Consumer Usage (runs for 10 seconds)")
    print("="*70)
    
    message_count = [0]
    
    def handle_message(message: Dict[Any, Any]):
        message_count[0] += 1
        logger.info(f"📨 Message #{message_count[0]}: {message}")
    
    consumer = BaseKafkaConsumer(
        topics=["test-topic"],
        group_id="async-example-group",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="latest"  # Only new messages
    )
    
    # Start consuming in background
    thread = consumer.start_async(message_handler=handle_message)
    
    # Let it run for 10 seconds
    print("Consumer running in background... (will stop after 10 seconds)")
    time.sleep(10)
    
    # Stop consumer
    consumer.stop_async()
    consumer.close()
    
    print(f"✅ Consumed {message_count[0]} messages in background!")


# ============================================================================
# Example 6: Custom Service - User Events
# ============================================================================

def example_custom_service():
    """Example of creating a custom service using the reusable components."""
    from app.core.kafka_producer import BaseKafkaProducer
    from app.core.kafka_consumer import BaseKafkaConsumer
    from datetime import datetime
    
    print("\n" + "="*70)
    print("Example 6: Custom User Event Service")
    print("="*70)
    
    class UserEventService:
        """Custom service for user events."""
        
        TOPIC = "user-events"
        
        def __init__(self):
            self.producer = BaseKafkaProducer(bootstrap_servers="localhost:9092")
        
        def track_login(self, user_id: str, ip_address: str):
            """Track user login event."""
            event = {
                "event_type": "login",
                "user_id": user_id,
                "ip_address": ip_address,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.producer.send_message(self.TOPIC, value=event, key=user_id)
            logger.info(f"👤 Tracked login for user {user_id}")
        
        def track_purchase(self, user_id: str, amount: float):
            """Track purchase event."""
            event = {
                "event_type": "purchase",
                "user_id": user_id,
                "amount": amount,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.producer.send_message(self.TOPIC, value=event, key=user_id)
            logger.info(f"💰 Tracked purchase for user {user_id}: ${amount}")
        
        def close(self):
            self.producer.close()
    
    # Use the custom service
    service = UserEventService()
    service.track_login("user123", "192.168.1.1")
    service.track_purchase("user123", 99.99)
    service.producer.flush()
    service.close()
    
    print("✅ User events tracked successfully!")


# ============================================================================
# Example 7: Multi-Topic Consumer
# ============================================================================

def example_multi_topic_consumer():
    """Example of consuming from multiple topics."""
    from app.core.kafka_consumer import BaseKafkaConsumer
    
    print("\n" + "="*70)
    print("Example 7: Multi-Topic Consumer")
    print("="*70)
    
    def handle_message(message: Dict[Any, Any]):
        logger.info(f"📨 Multi-topic message: {message}")
    
    with BaseKafkaConsumer(
        topics=["test-topic", "user-events", "orders"],
        group_id="multi-topic-group",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="earliest"
    ) as consumer:
        consumer.consume_messages(
            message_handler=handle_message,
            max_messages=10
        )
    
    print("✅ Consumed from multiple topics!")


# ============================================================================
# Main function to run examples
# ============================================================================

def main():
    """Run all examples."""
    examples = [
        ("Basic Producer", example_basic_producer),
        ("Producer Context Manager", example_producer_context_manager),
        ("Producer with Callbacks", example_producer_with_callbacks),
        # Consumer examples require messages in the topics
        # Uncomment after running producer examples
        # ("Basic Consumer", example_basic_consumer),
        # ("Async Consumer", example_async_consumer),
        ("Custom Service", example_custom_service),
        # ("Multi-Topic Consumer", example_multi_topic_consumer),
    ]
    
    print("\n" + "🚀 REUSABLE KAFKA COMPONENTS - EXAMPLES")
    print("="*70)
    print("Make sure Kafka is running: docker-compose up -d")
    print("="*70)
    
    for name, example_func in examples:
        try:
            example_func()
            time.sleep(1)  # Small delay between examples
        except Exception as e:
            logger.error(f"❌ Error in {name}: {e}", exc_info=True)
    
    print("\n" + "="*70)
    print("✅ All examples completed!")
    print("="*70)


if __name__ == "__main__":
    main()
