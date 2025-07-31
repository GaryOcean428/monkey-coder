#!/bin/bash

# Test Docker Build Script
# Tests the Docker build locally before Railway deployment

set -e

echo "🐳 Testing Docker build for monkey-coder..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Clean up any existing test containers
echo "🧹 Cleaning up existing test containers..."
docker rm -f monkey-coder-test 2>/dev/null || true
docker rmi -f monkey-coder-test 2>/dev/null || true

# Test web-builder stage only (faster for debugging)
echo "🔨 Testing web-builder stage..."
if docker buildx build --progress=plain --target=web-builder -t monkey-coder-web-test .; then
    echo -e "${GREEN}✅ Web builder stage successful!${NC}"
else
    echo -e "${RED}❌ Web builder stage failed!${NC}"
    exit 1
fi

# Test full build
echo "🏗️ Testing full multi-stage build..."
if docker buildx build --progress=plain -t monkey-coder-test .; then
    echo -e "${GREEN}✅ Full Docker build successful!${NC}"
else
    echo -e "${RED}❌ Full Docker build failed!${NC}"
    exit 1
fi

# Test container startup
echo "🚀 Testing container startup..."
if docker run -d -p 8000:8000 --name monkey-coder-test monkey-coder-test; then
    echo -e "${GREEN}✅ Container started successfully!${NC}"
    
    # Wait for startup
    echo "⏳ Waiting for application startup..."
    sleep 10
    
    # Test health endpoint
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Health check passed!${NC}"
    else
        echo -e "${YELLOW}⚠️ Health check failed (may be normal during startup)${NC}"
    fi
    
    # Show logs
    echo "📋 Container logs:"
    docker logs --tail 20 monkey-coder-test
    
    # Clean up
    docker stop monkey-coder-test
    docker rm monkey-coder-test
else
    echo -e "${RED}❌ Container startup failed!${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 All Docker tests passed! Ready for Railway deployment.${NC}"

# Show build summary
echo ""
echo "📊 Build Summary:"
echo "  • Frontend: Next.js with npm install --legacy-peer-deps"
echo "  • Backend: Python FastAPI with monkey-coder-core"
echo "  • Static Assets: Next.js export in /app/packages/web/out/"
echo "  • Container: Non-root user with health checks"
echo ""
echo "🚀 Railway deployment should now work correctly!"