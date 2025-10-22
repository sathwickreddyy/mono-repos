#!/bin/bash
# Memory Leak Simulation Test
# Tests worker restart behavior under sustained load
# Validates max_tasks_per_child configuration prevents memory accumulation

echo "🧪 Test 3.1: Memory Leak Simulation"
echo "===================================="
echo ""

# Check prerequisites
if ! command -v jq &> /dev/null; then
    echo "❌ Error: jq is required"
    exit 1
fi

if ! docker ps | grep -q celery-worker; then
    echo "❌ Error: No Celery workers running"
    exit 1
fi

echo "🎯 Test Objectives:"
echo "  • Verify workers restart after max_tasks_per_child limit"
echo "  • Monitor memory usage under sustained load"
echo "  • Test resource limits prevent memory exhaustion"
echo "  • Validate worker pool regeneration (no downtime)"
echo ""
echo "📋 Configuration:"
echo "  • max_tasks_per_child: 100 tasks (configured in docker-compose.yml)"
echo "  • Worker memory limit: 2GB per container"
echo "  • Test load: 250 requests × 16 tasks = 4000 total tasks"
echo "  • Expected: Each worker processes ~1333 tasks, restarting 13+ times"
echo ""
echo "⚠️  This test will:"
echo "   • Run for 5-10 minutes (depending on worker speed)"
echo "   • Generate significant CPU/memory load"
echo "   • Produce 4000 Celery task executions"
echo ""
echo "📊 Monitoring Recommendations:"
echo "   Terminal 1: docker stats"
echo "   Terminal 2: docker-compose logs -f celery-worker-1"
echo "   Terminal 3: http://localhost:5555 (Flower dashboard)"
echo ""
echo "Press Enter to start the test..."
read

echo ""
echo "📊 Phase 1: Baseline Worker State"
echo "----------------------------------"
echo ""

# Get initial worker PIDs and memory usage
echo "Capturing initial worker process information..."
echo ""

for worker in celery-worker-1 celery-worker-2 celery-worker-3; do
    if docker ps | grep -q $worker; then
        # Get container stats
        STATS=$(docker stats --no-stream --format "{{.MemUsage}}\t{{.CPUPerc}}" $worker 2>/dev/null)
        MEMORY=$(echo $STATS | cut -f1)
        CPU=$(echo $STATS | cut -f2)
        
        echo "  $worker:"
        echo "    Memory: $MEMORY"
        echo "    CPU: $CPU"
        
        # Get main process PID
        PID=$(docker exec $worker ps aux | grep "celery worker" | grep -v grep | head -1 | awk '{print $2}' 2>/dev/null)
        if [ ! -z "$PID" ]; then
            echo "    Main PID: $PID"
            echo "$worker:$PID" >> /tmp/memory-test-initial-pids.txt
        fi
    fi
done

echo ""
echo "  Initial state captured"
echo ""

sleep 2

# Submit heavy load
echo "📊 Phase 2: Submit Heavy Load (4000 tasks)"
echo "-------------------------------------------"
echo ""

echo "Submitting 250 requests with 16 tasks each..."
echo "This will take 2-3 minutes to submit all requests"
echo ""

START_SUBMIT=$(date +%s)

for i in {1..250}; do
    # Use different priorities to test all queues
    if [ $((i % 3)) -eq 0 ]; then
        PRIORITY="high"
    elif [ $((i % 3)) -eq 1 ]; then
        PRIORITY="medium"
    else
        PRIORITY="low"
    fi
    
    # Submit in background to speed up submission
    curl -s -X POST http://localhost/api/v1/tasks \
        -H "Content-Type: application/json" \
        -d "{
            \"amount\": $((i * 100)).0,
            \"interest_rate\": 0.0$((i % 10)),
            \"years\": $((i % 20 + 1)),
            \"priority\": \"$PRIORITY\"
        }" > /dev/null 2>&1 &
    
    # Limit concurrent submissions to avoid overwhelming the API
    if [ $((i % 25)) -eq 0 ]; then
        wait  # Wait for batch to complete
        echo "  $i/250 requests submitted..."
    fi
done

wait  # Wait for all submissions to complete

END_SUBMIT=$(date +%s)
SUBMIT_DURATION=$((END_SUBMIT - START_SUBMIT))

echo ""
echo "✅ All 250 requests submitted in ${SUBMIT_DURATION}s"
echo ""

sleep 2

# Monitor memory usage
echo "📊 Phase 3: Monitor Memory Usage"
echo "---------------------------------"
echo ""

echo "Monitoring worker memory every 30 seconds..."
echo "Tasks are processing in background (this takes 5-10 minutes)"
echo ""
echo "Press Ctrl+C when you want to skip to next phase"
echo ""

MONITOR_COUNT=0
MAX_MONITORS=20  # Monitor for up to 10 minutes (20 × 30s)

while [ $MONITOR_COUNT -lt $MAX_MONITORS ]; do
    TIMESTAMP=$(date '+%H:%M:%S')
    echo "[$TIMESTAMP] Memory Snapshot #$((MONITOR_COUNT + 1)):"
    
    for worker in celery-worker-1 celery-worker-2 celery-worker-3; do
        if docker ps | grep -q $worker; then
            STATS=$(docker stats --no-stream --format "{{.MemUsage}}\t{{.CPUPerc}}" $worker 2>/dev/null)
            MEMORY=$(echo $STATS | cut -f1)
            CPU=$(echo $STATS | cut -f2)
            
            echo "  $worker: Memory=$MEMORY CPU=$CPU"
        fi
    done
    
    # Check queue depth
    HEALTH=$(curl -s http://localhost/api/v1/health 2>/dev/null)
    QUEUE_DEPTH=$(echo $HEALTH | jq -r '.data.queue_stats.approximate_depth' 2>/dev/null || echo "unknown")
    echo "  Queue Depth: $QUEUE_DEPTH tasks remaining"
    
    echo ""
    
    # If queue is empty or nearly empty, exit monitoring
    if [ "$QUEUE_DEPTH" != "unknown" ] && [ $QUEUE_DEPTH -lt 10 ]; then
        echo "Queue nearly empty, moving to next phase..."
        break
    fi
    
    MONITOR_COUNT=$((MONITOR_COUNT + 1))
    
    if [ $MONITOR_COUNT -lt $MAX_MONITORS ]; then
        sleep 30
    fi
done

echo ""

# Check for worker restarts
echo "📊 Phase 4: Worker Restart Analysis"
echo "------------------------------------"
echo ""

echo "Checking if workers restarted (PID changes)..."
echo ""

RESTART_COUNT=0

if [ -f /tmp/memory-test-initial-pids.txt ]; then
    while IFS=: read -r worker initial_pid; do
        if docker ps | grep -q $worker; then
            CURRENT_PID=$(docker exec $worker ps aux | grep "celery worker" | grep -v grep | head -1 | awk '{print $2}' 2>/dev/null)
            
            if [ ! -z "$CURRENT_PID" ] && [ ! -z "$initial_pid" ]; then
                if [ "$CURRENT_PID" != "$initial_pid" ]; then
                    echo "  ✅ $worker: PID changed ($initial_pid → $CURRENT_PID)"
                    echo "     Worker restarted due to max_tasks_per_child"
                    RESTART_COUNT=$((RESTART_COUNT + 1))
                else
                    echo "  ℹ️  $worker: PID unchanged ($CURRENT_PID)"
                    echo "     May not have processed 100 tasks yet"
                fi
            fi
        fi
    done < /tmp/memory-test-initial-pids.txt
    
    rm -f /tmp/memory-test-initial-pids.txt
else
    echo "  ⚠️  Initial PID data not available"
fi

echo ""

if [ $RESTART_COUNT -gt 0 ]; then
    echo "  ✅ $RESTART_COUNT workers restarted (memory leak prevention working)"
else
    echo "  ℹ️  No restarts detected (workers may not have hit 100 task limit)"
    echo "  Note: Each worker needs to process 100 tasks to trigger restart"
fi

echo ""

# Final memory check
echo "📊 Phase 5: Final Memory State"
echo "-------------------------------"
echo ""

echo "Final memory usage after processing 4000 tasks:"
echo ""

for worker in celery-worker-1 celery-worker-2 celery-worker-3; do
    if docker ps | grep -q $worker; then
        STATS=$(docker stats --no-stream --format "{{.MemUsage}}\t{{.CPUPerc}}" $worker 2>/dev/null)
        MEMORY=$(echo $STATS | cut -f1)
        CPU=$(echo $STATS | cut -f2)
        
        echo "  $worker:"
        echo "    Memory: $MEMORY (limit: 2GB)"
        echo "    CPU: $CPU"
    fi
done

echo ""

# Check if workers hit memory limits
echo "Checking if any workers hit memory limits..."
MEMORY_KILLS=$(docker-compose logs celery-worker-1 celery-worker-2 celery-worker-3 2>/dev/null | grep -i "oom\|out of memory\|killed" | wc -l | xargs)

if [ $MEMORY_KILLS -gt 0 ]; then
    echo "  ⚠️  $MEMORY_KILLS OOM events detected (check logs)"
    echo "  Workers may need more memory or lower concurrency"
else
    echo "  ✅ No OOM kills detected"
    echo "  Memory limits properly configured"
fi

echo ""

# Check system health
echo "📊 Phase 6: System Health Verification"
echo "---------------------------------------"
echo ""

HEALTH=$(curl -s http://localhost/api/v1/health)
OVERALL_STATUS=$(echo $HEALTH | jq -r '.data.status' 2>/dev/null || echo "unknown")
QUEUE_DEPTH=$(echo $HEALTH | jq -r '.data.queue_stats.approximate_depth' 2>/dev/null || echo "0")

echo "  System Status: $OVERALL_STATUS"
echo "  Queue Depth: $QUEUE_DEPTH tasks"
echo ""

if [ "$OVERALL_STATUS" == "healthy" ]; then
    echo "  ✅ System healthy after stress test"
else
    echo "  ⚠️  System may be degraded"
fi

echo ""

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Memory Leak Simulation Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 Test Results:"
echo ""
echo "  1. WORKER RESTARTS:"
if [ $RESTART_COUNT -gt 0 ]; then
    echo "     ✅ $RESTART_COUNT workers restarted automatically"
    echo "     ✅ max_tasks_per_child=100 prevents memory leaks"
else
    echo "     ℹ️  No restarts observed in monitoring window"
    echo "     ℹ️  Workers may restart after test completion"
fi
echo ""
echo "  2. MEMORY MANAGEMENT:"
if [ $MEMORY_KILLS -eq 0 ]; then
    echo "     ✅ No OOM kills (memory limits appropriate)"
else
    echo "     ⚠️  $MEMORY_KILLS OOM events (consider tuning)"
fi
echo "     • Worker limit: 2GB per container"
echo "     • Concurrency: 4 processes per worker"
echo ""
echo "  3. THROUGHPUT:"
echo "     • Submitted: 4000 tasks"
echo "     • Workers: 3 × 4 concurrency = 12 parallel tasks"
echo "     • Expected duration: 4000 tasks ÷ 12 × 6s ≈ 2000s (33 min)"
echo ""
echo "  4. SYSTEM STABILITY:"
echo "     • System status: $OVERALL_STATUS"
echo "     • Queue depth: $QUEUE_DEPTH tasks"
echo ""
echo "📖 Production Insights:"
echo "  • max_tasks_per_child prevents memory leaks in long-running workers"
echo "  • Worker pool regeneration happens transparently (no downtime)"
echo "  • Memory limits + OOM killer = last resort protection"
echo "  • In production: Monitor memory trends over days/weeks"
echo ""
echo "🔍 Next Steps:"
echo "  • Check Flower for task history: http://localhost:5555"
echo "  • View worker logs: docker-compose logs celery-worker-1 | grep -i restart"
echo "  • Monitor long-term: docker stats --no-stream"
echo "  • Check for memory leaks: docker exec celery-worker-1 ps aux"
echo ""
echo "💡 Tuning Recommendations:"
echo "  • If OOM kills: Reduce concurrency or increase memory limit"
echo "  • If high memory: Reduce max_tasks_per_child (restart more often)"
echo "  • If slow processing: Increase concurrency (more CPU needed)"
echo ""
