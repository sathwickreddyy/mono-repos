# Phase 2: Infrastructure Setup - Quick Reference

## 🎯 What We Built

Production-grade Docker infrastructure for distributed task processing with **8 containerized services**, **3 isolated networks**, and **production-ready configurations**.

---

## 📁 File Summary

| File                       | Lines | Purpose               | Key Patterns                               |
| -------------------------- | ----- | --------------------- | ------------------------------------------ |
| `docker-compose.yml`       | 430+  | Service orchestration | Circuit breaker, bulkhead, health checks   |
| `nginx/nginx.conf`         | 230+  | Load balancer         | Least-conn, rate limiting, request tracing |
| `fastapi-app/Dockerfile`   | 70+   | API container         | Multi-stage build, non-root user           |
| `celery-worker/Dockerfile` | 70+   | Worker container      | CPU-optimized, numerical libs              |
| `redis/redis.conf`         | 200+  | Persistence tuning    | AOF, noeviction policy                     |

---

## 🏗️ Architecture at a Glance

```
USER REQUEST
    ↓
┌─────────────────┐
│  Nginx (Port 80) │  ← Rate limiting: 10 req/s
│  Load Balancer   │  ← Circuit breaker: max_fails=3
└────────┬────────┘
         ↓ (least_conn algorithm)
    ┌────┴────┬────────┐
    ↓         ↓        ↓
┌────────┐ ┌────────┐ ┌────────┐
│FastAPI1│ │FastAPI2│ │FastAPI3│  ← Stateless API servers
│ 512MB  │ │ 512MB  │ │ 512MB  │  ← Health checks every 30s
└────┬───┘ └───┬────┘ └────┬───┘
     └─────┬───┴─────┬──────┘
           ↓         ↓
       ┌───────────────┐
       │ Redis (1GB)   │  ← AOF persistence enabled
       │ Broker + DB   │  ← 7-day result retention
       └───┬───┬───┬───┘
           ↓   ↓   ↓
    ┌──────┴───┴───┴──────┐
    ↓          ↓          ↓
┌─────────┐ ┌─────────┐ ┌─────────┐
│Worker 1 │ │Worker 2 │ │Worker 3 │  ← CPU-intensive tasks
│  2GB    │ │  2GB    │ │  2GB    │  ← 4 concurrent each
│ 2 CPUs  │ │ 2 CPUs  │ │ 2 CPUs  │  ← Priority queues
└─────────┘ └─────────┘ └─────────┘
     └──────────┬──────────┘
                ↓
         ┌─────────────┐
         │   Flower    │  ← Monitoring dashboard
         │   256MB     │  ← http://localhost:5555
         └─────────────┘
```

---

## 🔑 Key Design Decisions

### 1. Load Balancing: **least_conn** (not round-robin)

```nginx
# Problem: 5-6s tasks + round-robin = unbalanced load
# Solution: Route to server with fewest active connections
upstream fastapi_backend {
    least_conn;
    server fastapi-1:8000;
}
```

### 2. Worker Configuration: **prefetch_multiplier=1** (not 4)

```yaml
# Problem: Default prefetch causes task hoarding
# Solution: Fair distribution with single-task prefetch
command: celery worker --prefetch-multiplier=1
```

### 3. Redis Persistence: **AOF everysec** (not RDB)

```conf
# Problem: Financial calculations can't afford data loss
# Solution: AOF logs every write, 1s loss window acceptable
appendonly yes
appendfsync everysec
```

### 4. Memory Policy: **noeviction** (not allkeys-lru)

```conf
# Problem: Cache eviction would drop tasks silently
# Solution: Fail fast when queue full (circuit breaker)
maxmemory-policy noeviction
```

### 5. Docker Images: **Multi-stage build** (not single-stage)

```dockerfile
# Problem: Build tools add 1GB+ to production image
# Solution: Builder stage (1.2GB) → Runtime stage (180MB)
FROM python:3.11-slim as builder
# ... install gcc, compile wheels ...
FROM python:3.11-slim
# ... copy wheels, no build tools
```

---

## 📊 Resource Allocation

| Service   | Replicas | Memory | CPU  | Total Memory | Total CPU    |
| --------- | -------- | ------ | ---- | ------------ | ------------ |
| Redis     | 1        | 1GB    | 0.5  | 1GB          | 0.5          |
| FastAPI   | 3        | 512MB  | 0.5  | 1.5GB        | 1.5          |
| Workers   | 3        | 2GB    | 2.0  | 6GB          | 6.0          |
| Nginx     | 1        | 256MB  | 0.5  | 256MB        | 0.5          |
| Flower    | 1        | 256MB  | 0.25 | 256MB        | 0.25         |
| **TOTAL** | **9**    |        |      | **~9GB**     | **~9 cores** |

**System Requirements**: 16GB RAM, 12+ CPU cores (macOS M4 Pro ✅)

---

## ⚡ Performance Targets

```
Throughput Calculation:
  Workers: 3
  Concurrency: 4 tasks/worker
  Parallel capacity: 12 tasks
  Task duration: 6 seconds

  Throughput = 12 / 6 = 2 tasks/second
  Daily capacity = 172,800 tasks/day
  Monthly capacity = 5.2M tasks/month
```

**Scaling Options:**

-   **Vertical**: Increase concurrency (4 → 8) = 4 tasks/sec
-   **Horizontal**: Add workers (3 → 6) = 4 tasks/sec
-   **Combined**: 6 workers × 8 concurrency = 8 tasks/sec

---

## 🔒 Security Hardening

| Layer       | Security Measure  | Protection Against       |
| ----------- | ----------------- | ------------------------ |
| Container   | Non-root user     | Container escape attacks |
| Network     | Isolated networks | Lateral movement         |
| Resource    | Memory/CPU limits | Resource exhaustion DoS  |
| Application | Rate limiting     | API abuse, DDoS          |
| Data        | AOF persistence   | Data loss from crashes   |

---

## 🧪 Testing the Infrastructure

### 1. Build and Start

```bash
cd /Users/sathwick/IdeaProjects/mono-repos/task-queue-cpu-intesive
docker-compose up --build -d
```

### 2. Verify Health

```bash
# Check all containers running
docker-compose ps

# Check health status
docker-compose ps | grep "healthy"

# View logs
docker-compose logs -f redis
docker-compose logs -f fastapi-1
docker-compose logs -f celery-worker-1
```

### 3. Test Endpoints

```bash
# Nginx health check
curl http://localhost/health

# FastAPI direct access
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health

# Flower monitoring
open http://localhost:5555
```

### 4. Chaos Testing

```bash
# Kill a worker, verify others continue
docker stop celery-worker-2
docker-compose logs -f celery-worker-1  # Should still process tasks

# Kill API server, verify load balancer routes around it
docker stop fastapi-server-2
curl http://localhost/health  # Should still respond (via server 1 or 3)

# Restart failed services
docker-compose up -d
```

---

## 🐛 Troubleshooting

### Redis Connection Refused

```bash
# Check Redis is running
docker-compose ps redis

# Check Redis logs
docker-compose logs redis

# Test connection
docker exec -it redis-broker redis-cli ping
# Expected: PONG
```

### Workers Not Picking Up Tasks

```bash
# Check worker logs
docker-compose logs celery-worker-1

# Inspect Celery workers
docker exec -it celery-worker-1 celery -A tasks inspect active

# Check Redis queue
docker exec -it redis-broker redis-cli LLEN celery
# Expected: 0 (empty queue)
```

### Nginx 502 Bad Gateway

```bash
# Check FastAPI servers are healthy
docker-compose ps | grep fastapi

# Check upstream status
docker exec -it nginx-loadbalancer cat /var/log/nginx/error.log

# Verify network connectivity
docker exec -it nginx-loadbalancer wget -O- http://fastapi-1:8000/health
```

---

## 📈 Monitoring Metrics

### Key Metrics to Track

1. **Latency**

    - API response time: `<50ms` target
    - Task processing time: `5-6s` expected
    - Queue wait time: `<100ms` target

2. **Throughput**

    - Tasks/second: `2 tasks/sec` baseline
    - Queue consumption rate
    - Failed tasks/total tasks ratio

3. **Resource Usage**

    - Redis memory usage: Monitor via `INFO memory`
    - Worker CPU usage: Should be ~100% during tasks
    - Queue depth: Alert if >500 tasks

4. **Availability**
    - Health check success rate: >99.9%
    - Container restart count
    - Upstream server failures

### Flower Dashboard

-   **URL**: http://localhost:5555
-   **Features**:
    -   Active tasks view
    -   Worker status
    -   Task history (last 7 days with your config)
    -   Queue depth graphs
    -   Success/failure rates

---

## 🎓 Architectural Patterns Used

1. **Microservices Architecture**: Independent, scalable services
2. **Circuit Breaker**: Fail fast when dependencies down
3. **Bulkhead Pattern**: Resource isolation prevents cascade failures
4. **Competing Consumers**: Multiple workers for horizontal scaling
5. **Queue-Based Load Leveling**: Buffer traffic spikes
6. **Health Check Pattern**: Automatic failure detection
7. **Gateway Aggregation**: Nginx as single entry point
8. **Retry Pattern**: Nginx retries failed upstreams

---

## ✅ Validation Checklist

Before moving to Phase 3, verify:

-   [ ] All 9 containers start successfully
-   [ ] Health checks pass (green in `docker ps`)
-   [ ] Redis persistence enabled (check redis-data/ has AOF files)
-   [ ] Nginx routes to all 3 FastAPI servers
-   [ ] Workers connect to Redis broker
-   [ ] Flower dashboard accessible
-   [ ] Volume mounts created on host
-   [ ] Logs rotating properly (check max-size)
-   [ ] No OOM kills in `docker stats`
-   [ ] Network isolation working (workers can't reach internet)

---

## 🚀 Ready for Phase 3!

**Infrastructure**: ✅ Complete  
**Next Step**: Build FastAPI application and Celery tasks

**Preview of Phase 3:**

-   `/tasks` POST endpoint (submit calculations)
-   `/tasks/{id}` GET endpoint (check status)
-   Celery task for financial calculations (5-6s CPU work)
-   Priority queue routing (high/medium/low)
-   Structured logging with correlation IDs
-   Integration tests
