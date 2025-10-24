"""
Reusable Kafka Consumer wrapper with JSON deserialization support.
"""
import json
import logging
from typing import Any, Callable, Optional
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import threading

logger = logging.getLogger(__name__)


class BaseKafkaConsumer:
    """Base Kafka Consumer with JSON deserialization support."""

    def __init__(
        self,
        topics: list[str],
        group_id: str,
        bootstrap_servers: str | list[str] = "localhost:9092",
        auto_offset_reset: str = "earliest",
        **kwargs,
    ):
        """
        Initialize Kafka Consumer.

        Args:
            topics: List of topics to subscribe to
            group_id: Consumer group ID
            bootstrap_servers: Kafka broker addresses
            auto_offset_reset: Where to start reading (earliest, latest)
            **kwargs: Additional arguments for KafkaConsumer
        """
        self.topics = topics
        self.group_id = group_id
        self.bootstrap_servers = bootstrap_servers
        self.consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            **kwargs,
        )
        self._running = False
        self._thread: Optional[threading.Thread] = None
        logger.info(
            f"Kafka Consumer initialized for topics: {topics}, "
            f"group_id: {group_id}, servers: {bootstrap_servers}"
        )

    def consume_messages(
        self,
        message_handler: Callable[[dict], None],
        timeout_ms: int = 1000,
        max_messages: Optional[int] = None,
    ) -> None:
        """
        Consume messages from Kafka topics (blocking).

        Args:
            message_handler: Callback function to handle each message
            timeout_ms: Poll timeout in milliseconds
            max_messages: Maximum messages to consume (None = infinite)
        """
        message_count = 0
        try:
            logger.info(f"Starting to consume messages from topics: {self.topics}")
            for message in self.consumer:
                try:
                    logger.info(
                        f"Received message from topic={message.topic}, "
                        f"partition={message.partition}, offset={message.offset}"
                    )
                    message_handler(message.value)
                    message_count += 1

                    if max_messages and message_count >= max_messages:
                        logger.info(f"Reached max messages limit: {max_messages}")
                        break

                except Exception as e:
                    logger.error(f"Error handling message: {e}")

        except KafkaError as e:
            logger.error(f"Kafka error while consuming messages: {e}")
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error in consumer: {e}")
        finally:
            self.close()

    def start_async(
        self,
        message_handler: Callable[[dict], None],
        daemon: bool = True,
    ) -> threading.Thread:
        """
        Start consuming messages in a background thread.

        Args:
            message_handler: Callback function to handle each message
            daemon: Whether thread should be a daemon thread

        Returns:
            The consumer thread
        """
        self._running = True
        self._thread = threading.Thread(
            target=self.consume_messages,
            args=(message_handler,),
            daemon=daemon,
        )
        self._thread.start()
        logger.info("Consumer started in background thread")
        return self._thread

    def stop_async(self, timeout: Optional[int] = 5) -> None:
        """
        Stop the async consumer thread.

        Args:
            timeout: Timeout for thread join in seconds
        """
        if self._thread and self._thread.is_alive():
            self._running = False
            self._thread.join(timeout=timeout)
            logger.info("Consumer async thread stopped")

    def close(self) -> None:
        """Close the consumer."""
        self.consumer.close()
        logger.info("Kafka Consumer closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
