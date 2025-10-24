# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Start Kafka

```bash
cd /Users/sathwick/IdeaProjects/mono-repos/kafka
docker-compose up -d
```

Wait ~30 seconds, then verify:

```bash
docker-compose ps
```

All services should be "Up" and "healthy".

### Step 2: Start FastAPI Application

```bash
cd /Users/sathwick/IdeaProjects/mono-repos/kafka
/Users/sathwick/IdeaProjects/mono-repos/kafka/.venv/bin/python app/main.py
```

You should see:

```
🚀 Starting Order Processing System...
✅ Kafka producer initialized
✅ Kafka consumer started in background
🎉 Order Processing System started successfully!
```

### Step 3: Send Test Orders

**Option A: Using the test script**

```bash
/Users/sathwick/IdeaProjects/mono-repos/kafka/.venv/bin/python scripts/send_test_orders.py
```

**Option B: Using curl**

```bash
curl -X POST "http://localhost:8000/api/orders/" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "ORD-001",
    "customer_id": "CUST-123",
    "product_id": "PROD-456",
    "quantity": 2,
    "price": 29.99
  }'
```

**Option C: Using the interactive API docs**

1. Open http://localhost:8000/docs
2. Click "POST /api/orders/"
3. Click "Try it out"
4. Modify the example JSON
5. Click "Execute"

## 📊 Monitoring

-   **API Docs**: http://localhost:8000/docs
-   **Health Check**: http://localhost:8000/api/health
-   **Kafka UI**: http://localhost:8080

## 🛠️ Useful Commands

### Check Docker Services

```bash
docker-compose ps
docker-compose logs -f kafka
docker-compose logs -f zookeeper
```

### Restart Kafka

```bash
docker-compose restart kafka
```

### Stop Everything

```bash
# Stop FastAPI (Ctrl+C in the terminal)
docker-compose down
```

### Clean Up Completely

```bash
docker-compose down -v  # Removes volumes (data will be lost!)
```

## 📝 Order JSON Format

```json
{
    "order_id": "ORD-001",
    "customer_id": "CUST-123",
    "product_id": "PROD-456",
    "quantity": 2,
    "price": 29.99,
    "status": "pending"
}
```

## 🔍 What to Look For

When you send an order, watch the application logs for:

1. **Producer logs** (sending order):

    ```
    Sending order ORD-001 to topic orders
    Message sent to topic=orders, partition=0, offset=0
    ```

2. **Consumer logs** (receiving order):
    ```
    📦 Received Order: ID=ORD-001, Customer=CUST-123, ...
    ✅ Successfully processed order ORD-001
    ```

## ⚡ Troubleshooting

**Problem**: Connection refused to Kafka

-   **Solution**: Make sure Docker containers are running: `docker-compose ps`

**Problem**: Module not found errors

-   **Solution**: Install dependencies: `pip install -r requirements.txt`

**Problem**: Consumer not processing messages

-   **Solution**: Check Kafka UI (http://localhost:8080) to verify topic exists and has messages

**Problem**: Port already in use (8000, 9092, 8080)

-   **Solution**: Stop other applications using these ports or change ports in config files
