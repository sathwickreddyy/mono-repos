#!/usr/bin/env bash
# ============================================================================
# Infrastructure Validation Script
# ============================================================================
# Purpose: Verify Phase 2 Docker infrastructure is correctly configured
# Usage: ./scripts/validate-infrastructure.sh
# ============================================================================

# Don't exit on error - we want to see all validation results
set +e

echo "🔍 Phase 2 Infrastructure Validation"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

# Helper functions
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# ============================================================================
# 1. Check Required Files
# ============================================================================
echo "📁 Checking Required Files..."

files=(
    "docker-compose.yml"
    "nginx/nginx.conf"
    "fastapi-app/Dockerfile"
    "fastapi-app/requirements.txt"
    "celery-worker/Dockerfile"
    "celery-worker/requirements.txt"
    "redis/redis.conf"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        pass "$file exists"
    else
        fail "$file missing"
    fi
done

echo ""

# ============================================================================
# 2. Check Volume Mount Directories
# ============================================================================
echo "💾 Checking Volume Mounts..."

MOUNT_BASE="/Users/sathwick/my-office/docker-mounts/task-queue-cpu-intesive"

if [ -d "$MOUNT_BASE/redis-data" ]; then
    pass "Redis data directory exists"
else
    fail "Redis data directory missing: $MOUNT_BASE/redis-data"
fi

if [ -d "$MOUNT_BASE/nginx-logs" ]; then
    pass "Nginx logs directory exists"
else
    fail "Nginx logs directory missing: $MOUNT_BASE/nginx-logs"
fi

echo ""

# ============================================================================
# 3. Validate docker-compose.yml Syntax
# ============================================================================
echo "🐳 Validating docker-compose.yml..."

if docker-compose config > /dev/null 2>&1; then
    pass "docker-compose.yml syntax valid"
else
    fail "docker-compose.yml has syntax errors"
    docker-compose config
fi

echo ""

# ============================================================================
# 4. Check Docker Daemon
# ============================================================================
echo "🐋 Checking Docker..."

if docker info > /dev/null 2>&1; then
    pass "Docker daemon running"
else
    fail "Docker daemon not running"
fi

echo ""

# ============================================================================
# 5. Check System Resources
# ============================================================================
echo "💻 Checking System Resources..."

# Get total memory (macOS)
if command -v sysctl &> /dev/null; then
    TOTAL_MEM=$(sysctl -n hw.memsize)
    TOTAL_MEM_GB=$((TOTAL_MEM / 1024 / 1024 / 1024))
    
    if [ "$TOTAL_MEM_GB" -ge 16 ]; then
        pass "Memory: ${TOTAL_MEM_GB}GB (sufficient)"
    else
        warn "Memory: ${TOTAL_MEM_GB}GB (recommended 16GB+)"
    fi
fi

# Get CPU cores
if command -v sysctl &> /dev/null; then
    CPU_CORES=$(sysctl -n hw.ncpu)
    
    if [ "$CPU_CORES" -ge 8 ]; then
        pass "CPU cores: $CPU_CORES (sufficient)"
    else
        warn "CPU cores: $CPU_CORES (recommended 8+)"
    fi
fi

echo ""

# ============================================================================
# 6. Check Network Configuration
# ============================================================================
echo "🌐 Checking Network Configuration..."

# Check if networks defined in docker-compose
if grep -q "networks:" docker-compose.yml; then
    pass "Docker networks defined"
else
    fail "Docker networks not defined"
fi

# Check for frontend, backend, monitoring networks
for network in frontend backend monitoring; do
    if grep -q "$network:" docker-compose.yml; then
        pass "Network '$network' configured"
    else
        fail "Network '$network' not found"
    fi
done

echo ""

# ============================================================================
# 7. Validate Service Configuration
# ============================================================================
echo "⚙️  Validating Services..."

services=(
    "redis"
    "fastapi-1"
    "fastapi-2"
    "fastapi-3"
    "celery-worker-1"
    "celery-worker-2"
    "celery-worker-3"
    "nginx"
    "flower"
)

for service in "${services[@]}"; do
    if grep -q "$service:" docker-compose.yml; then
        pass "Service '$service' defined"
    else
        fail "Service '$service' not found"
    fi
done

echo ""

# ============================================================================
# 8. Check Health Check Configuration
# ============================================================================
echo "🏥 Checking Health Checks..."

if grep -q "healthcheck:" docker-compose.yml; then
    count=$(grep -c "healthcheck:" docker-compose.yml)
    pass "Health checks configured ($count services)"
else
    fail "No health checks found"
fi

echo ""

# ============================================================================
# 9. Check Resource Limits
# ============================================================================
echo "📊 Checking Resource Limits..."

if grep -q "deploy:" docker-compose.yml && grep -q "resources:" docker-compose.yml; then
    pass "Resource limits configured"
else
    fail "Resource limits not configured"
fi

echo ""

# ============================================================================
# 10. Validate Nginx Configuration
# ============================================================================
echo "🔧 Validating Nginx Configuration..."

if [ -f "nginx/nginx.conf" ]; then
    # Check for key configurations
    if grep -q "least_conn" nginx/nginx.conf; then
        pass "Load balancing algorithm configured (least_conn)"
    else
        fail "Load balancing algorithm not found"
    fi
    
    if grep -q "limit_req_zone" nginx/nginx.conf; then
        pass "Rate limiting configured"
    else
        warn "Rate limiting not configured"
    fi
    
    if grep -q "keepalive" nginx/nginx.conf; then
        pass "Connection pooling configured"
    else
        warn "Connection pooling not configured"
    fi
fi

echo ""

# ============================================================================
# Summary
# ============================================================================
echo "=================================="
echo "📈 Validation Summary"
echo "=================================="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Infrastructure ready for Phase 3.${NC}"
    exit 0
else
    echo -e "${RED}❌ Some checks failed. Please fix the issues above.${NC}"
    exit 1
fi
