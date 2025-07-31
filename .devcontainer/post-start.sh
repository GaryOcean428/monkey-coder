#!/bin/bash

set -e

echo "🔄 Starting development services..."

# Ensure services are healthy
echo "🏥 Checking service health..."

# Check PostgreSQL
until pg_isready -h postgres -p 5432 -U postgres; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done

# Check Redis
until redis-cli -h redis ping; do
    echo "Waiting for Redis..."
    sleep 2
done

echo "✅ All services are healthy!"

# Start development servers in the background if desired
# Uncomment the following lines to auto-start services

# echo "🚀 Starting development servers..."
# cd /workspace
# 
# # Start the API server
# nohup python -m monkey_coder.app.main > logs/api.log 2>&1 &
# 
# # Start the web frontend
# cd packages/web
# nohup yarn dev > ../logs/web.log 2>&1 &
# cd /workspace

echo "🎉 Ready for development!"
