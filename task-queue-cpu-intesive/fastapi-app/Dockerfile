# ============================================================================
# FASTAPI PRODUCTION DOCKERFILE - Simplified Single-Stage Build
# ============================================================================

FROM python:3.11-slim

# Metadata labels
LABEL maintainer="sathwick@example.com"
LABEL version="1.0.0"
LABEL description="FastAPI API server for distributed task queue"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/app/.local/bin:$PATH"

# Install runtime and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tini \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r app && useradd -r -g app -u 1000 app

# Create app directory
WORKDIR /app
RUN chown app:app /app

# Copy requirements and install as root (need gcc)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Remove build dependencies to reduce image size
RUN apt-get purge -y gcc && apt-get autoremove -y

# Switch to non-root user
USER app

# Copy application code
COPY --chown=app:app . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use tini as init
ENTRYPOINT ["/usr/bin/tini", "--"]

# Run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
