.PHONY: setup build test clean run-all run-java run-python run-react

# Setup development environment
setup:
	./scripts/setup-env.sh

# Build all projects
build:
	bazel build //...

# Test all projects
test:
	bazel test //...

# Clean build artifacts
clean:
	bazel clean

# Run all services
run-all:
	./scripts/run-all.sh

# Individual service runners
run-java:
	bazel run //demo:bootRun

run-python:
	bazel run //fastapi:server

run-react:
	bazel run //frontend:dev

# Quick development cycle
dev: build test
	@echo "Development build complete"

# CI simulation
ci: clean build test
	@echo "CI pipeline simulation complete"
