# Architecture Design Document

## System Overview

This is a horizontally scalable, distributed task processing system built on microservices principles.

### Core Components

1. **API Layer (FastAPI)**: Stateless HTTP API servers
2. **Message Broker (Redis)**: Reliable message queue with persistence
3. **Worker Layer (Celery)**: Horizontally scalable compute workers
4. **Load Balancer (Nginx)**: Request distribution and health checks
5. **Monitoring (Flower)**: Observability and metrics dashboard

### Architectural Patterns Used

1. **Microservices Architecture**: Each component is independently scalable
2. **Queue-Based Load Leveling**: Buffers requests during traffic spikes
3. **Competing Consumers**: Multiple workers process tasks in parallel
4. **Circuit Breaker**: Backpressure mechanism prevents system overload
5. **Health Check Pattern**: Each service exposes /health endpoint
6. **Strangler Fig Pattern**: Can migrate from monolith incrementally

### Design Principles

#### 1. Separation of Concerns

-   **API servers**: Only handle HTTP, validation, and task submission
-   **Workers**: Only handle computation (no HTTP dependencies)
-   **Redis**: Only handles message passing and result storage
-   **Nginx**: Only handles routing and load distribution

#### 2. Statelessness

-   API servers have no local state (can scale horizontally)
-   Workers are ephemeral (can be killed and restarted)
-   All state stored in Redis (single source of truth)

#### 3. Fault Tolerance

-   Multiple API servers (survives individual crashes)
-   Multiple workers (survives worker failures)
-   Redis persistence (survives restarts)
-   Nginx health checks (routes around failed servers)

#### 4. Observability

-   Structured logging with correlation IDs
-   Metrics exposed via Flower dashboard
-   Request tracing via X-Request-ID headers
-   Health check endpoints for monitoring

### Trade-offs & Alternatives

#### Current Design: Redis as Broker

**Pros:**

-   Simple setup (single container)
-   Fast (in-memory operations)
-   Built-in persistence with AOF

**Cons:**

-   Single point of failure (no clustering in this setup)
-   Limited message size (512MB max)
-   In-memory means RAM constraints

**Alternatives:**

-   RabbitMQ: Better for complex routing, message persistence
-   AWS SQS: Fully managed, auto-scaling, but vendor lock-in
-   Kafka: Better for event streaming, but overkill for task queue

#### Current Design: Nginx Load Balancer

**Pros:**

-   Lightweight and fast
-   Simple configuration
-   Well-tested in production

**Cons:**

-   No auto-scaling of backends
-   Manual health check configuration

**Alternatives:**

-   HAProxy: More advanced load balancing algorithms
-   AWS ALB: Managed, auto-scales, but AWS-specific
-   Traefik: Dynamic configuration, but more complex

### Scaling Strategy

#### Vertical Scaling (Scale Up)

-   Increase worker concurrency: `--concurrency=8`
-   Increase CPU/RAM per container
-   Limit: Single machine constraints

#### Horizontal Scaling (Scale Out)

-   Add more worker containers: `docker-compose scale celery-worker=10`
-   Add more API servers
-   Limit: Redis connection limit, network bandwidth

### Production Considerations

1. **Security**

    - Add authentication (JWT tokens)
    - Encrypt Redis connections (TLS)
    - Network segmentation (API servers in DMZ, workers in private subnet)

2. **Reliability**

    - Redis clustering (Redis Sentinel or Cluster mode)
    - Multiple availability zones
    - Automated failover

3. **Performance**

    - Connection pooling (Redis, database)
    - Caching layer (Redis for results)
    - CDN for static assets

4. **Monitoring**
    - Prometheus + Grafana for metrics
    - ELK stack for log aggregation
    - Sentry for error tracking
    - New Relic/Datadog for APM

## Request Flow

```
User Request
    ↓
Nginx (Load Balancer)
    ↓ (least_conn algorithm)
FastAPI Server (1, 2, or 3)
    ↓ (validates request)
    ↓ (generates task ID)
    ↓ (enqueues to Redis)
Redis Broker (queue: celery)
    ↓ (worker pulls task)
Celery Worker (1, 2, or 3)
    ↓ (executes CPU work)
    ↓ (stores result)
Redis Backend (key: celery-task-meta-{task_id})
    ↑ (API polls for result)
FastAPI Server
    ↓
User Response
```

## Failure Scenarios & Recovery

### Scenario 1: API Server Crash

-   **Detection**: Nginx health checks fail
-   **Response**: Nginx routes traffic to healthy servers
-   **Recovery**: Restart container, Nginx auto-detects

### Scenario 2: Worker Crash

-   **Detection**: Task stuck in 'PENDING' state
-   **Response**: Other workers continue processing queue
-   **Recovery**: Restart worker, picks up new tasks

### Scenario 3: Redis Crash

-   **Detection**: Workers can't connect to broker
-   **Response**: System stops accepting tasks (HTTP 503)
-   **Recovery**: Restart Redis, workers reconnect

### Scenario 4: Nginx Crash

-   **Detection**: Port 80 not responding
-   **Response**: Direct API access still works (bypass LB)
-   **Recovery**: Restart Nginx

## Performance Targets

| Metric                 | Target           | Current |
| ---------------------- | ---------------- | ------- |
| API Response Time      | <50ms            | TBD     |
| Task Queue Latency     | <100ms           | TBD     |
| Task Processing Time   | 5-6s             | TBD     |
| Throughput (tasks/sec) | 12 (3×4 workers) | TBD     |
| Queue Depth (max)      | 500 tasks        | 500     |
| Uptime SLA             | 99.9%            | TBD     |

## Cost Analysis (AWS)

| Component     | Instance Type | Monthly Cost |
| ------------- | ------------- | ------------ |
| Nginx + Redis | t3.medium     | $30          |
| FastAPI × 3   | t3.small      | $45          |
| Workers × 3   | c6i.2xlarge   | $900         |
| **Total**     |               | **$975**     |

## Next Steps

1. Implement circuit breaker pattern for Redis failures
2. Add request tracing with OpenTelemetry
3. Implement task retry logic with exponential backoff
4. Add rate limiting per user/API key
5. Implement task prioritization (high/medium/low)
