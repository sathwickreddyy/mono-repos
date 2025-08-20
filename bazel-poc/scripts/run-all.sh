#!/bin/bash

echo "Starting all services in parallel..."

# Start Java service in background
echo "Starting Java Spring service on :8080..."
bazel run //demo:bootRun &
JAVA_PID=$!

# Start Python service in background
echo "Starting Python FastAPI service on :8000..."
bazel run //fastapi:server &
PYTHON_PID=$!

# Start React frontend in background
echo "Starting React frontend on :3000..."
bazel run //frontend:dev &
REACT_PID=$!

echo "All services started!"
echo "Java Spring: http://localhost:8080"
echo "Python FastAPI: http://localhost:8000"
echo "React Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt signal
trap 'kill $JAVA_PID $PYTHON_PID $REACT_PID' SIGINT
wait
