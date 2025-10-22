#!/bin/bash
# Baseline Performance Test
# Tests single request latency, throughput under parallel load, and system stats
# This establishes the performance baseline for SLA verification

echo "🧪 Test 1.1: Baseline Performance"
echo "=================================="
echo ""

# Check prerequisites
if ! command -v jq &> /dev/null; then
    echo "❌ Error: jq is required but not installed"
    echo "Install: brew install jq"
    exit 1
fi

if ! command -v bc &> /dev/null; then
    echo "❌ Error: bc is required but not installed"
    echo "Install: brew install bc"
    exit 1
fi

# Check if system is running
if ! curl -s http://localhost/health > /dev/null 2>&1; then
    echo "❌ Error: System not responding on http://localhost"
    echo "Start with: docker-compose up -d"
    exit 1
fi

echo "✅ Prerequisites met, starting test..."
echo ""

# Warm up the system
echo "🔥 Warming up (10 requests)..."
for i in {1..10}; do
    curl -s -X POST http://localhost/api/v1/tasks \
        -H "Content-Type: application/json" \
        -d '{
            "amount": 1000.0,
            "interest_rate": 0.05,
            "years": 10,
            "priority": "medium"
        }' > /dev/null
    
    if [ $((i % 5)) -eq 0 ]; then
        echo "  $i/10 warmup requests sent..."
    fi
done

echo "  Waiting for system to stabilize..."
sleep 5
echo ""

# Measure single request latency
echo "📊 Single Request Latency (10 samples):"
echo "---------------------------------------"

LATENCIES=()
for i in {1..10}; do
    # Measure request time in milliseconds
    START=$(date +%s%N)
    RESPONSE=$(curl -s -X POST http://localhost/api/v1/tasks \
        -H "Content-Type: application/json" \
        -d '{
            "amount": 1000.0,
            "interest_rate": 0.05,
            "years": 10,
            "priority": "medium"
        }')
    END=$(date +%s%N)
    
    # Calculate latency in milliseconds
    LATENCY=$(echo "scale=2; ($END - $START) / 1000000" | bc)
    LATENCIES+=($LATENCY)
    
    TASK_ID=$(echo $RESPONSE | jq -r '.data.task_id' 2>/dev/null || echo "unknown")
    STATUS=$(echo $RESPONSE | jq -r '.data.status' 2>/dev/null || echo "unknown")
    
    echo "  Request $i: ${LATENCY}ms | Task: $TASK_ID | Status: $STATUS"
done

# Calculate average latency
TOTAL=0
for lat in "${LATENCIES[@]}"; do
    TOTAL=$(echo "$TOTAL + $lat" | bc)
done
AVG_LATENCY=$(echo "scale=2; $TOTAL / ${#LATENCIES[@]}" | bc)

echo ""
echo "  Average Latency: ${AVG_LATENCY}ms"
echo "  Target: <100ms"
if (( $(echo "$AVG_LATENCY < 100" | bc -l) )); then
    echo "  ✅ PASS - Within SLA"
else
    echo "  ⚠️  WARN - Above SLA target"
fi
echo ""

# Measure throughput
echo "📊 Throughput Test (100 requests in parallel):"
echo "-----------------------------------------------"

echo "  Launching 100 concurrent requests..."
START=$(date +%s)

# Create temp directory for responses
mkdir -p /tmp/baseline-test
rm -f /tmp/baseline-test/*.json

for i in {1..100}; do
    curl -s -X POST http://localhost/api/v1/tasks \
        -H "Content-Type: application/json" \
        -d '{
            "amount": 1000.0,
            "interest_rate": 0.05,
            "years": 10,
            "priority": "medium"
        }' -o /tmp/baseline-test/response-$i.json &
    
    if [ $((i % 25)) -eq 0 ]; then
        echo "    $i/100 requests launched..."
    fi
done

echo "  Waiting for all requests to complete..."
wait
END=$(date +%s)
DURATION=$((END - START))

echo ""
echo "  All requests completed!"
echo "  Duration: ${DURATION}s"
echo "  Throughput: $(echo "scale=2; 100 / $DURATION" | bc) requests/sec"
echo "  Expected: 10-20 req/sec"
echo ""

# Analyze responses
SUCCESS=$(grep -l '"status":"success"\|"status":"PENDING"\|"status":"queued"' /tmp/baseline-test/*.json 2>/dev/null | wc -l | xargs)
ERRORS=$(grep -l '"error"' /tmp/baseline-test/*.json 2>/dev/null | wc -l | xargs)

echo "  Response Analysis:"
echo "    ✅ Successful: $SUCCESS/100"
echo "    ❌ Errors: $ERRORS/100"
echo ""

# Check system stats
echo "📊 System Health Check:"
echo "----------------------"

HEALTH=$(curl -s http://localhost/api/v1/health)
REDIS_STATUS=$(echo $HEALTH | jq -r '.data.dependencies.redis.status' 2>/dev/null || echo "unknown")
CELERY_STATUS=$(echo $HEALTH | jq -r '.data.dependencies.celery.status' 2>/dev/null || echo "unknown")
QUEUE_DEPTH=$(echo $HEALTH | jq -r '.data.queue_stats.approximate_depth' 2>/dev/null || echo "0")

echo "  Redis: $REDIS_STATUS"
echo "  Celery: $CELERY_STATUS"
echo "  Queue Depth: $QUEUE_DEPTH tasks"
echo ""

# Check which FastAPI servers handled requests
echo "📊 Load Balancing Analysis:"
echo "---------------------------"
echo "  Checking X-Served-By headers (requires curl verbose mode)..."
echo "  Run manually: curl -v http://localhost/api/v1/health | grep 'X-Served-By'"
echo ""

# Cleanup
rm -rf /tmp/baseline-test

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Baseline Performance Test Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Key Metrics:"
echo "  • Single Request Latency: ${AVG_LATENCY}ms (target: <100ms)"
echo "  • Throughput: $(echo "scale=2; 100 / $DURATION" | bc) req/sec (target: 10-20)"
echo "  • Success Rate: ${SUCCESS}% (target: 100%)"
echo "  • Queue Depth: $QUEUE_DEPTH tasks (max: 500)"
echo ""
echo "📖 Observations:"
echo "  1. Check Flower dashboard for task distribution: http://localhost:5555"
echo "  2. Monitor Docker stats: docker stats --no-stream"
echo "  3. Check logs: docker-compose logs -f fastapi-1 celery-worker-1"
echo ""
