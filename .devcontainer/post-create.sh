#!/bin/bash

set -e

echo "🚀 Setting up Monkey Coder development environment..."

# Ensure we're in the workspace directory
cd /workspace

# Install Node.js dependencies if not already installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    yarn install --frozen-lockfile
fi

# Install Python dependencies for all packages
echo "🐍 Installing Python dependencies..."

# Install core package in development mode
if [ -f "packages/core/pyproject.toml" ]; then
    cd packages/core
    pip install -e ".[dev]"
    cd /workspace
fi

# Install SDK package in development mode
if [ -f "packages/sdk/src/python/setup.py" ]; then
    cd packages/sdk/src/python
    pip install -e ".[dev]"
    cd /workspace
fi

# Install pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
if [ -f ".pre-commit-config.yaml" ]; then
    pre-commit install
fi

# Set up environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating default environment file..."
    cp .env.example .env 2>/dev/null || echo "# Monkey Coder Development Environment" > .env
fi

# Create necessary directories
echo "📁 Creating development directories..."
mkdir -p logs temp uploads

# Set up database
echo "🗄️  Setting up development database..."
# Wait for PostgreSQL to be ready
until pg_isready -h postgres -p 5432 -U postgres; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done

# Run database migrations if available
if [ -f "scripts/migrate.py" ]; then
    python scripts/migrate.py
fi

# Build TypeScript packages
echo "🔨 Building TypeScript packages..."
yarn build

# Install CLI globally for development
echo "🛠️  Installing CLI for development..."
cd packages/cli
npm link
cd /workspace

echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Quick start commands:"
echo "  yarn dev          - Start all development servers"
echo "  yarn test         - Run all tests"
echo "  yarn lint         - Run linting"
echo "  yarn build        - Build all packages"
echo "  monkey-coder      - Run CLI tool"
echo ""
echo "🌐 Available services:"
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  Docs:      http://localhost:3001"
echo "  Metrics:   http://localhost:9090"
echo ""
