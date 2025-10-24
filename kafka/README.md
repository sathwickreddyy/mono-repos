# Kafka Order Processing System

A FastAPI-based order processing system demonstrating Kafka producer-consumer pattern with reusable components.

## Features

-   ✅ Reusable Kafka Producer and Consumer classes
-   ✅ FastAPI REST API for order management
-   ✅ Docker Compose setup for Kafka and Zookeeper
-   ✅ Persistent storage for Kafka data
-   ✅ Pydantic models for data validation
-   ✅ Async consumer running in background
-   ✅ Comprehensive logging
-   ✅ Kafka UI for monitoring

## Project Structure

```
kafka/
├── app/
│   ├── api/                    # FastAPI routes
│   │   ├── health.py          # Health check endpoints
│   │   └── orders.py          # Order management endpoints
│   ├── consumers/             # Kafka consumers
│   │   └── order_consumer.py # Order processing consumer
│   ├── core/                  # Core reusable components
│   │   ├── kafka_producer.py # Reusable Kafka producer
│   │   └── kafka_consumer.py # Reusable Kafka consumer
│   ├── models/                # Data models
│   │   └── order.py          # Order Pydantic model
│   ├── services/              # Business logic services
│   │   └── order_producer.py # Order producer service
│   └── main.py               # FastAPI application entry point
├── docker-compose.yml        # Kafka infrastructure
└── requirements.txt          # Python dependencies
```

## Prerequisites

-   Python 3.12+
-   Docker and Docker Compose
-   8GB RAM recommended for Kafka

## Setup Instructions

### 1. Create Docker mount directory

```bash
mkdir -p /Users/sathwick/my-office/docker-mounts/kafka/zookeeper/{data,log}
mkdir -p /Users/sathwick/my-office/docker-mounts/kafka/broker/data
```

### 2. Start Kafka infrastructure

```bash
docker-compose up -d
```

Wait for services to be healthy (~30 seconds):

```bash
docker-compose ps
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the FastAPI application

```bash
cd app
python main.py
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Usage

### API Endpoints

-   **API Documentation**: http://localhost:8000/docs
-   **Health Check**: http://localhost:8000/api/health
-   **Kafka UI**: http://localhost:8080

### Create a Single Order

```bash
curl -X POST "http://localhost:8000/api/orders/" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "ORD-001",
    "customer_id": "CUST-123",
    "product_id": "PROD-456",
    "quantity": 2,
    "price": 29.99,
    "status": "pending"
  }'
```

### Create Bulk Orders

```bash
curl -X POST "http://localhost:8000/api/orders/bulk" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "order_id": "ORD-001",
      "customer_id": "CUST-123",
      "product_id": "PROD-456",
      "quantity": 2,
      "price": 29.99
    },
    {
      "order_id": "ORD-002",
      "customer_id": "CUST-124",
      "product_id": "PROD-457",
      "quantity": 1,
      "price": 49.99
    }
  ]'
```

### Monitor Orders

Check the application logs to see orders being processed:

-   Producer logs show orders being sent to Kafka
-   Consumer logs show orders being received and processed

## Reusable Components

### BaseKafkaProducer

Located in `app/core/kafka_producer.py`:

```python
from app.core.kafka_producer import BaseKafkaProducer

producer = BaseKafkaProducer(bootstrap_servers="localhost:9092")
producer.send_message(
    topic="my-topic",
    value={"key": "value"},
    key="message-key"
)
producer.flush()
producer.close()
```

### BaseKafkaConsumer

Located in `app/core/kafka_consumer.py`:

```python
from app.core.kafka_consumer import BaseKafkaConsumer

def handle_message(message: dict):
    print(f"Received: {message}")

consumer = BaseKafkaConsumer(
    topics=["my-topic"],
    group_id="my-group",
    bootstrap_servers="localhost:9092"
)

# Synchronous consumption
consumer.consume_messages(message_handler=handle_message)

# Or async consumption
consumer.start_async(message_handler=handle_message)
```

## Architecture

### Producer-Consumer Flow

1. **REST API** receives order via POST request
2. **OrderProducerService** sends order to Kafka topic `orders`
3. **OrderConsumerService** (running in background) consumes from `orders` topic
4. Consumer processes and logs the order details

### Key Concepts Demonstrated

-   ✅ **Topics**: Single `orders` topic for order messages
-   ✅ **Producers**: Sending JSON-serialized orders to Kafka
-   ✅ **Consumers**: Consuming and deserializing orders from Kafka
-   ✅ **Consumer Groups**: Orders processed by `order-processing-group`
-   ✅ **Serialization/Deserialization**: Automatic JSON encoding/decoding
-   ✅ **Async Processing**: Background consumer thread
-   ✅ **Error Handling**: Comprehensive logging and error management

## Configuration

### Kafka Configuration

Edit `docker-compose.yml` to customize:

-   Ports (default: 9092 for Kafka, 2181 for Zookeeper)
-   Retention periods
-   Replication factors
-   Storage paths

### Application Configuration

Edit `app/main.py` to customize:

-   Kafka bootstrap servers
-   Consumer group IDs
-   Topic names
-   Logging levels

## Monitoring

### Kafka UI

Access Kafka UI at http://localhost:8080 to:

-   View topics and partitions
-   Monitor consumer groups
-   Inspect messages
-   Check consumer lag

### Application Logs

The application provides detailed logging:

-   📦 Order received events
-   ✅ Successful processing
-   ❌ Error messages with stack traces

## Troubleshooting

### Kafka not starting

```bash
# Check Kafka logs
docker-compose logs kafka

# Restart services
docker-compose down
docker-compose up -d
```

### Consumer not receiving messages

1. Check if topic exists in Kafka UI
2. Verify Kafka is running: `docker-compose ps`
3. Check application logs for connection errors

### Import errors

```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## Cleanup

### Stop services

```bash
# Stop FastAPI app (Ctrl+C)

# Stop Kafka infrastructure
docker-compose down

# Remove volumes (data will be lost)
docker-compose down -v
```

## Next Steps

Potential enhancements:

-   Add order status updates
-   Implement dead letter queues
-   Add metrics and monitoring (Prometheus)
-   Implement order validation logic
-   Add database persistence
-   Create additional topics for notifications
-   Add Kafka Streams for complex processing

## License

MIT
