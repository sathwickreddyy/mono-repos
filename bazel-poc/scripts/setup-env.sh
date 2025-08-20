#!/bin/bash

echo "Setting up Bazel monorepo environment..."

# Install Bazelisk if not present
if ! command -v bazel &> /dev/null; then
    echo "Installing Bazelisk..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install bazelisk
    else
        # Linux installation
        curl -LO "https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64"
        chmod +x bazelisk-linux-amd64
        sudo mv bazelisk-linux-amd64 /usr/local/bin/bazel
    fi
fi

# Setup Java service
echo "Setting up Java service..."
cd demo
chmod +x gradlew
./gradlew wrapper --gradle-version=8.5
cd ..

# Setup Python service
echo "Setting up Python service..."
cd fastapi
python -m pip install -r requirements.txt
cd ..

# Setup frontend
echo "Setting up frontend..."
cd frontend
npm install
cd ..

echo "Environment setup complete!"
echo "Run 'make run-all' to start all services"
