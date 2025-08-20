# Bazel Monorepo: Java Spring + Python FastAPI + React

A production-ready monorepo demonstrating how Bazel orchestrates multiple language ecosystems while preserving native development workflows.

## Architecture Overview

- **Java Service**: Spring Boot 3.3 with Gradle (port 8080)
- **Python API**: FastAPI with uvicorn (port 8000)
- **React Frontend**: Vite-powered SPA (port 3000)
- **Build System**: Bazel as unified orchestrator
- **CI/CD**: GitHub Actions with incremental builds

## Key Benefits Realized

| Traditional Multi-Repo | This Bazel Monorepo |
|-------------------------|---------------------|
| 3 separate CI pipelines | 1 unified pipeline |
| Dependency drift between services | Atomic cross-service updates |
| Manual coordination for API changes | Single commit updates all consumers |
| 3 different build tools | Consistent Bazel interface |

## Quick Start

