#!/usr/bin/env python3
"""
Standalone script to run the order consumer independently.
Useful for testing or running consumer separately from the API.
"""
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.consumers.order_consumer import OrderConsumerService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


def main():
    """Run the order consumer."""
    logger.info("Starting standalone order consumer...")
    
    try:
        consumer = OrderConsumerService(bootstrap_servers="localhost:9092")
        consumer.start_consuming()
    except KeyboardInterrupt:
        logger.info("Consumer stopped by user")
    except Exception as e:
        logger.error(f"Error running consumer: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
