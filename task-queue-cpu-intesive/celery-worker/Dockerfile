# ============================================================================
# CELERY WORKER DOCKERFILE - Simplified Single-Stage Build  
# ============================================================================

FROM python:3.11-slim

# Metadata labels
LABEL maintainer="sathwick@example.com"
LABEL version="1.0.0"
LABEL description="Celery worker for CPU-intensive financial calculations"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install runtime and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libopenblas0 \
    libgomp1 \
    tini \
    gcc \
    g++ \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r worker && useradd -r -g worker -u 1001 worker

# Create working directory
WORKDIR /app
RUN chown worker:worker /app

# Copy requirements and install as root (need gcc)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Remove build dependencies (keep runtime libs)
RUN apt-get purge -y gcc g++ gfortran && apt-get autoremove -y

# Switch to non-root user
USER worker

# Copy application code
COPY --chown=worker:worker . .

# Use tini as init
ENTRYPOINT ["/usr/bin/tini", "--"]

# Run Celery worker
CMD ["celery", "-A", "main", "worker", \
    "--loglevel=info", \
    "--concurrency=4", \
    "--max-tasks-per-child=100", \
    "--task-events"]
