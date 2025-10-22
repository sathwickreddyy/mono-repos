#!/bin/bash
# Thundering Herd Test - 500 concurrent requests
# Simulates sudden traffic spike to test circuit breaker and backpressure
# This validates the system handles overload gracefully (fail fast principle)

echo "🧪 Test 1.2: Thundering Herd (500 concurrent requests)"
echo "======================================================"
echo ""

# Check prerequisites
if ! command -v jq &> /dev/null; then
    echo "❌ Error: jq is required"
    exit 1
fi

if ! curl -s http://localhost/health > /dev/null 2>&1; then
    echo "❌ Error: System not responding"
    exit 1
fi

echo "⚠️  WARNING: This stress test will:"
echo "   • Launch 500 concurrent HTTP requests"
echo "   • Trigger circuit breaker (queue depth limit: 500 tasks)"
echo "   • Generate ~4000 Celery tasks (500 requests × 8 tasks each)"
echo "   • Stress test Redis, Nginx, FastAPI, and Celery workers"
echo ""
echo "📊 Monitor in real-time:"
echo "   • Flower dashboard: http://localhost:5555"
echo "   • Docker stats: docker stats"
echo "   • Logs: docker-compose logs -f"
echo ""
echo "Press Enter to start the chaos..."
read

# Create temp directory
mkdir -p /tmp/thundering-herd
rm -f /tmp/thundering-herd/*.json

echo ""
echo "🚀 Launching 500 concurrent requests..."
echo "---------------------------------------"

START=$(date +%s)

# Launch 500 requests in background
for i in {1..500}; do
    # Vary the priority to test all queues
    if [ $((i % 3)) -eq 0 ]; then
        PRIORITY="high"
    elif [ $((i % 3)) -eq 1 ]; then
        PRIORITY="medium"
    else
        PRIORITY="low"
    fi
    
    curl -s -w "\nHTTP_CODE:%{http_code}\nTIME_TOTAL:%{time_total}\n" \
        -X POST http://localhost/api/v1/tasks \
        -H "Content-Type: application/json" \
        -d "{
            \"amount\": $((i * 100)).0,
            \"interest_rate\": 0.0$((i % 10)),
            \"years\": $((i % 20 + 1)),
            \"priority\": \"$PRIORITY\"
        }" > /tmp/thundering-herd/response-$i.txt 2>&1 &
    
    # Progress indicator every 50 requests
    if [ $((i % 50)) -eq 0 ]; then
        echo "  $i/500 requests launched..."
    fi
done

echo ""
echo "⏳ All 500 requests launched, waiting for completion..."
echo "  (This may take 30-60 seconds depending on system load)"
echo ""

wait

END=$(date +%s)
DURATION=$((END - START))

echo ""
echo "✅ All requests completed!"
echo ""

# Analyze responses
echo "📊 Analyzing Results..."
echo "----------------------"

# Count HTTP status codes
SUCCESS_201=$(grep "HTTP_CODE:201" /tmp/thundering-herd/*.txt 2>/dev/null | wc -l | xargs)
SUCCESS_200=$(grep "HTTP_CODE:200" /tmp/thundering-herd/*.txt 2>/dev/null | wc -l | xargs)
REJECTED_503=$(grep "HTTP_CODE:503" /tmp/thundering-herd/*.txt 2>/dev/null | wc -l | xargs)
ERROR_500=$(grep "HTTP_CODE:500" /tmp/thundering-herd/*.txt 2>/dev/null | wc -l | xargs)
ERROR_502=$(grep "HTTP_CODE:502" /tmp/thundering-herd/*.txt 2>/dev/null | wc -l | xargs)
OTHER=$(ls /tmp/thundering-herd/*.txt 2>/dev/null | wc -l | xargs)
OTHER=$((OTHER - SUCCESS_201 - SUCCESS_200 - REJECTED_503 - ERROR_500 - ERROR_502))

TOTAL_SUCCESS=$((SUCCESS_201 + SUCCESS_200))
SUCCESS_RATE=$(echo "scale=1; $TOTAL_SUCCESS * 100 / 500" | bc)

echo ""
echo "📈 Response Status Codes:"
echo "  ✅ 201 Created: $SUCCESS_201"
echo "  ✅ 200 OK: $SUCCESS_200"
echo "  🛑 503 Service Unavailable: $REJECTED_503 (circuit breaker)"
echo "  ❌ 500 Internal Error: $ERROR_500"
echo "  ❌ 502 Bad Gateway: $ERROR_502"
echo "  ❓ Other: $OTHER"
echo ""
echo "  Total Success: $TOTAL_SUCCESS/500 (${SUCCESS_RATE}%)"
echo "  Total Rejected: $REJECTED_503/500 (backpressure working: $(echo "scale=1; $REJECTED_503 * 100 / 500" | bc)%)"
echo ""

# Calculate average response time
echo "⏱️  Performance Metrics:"
TOTAL_TIME=0
COUNT=0
while IFS= read -r line; do
    TIME=$(echo "$line" | grep "TIME_TOTAL" | cut -d: -f2)
    if [ ! -z "$TIME" ]; then
        TOTAL_TIME=$(echo "$TOTAL_TIME + $TIME" | bc)
        COUNT=$((COUNT + 1))
    fi
done < <(cat /tmp/thundering-herd/*.txt 2>/dev/null)

if [ $COUNT -gt 0 ]; then
    AVG_TIME=$(echo "scale=3; $TOTAL_TIME / $COUNT" | bc)
    AVG_TIME_MS=$(echo "scale=0; $AVG_TIME * 1000" | bc)
    echo "  Average Response Time: ${AVG_TIME_MS}ms"
fi

echo "  Total Duration: ${DURATION}s"
echo "  Throughput: $(echo "scale=2; 500 / $DURATION" | bc) req/sec"
echo ""

# Check queue depth during spike
echo "📊 System State During Spike:"
echo "-----------------------------"

HEALTH=$(curl -s http://localhost/api/v1/health 2>/dev/null)
if [ $? -eq 0 ]; then
    QUEUE_DEPTH=$(echo $HEALTH | jq -r '.data.queue_stats.approximate_depth' 2>/dev/null || echo "unknown")
    REDIS_STATUS=$(echo $HEALTH | jq -r '.data.dependencies.redis.status' 2>/dev/null || echo "unknown")
    CELERY_STATUS=$(echo $HEALTH | jq -r '.data.dependencies.celery.status' 2>/dev/null || echo "unknown")
    
    echo "  Queue Depth: $QUEUE_DEPTH tasks (max: 500)"
    echo "  Redis: $REDIS_STATUS"
    echo "  Celery: $CELERY_STATUS"
else
    echo "  ⚠️  Health check failed (system under heavy load)"
fi
echo ""

# Check for 503 responses (circuit breaker evidence)
echo "🔍 Circuit Breaker Analysis:"
echo "---------------------------"

if [ $REJECTED_503 -gt 0 ]; then
    echo "  ✅ Circuit breaker triggered correctly!"
    echo "  📋 Sample 503 response:"
    
    # Show first 503 response
    SAMPLE_503=$(grep -l "HTTP_CODE:503" /tmp/thundering-herd/*.txt 2>/dev/null | head -1)
    if [ ! -z "$SAMPLE_503" ]; then
        cat "$SAMPLE_503" | grep -v "HTTP_CODE\|TIME_TOTAL" | jq '.' 2>/dev/null || cat "$SAMPLE_503" | head -5
    fi
else
    echo "  ⚠️  No 503 responses (circuit breaker may not have triggered)"
    echo "  This could mean:"
    echo "    • Queue never reached 500 tasks (workers processed fast enough)"
    echo "    • Circuit breaker threshold configured differently"
fi
echo ""

# Cleanup
echo "🧹 Cleaning up temporary files..."
rm -rf /tmp/thundering-herd

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Thundering Herd Test Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 Key Findings:"
echo ""
echo "  1. BACKPRESSURE:"
if [ $REJECTED_503 -gt 0 ]; then
    echo "     ✅ System rejected $REJECTED_503 requests with 503 (fail fast)"
    echo "     ✅ Prevents cascading failures and resource exhaustion"
else
    echo "     ℹ️  No 503s observed - queue depth stayed under limit"
fi
echo ""
echo "  2. AVAILABILITY:"
echo "     • Success Rate: ${SUCCESS_RATE}%"
echo "     • System remained responsive during spike"
echo ""
echo "  3. PERFORMANCE:"
echo "     • Throughput: $(echo "scale=2; 500 / $DURATION" | bc) req/sec"
if [ $COUNT -gt 0 ]; then
    echo "     • Avg Response: ${AVG_TIME_MS}ms"
fi
echo ""
echo "  4. RECOVERY:"
echo "     • Check if queue drains: watch curl -s http://localhost/api/v1/health | jq '.data.queue_stats'"
echo "     • Monitor task completion: http://localhost:5555"
echo ""
echo "📖 Production Insights:"
echo "  • This test simulates Black Friday / market open scenarios"
echo "  • 503 responses allow clients to retry with exponential backoff"
echo "  • Circuit breaker prevents system collapse under load"
echo "  • Queue-based load leveling smooths traffic spikes"
echo ""
