"""
Reusable Kafka Producer wrapper with JSON serialization support.
"""
import json
import logging
from typing import Any, Optional, Callable
from kafka import KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


class BaseKafkaProducer:
    """Base Kafka Producer with JSON serialization support."""

    def __init__(
        self,
        bootstrap_servers: str | list[str] = "localhost:9092",
        **kwargs,
    ):
        """
        Initialize Kafka Producer.

        Args:
            bootstrap_servers: Kafka broker addresses
            **kwargs: Additional arguments for KafkaProducer
        """
        self.bootstrap_servers = bootstrap_servers
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            **kwargs,
        )
        logger.info(f"Kafka Producer initialized with servers: {bootstrap_servers}")

    def send_message(
        self,
        topic: str,
        value: Any,
        key: Optional[str] = None,
        on_success: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
    ) -> None:
        """
        Send a message to Kafka topic.

        Args:
            topic: Topic name
            value: Message value (will be JSON serialized)
            key: Optional message key for partitioning
            on_success: Optional callback on success
            on_error: Optional callback on error
        """
        try:
            future = self.producer.send(topic, value=value, key=key)

            def handle_success(record_metadata):
                msg = (
                    f"Message sent to topic={record_metadata.topic}, "
                    f"partition={record_metadata.partition}, offset={record_metadata.offset}"
                )
                logger.info(msg)
                if on_success:
                    on_success(record_metadata)

            def handle_error(exc):
                logger.error(f"Error sending message to topic {topic}: {exc}")
                if on_error:
                    on_error(exc)

            future.add_callback(handle_success)
            future.add_errback(handle_error)

        except KafkaError as e:
            logger.error(f"Kafka error while sending message: {e}")
            if on_error:
                on_error(e)
        except Exception as e:
            logger.error(f"Unexpected error while sending message: {e}")
            if on_error:
                on_error(e)

    def flush(self, timeout: int = 10) -> None:
        """
        Ensure all messages are sent.

        Args:
            timeout: Timeout in seconds
        """
        self.producer.flush(timeout)
        logger.info("Producer flushed")

    def close(self) -> None:
        """Close the producer."""
        self.producer.close()
        logger.info("Kafka Producer closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
