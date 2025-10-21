# Distributed Task Processing System

A production-grade, horizontally scalable distributed task processing system for CPU-intensive financial calculations built with FastAPI, Celery, Redis, and Nginx.

## 🏗️ Architecture Overview

This system implements a microservices architecture with:

-   **FastAPI** - Stateless HTTP API servers (3 replicas)
-   **Celery** - Distributed task workers (3 replicas, 4 concurrent tasks each)
-   **Redis** - Message broker and result backend
-   **Nginx** - Load balancer with health checks
-   **Flower** - Real-time monitoring dashboard

**Throughput**: ~12 tasks/second (3 workers × 4 concurrent tasks ÷ 6s per task)

## 📋 Prerequisites

-   Docker & Docker Compose
-   Python 3.11+
-   8GB RAM minimum (16GB recommended)

## 🚀 Quick Start

1. **Clone and navigate to the project**

    ```bash
    cd task-queue-cpu-intesive
    ```

2. **Create environment file**

    ```bash
    cp .env.example .env
    # Edit .env with your configuration
    ```

3. **Start all services**

    ```bash
    docker-compose up -d
    ```

4. **Verify services are running**

    ```bash
    docker-compose ps
    ```

5. **Access the system**
    - API: http://localhost (load balanced)
    - API Docs: http://localhost/docs
    - Flower Dashboard: http://localhost:5555
    - Individual API servers: :8001, :8002, :8003

## 📖 Documentation

-   **[Architecture Design](./README-ARCHITECTURE.md)** - System design, patterns, and trade-offs
-   **[API Documentation](./docs/api.md)** - Endpoint specifications (coming in Phase 3)
-   **[Deployment Guide](./docs/deployment.md)** - Production deployment (coming in Phase 5)

## 🔧 Development

### Project Structure

```
task-queue-cpu-intesive/
├── fastapi-app/          # API server code
├── celery-worker/        # Worker code and task definitions
├── nginx/                # Load balancer configuration
├── docs/                 # Additional documentation
├── scripts/              # Utility scripts
├── docker-compose.yml    # Service orchestration (Phase 2)
└── .env                  # Environment configuration
```

### Running Locally

**Option 1: Full Docker Stack** (Recommended)

```bash
docker-compose up --build
```

**Option 2: Local Development** (For debugging)

```bash
# Terminal 1: Start Redis
docker run -p 6379:6379 redis:7-alpine

# Terminal 2: Start API
cd fastapi-app
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 3: Start Worker
cd celery-worker
pip install -r requirements.txt
celery -A tasks worker --loglevel=info --concurrency=4
```

## 📊 Monitoring

Access Flower dashboard at http://localhost:5555

-   Default credentials: `admin:secret123` (change in `.env`)
-   View active tasks, worker status, and metrics

## 🧪 Testing

```bash
# Submit a task
curl -X POST http://localhost/tasks \
  -H "Content-Type: application/json" \
  -d '{"data": {"amount": 10000, "rate": 0.05}}'

# Check task status
curl http://localhost/tasks/{task_id}
```

## 📈 Scaling

**Scale workers horizontally:**

```bash
docker-compose up -d --scale celery-worker=5
```

**Scale API servers:**

```bash
docker-compose up -d --scale fastapi-server=5
# Update nginx/nginx.conf with new upstream servers
```

## 🔒 Production Considerations

Before deploying to production:

1. Change `FLOWER_BASIC_AUTH` in `.env`
2. Enable Redis persistence (see `docker-compose.yml`)
3. Configure TLS/SSL for Nginx
4. Set up monitoring (Prometheus/Grafana)
5. Implement authentication (JWT)
6. Review resource limits in `docker-compose.yml`

## 🐛 Troubleshooting

**Redis connection refused:**

```bash
docker-compose logs redis
```

**Worker not picking up tasks:**

```bash
docker-compose logs celery-worker
```

**API health check failing:**

```bash
curl http://localhost:8001/health
```

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

This is a learning project. PRs welcome!

---

**Status**: Phase 1 Complete ✅  
**Next**: Phase 2 - Docker Infrastructure
