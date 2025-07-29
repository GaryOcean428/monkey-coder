#!/bin/bash
# Test script for unified deployment setup

set -e

echo "🧪 Testing Unified Deployment Setup"
echo "=================================="

# Test 1: Build Next.js frontend
echo "📦 Building Next.js frontend..."
cd packages/web
if yarn build; then
    echo "✅ Next.js build successful"
    if [ -d "out" ]; then
        echo "✅ Static export directory 'out' created"
        echo "📊 Frontend files generated:"
        ls -la out/
    else
        echo "❌ Static export directory 'out' not found"
        exit 1
    fi
else
    echo "❌ Next.js build failed"
    exit 1
fi

cd ../..

# Test 2: Test Docker build
echo ""
echo "🐳 Testing Docker build..."
if docker build -f Dockerfile.unified -t monkey-coder-test:latest .; then
    echo "✅ Docker build successful"
else
    echo "❌ Docker build failed"
    exit 1
fi

# Test 3: Test container startup (quick test)
echo ""
echo "🚀 Testing container startup..."
CONTAINER_ID=$(docker run -d -p 8001:8000 -e PORT=8000 monkey-coder-test:latest)

echo "⏳ Waiting for container to start..."
sleep 10

# Test health endpoint
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    docker logs $CONTAINER_ID
    docker stop $CONTAINER_ID
    exit 1
fi

# Test if static files are being served
if curl -f http://localhost:8001/ > /dev/null 2>&1; then
    echo "✅ Frontend static files are being served"
else
    echo "❌ Frontend static files not accessible"
    docker logs $CONTAINER_ID
    docker stop $CONTAINER_ID
    exit 1
fi

# Cleanup
echo ""
echo "🧹 Cleaning up test container..."
docker stop $CONTAINER_ID > /dev/null
docker rm $CONTAINER_ID > /dev/null

echo ""
echo "🎉 All tests passed! Unified deployment is ready."
echo ""
echo "🚀 Next steps:"
echo "1. Commit your changes to git"
echo "2. Push to your repository"
echo "3. In Railway dashboard, change the service to use Dockerfile.unified"
echo "4. Deploy the updated service"
echo ""
echo "🔗 Your Railway service ID: ccc58ca2-1f4b-4086-beb6-2321ac7dab40"
echo "🌐 Expected URL: https://monkey-coder.up.railway.app"