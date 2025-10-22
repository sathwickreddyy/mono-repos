# Chaos Engineering Test Suite - Quick Start Guide

## Prerequisites

Before running tests, ensure:

```bash
# 1. Install required tools
brew install jq bc

# 2. Start the system
docker-compose up -d

# 3. Wait for all services to be healthy (30-60 seconds)
docker-compose ps

# 4. Verify system is responding
curl http://localhost/health
```

---

## Running Tests

### Option 1: Run All Tests (Recommended)

```bash
./scripts/run-all-tests.sh
```

**Duration**: 30-45 minutes  
**What it does**: Runs all 7 test suites in sequence with pauses between each test

---

### Option 2: Run Individual Tests

#### 1. Baseline Performance Test

```bash
./scripts/test-baseline.sh
```

-   **Duration**: ~5 minutes
-   **Purpose**: Establish performance baseline
-   **Metrics**: Latency, throughput, success rate

#### 2. Thundering Herd (Spike Load)

```bash
./scripts/test-thundering-herd.sh
```

-   **Duration**: ~2 minutes
-   **Purpose**: Test circuit breaker under 500 concurrent requests
-   **What to watch**: Flower dashboard (http://localhost:5555)

#### 3. Worker Failure (Chaos Monkey)

```bash
./scripts/test-worker-failure.sh
```

-   **Duration**: ~3 minutes
-   **Purpose**: Verify fault tolerance when worker crashes
-   **What happens**: Kills celery-worker-1, then restarts it

#### 4. Redis Failure (Data Layer Outage)

```bash
./scripts/test-redis-failure.sh
```

-   **Duration**: ~2 minutes
-   **Purpose**: Test graceful degradation when Redis crashes
-   **What happens**: Stops Redis, then restarts it

#### 5. Nginx Failure (Load Balancer Outage)

```bash
./scripts/test-nginx-failure.sh
```

-   **Duration**: ~2 minutes
-   **Purpose**: Verify direct API access when LB fails
-   **What happens**: Stops Nginx, tests direct access, restarts

#### 6. Memory Leak Simulation

```bash
./scripts/test-memory-leak.sh
```

-   **Duration**: ~10 minutes
-   **Purpose**: Verify workers restart to prevent memory leaks
-   **What to watch**: `docker stats` in another terminal

#### 7. Security & Input Validation

```bash
./scripts/test-security.sh
```

-   **Duration**: ~3 minutes
-   **Purpose**: Test injection attacks, validation
-   **Tests**: SQL injection, XSS, command injection, etc.

---

## Monitoring During Tests

### Terminal 1: Run Tests

```bash
./scripts/run-all-tests.sh
```

### Terminal 2: Watch Logs

```bash
docker-compose logs -f fastapi-1 celery-worker-1
```

### Terminal 3: Monitor Resources

```bash
watch -n 2 docker stats
```

### Browser: Flower Dashboard

```
http://localhost:5555
```

---

## Understanding Test Results

### ✅ What "PASS" Means

-   **Baseline Performance**: Latency <100ms, throughput 10-20 req/sec
-   **Thundering Herd**: Circuit breaker triggered, 503 responses returned
-   **Worker Failure**: System continued with 2/3 workers, no task loss
-   **Redis Failure**: 503 errors during outage, fast recovery
-   **Nginx Failure**: Direct API access worked, zero downtime
-   **Memory Leak**: Workers restarted after 100 tasks, no OOM kills
-   **Security**: All injection attempts blocked (422 status)

### ⚠️ What to Investigate

-   **High latency** (>100ms): Check CPU usage, slow tasks
-   **Low throughput** (<10 req/sec): Scale workers or optimize code
-   **Task loss**: Check Redis persistence, worker logs
-   **OOM kills**: Reduce concurrency or increase memory limits
-   **Security failures**: Review Pydantic validators

---

## Troubleshooting

### Test Fails: "System not responding"

```bash
# Check if containers are running
docker-compose ps

# Restart if needed
docker-compose restart

# Check logs
docker-compose logs
```

### Test Hangs or Times Out

```bash
# Kill the test
Ctrl+C

# Check queue depth
curl http://localhost/api/v1/health | jq '.data.queue_stats'

# Clear queue if needed
docker-compose restart celery-worker-1 celery-worker-2 celery-worker-3
```

### "jq: command not found"

```bash
brew install jq
```

### "bc: command not found"

```bash
brew install bc
```

---

## After Testing

### 1. Review Results

```bash
# Check test results summary
cat /tmp/chaos-test-results.txt

# View system health
curl http://localhost/api/v1/health | jq '.'
```

### 2. Document Findings

Edit `docs/TEST-REPORT.md` with your actual metrics:

-   Fill in [XX] placeholders with real numbers
-   Add observations and recommendations
-   Sign and date the report

### 3. Check for Issues

```bash
# Check for errors in logs
docker-compose logs | grep -i error

# Check container status
docker-compose ps

# View resource usage
docker stats --no-stream
```

### 4. Clean Up (Optional)

```bash
# Stop all containers
docker-compose down

# Remove test data
rm -f /tmp/chaos-test-results.txt
rm -rf /tmp/baseline-test /tmp/thundering-herd /tmp/chaos-test /tmp/redis-test
```

---

## Best Practices

1. **Run baseline test first** to establish normal performance
2. **Wait between tests** for queue to drain (check Flower)
3. **Monitor multiple terminals** during tests
4. **Take screenshots** of Flower dashboard during spike loads
5. **Document unexpected behavior** in TEST-REPORT.md
6. **Run tests during quiet periods** (low production load)
7. **Have rollback plan** if testing in staging/production

---

## Next Steps

After all tests pass:

1. ✅ **Document Results**: Fill out `docs/TEST-REPORT.md`
2. 🔐 **Add Security**: Implement authentication (JWT)
3. 🔒 **Enable HTTPS**: Configure SSL certificates
4. 📊 **Set Up Monitoring**: Deploy Prometheus + Grafana
5. 🚨 **Configure Alerts**: PagerDuty, Slack notifications
6. 🏗️ **High Availability**: Redis Sentinel, multi-AZ deployment
7. 🚀 **Deploy to Production**: Use CI/CD pipeline

---

## Key Metrics to Track

| Metric        | Target      | Command                               |
| ------------- | ----------- | ------------------------------------- |
| API Latency   | <100ms      | `./scripts/test-baseline.sh`          |
| Throughput    | 10-20 req/s | `./scripts/test-baseline.sh`          |
| Queue Depth   | <500 tasks  | `curl http://localhost/api/v1/health` |
| Worker CPU    | <80%        | `docker stats`                        |
| Worker Memory | <1.5GB      | `docker stats`                        |
| Success Rate  | >99%        | Check test outputs                    |
| Recovery Time | <10s        | Individual failure tests              |

---

## Questions?

-   **How long should tests run?** 30-45 minutes for full suite
-   **Can I run in production?** Start with staging; use blue-green deployment
-   **What if a test fails?** Check logs, adjust configuration, re-run
-   **Do tests affect real data?** No, tasks are synthetic test data
-   **Can I customize tests?** Yes, edit scripts to adjust parameters

---

**Ready to validate your production-ready system? Run:**

```bash
./scripts/run-all-tests.sh
```

Good luck! 🚀
