<!-- Use this file to provide workspace-specific custom instructions to Copilot -->

## Project Context
This is a **production-grade distributed task processing system** for CPU-intensive financial calculations.

## Tech Stack
- **Backend**: Python 3.11+, FastAPI
- **Task Queue**: Celery with Redis broker
- **Load Balancer**: Nginx
- **Monitoring**: Flower
- **Infrastructure**: Docker Compose

## Architecture Patterns
- Microservices architecture
- Queue-based load leveling
- Competing consumers pattern
- Circuit breaker for backpressure
- Health check pattern

## Code Style & Standards
1. **Follow PEP 8** for Python code
2. **Type hints** required for all functions
3. **Docstrings** for all public methods (Google style)
4. **Error handling**: Use custom exceptions, structured logging
5. **Testing**: Unit tests for business logic, integration tests for APIs

## Senior Developer Best Practices
- Separation of concerns (API vs Worker logic)
- Stateless services (12-factor app)
- Observability first (logging, metrics, tracing)
- Graceful degradation (circuit breakers, timeouts)
- Idempotent task design

## File Organization
- `fastapi-app/`: API server code only (no business logic)
- `celery-worker/`: Task definitions and CPU-intensive work
- `nginx/`: Load balancer configuration
- `scripts/`: Deployment and utility scripts
- `docs/`: Architecture and API documentation

## Environment Variables
- Always use environment variables for configuration
- Never hardcode secrets, ports, or hostnames
- Use `.env.example` as template

## Docker Guidelines
- One process per container
- Health checks for all services
- Resource limits defined
- Explicit image tags (no `latest`)

## Logging Standards
- Structured JSON logging
- Include correlation IDs (X-Request-ID)
- Log levels: DEBUG (dev), INFO (prod), ERROR (alerts)
- No sensitive data in logs

## Performance Targets
- API response: <50ms
- Task processing: 5-6s (CPU-intensive)
- Throughput: 12 tasks/sec (baseline)
- Queue depth: Max 500 tasks

## Security Considerations
- Input validation on all endpoints
- Rate limiting per IP/user
- Authentication required (JWT in production)
- Redis connection encryption (TLS in production)

## When Suggesting Code
1. Explain the **architectural decision** behind it
2. Point out **design patterns** used
3. Highlight **production-ready features** (error handling, retries, timeouts)
4. Mention **trade-offs** and alternatives
5. Include type hints and comprehensive error handling
