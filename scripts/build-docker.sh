#!/bin/bash

# LOCAL DOCKER TESTING SCRIPT - NOT USED FOR RAILWAY DEPLOYMENT
#
# This script is for LOCAL development and testing only.
# Railway deployment uses railpack.json and does NOT use this Docker script.
#
# Railway deployment workflow:
# 1. Railway reads railpack.json 
# 2. Railway automatically creates containers internally
# 3. No Dockerfile or Docker scripts needed
#
# For Railway deployment, use: railway deploy
# For local development, use: python run_server.py
#
# This script remains for developers who want to test Docker builds locally

# Docker buildx script for local testing with Railway optimization
# Follows Railway best practices for multi-stage builds and caching

set -e

echo "⚠️  WARNING: This script is for LOCAL testing only!"
echo "⚠️  Railway deployment uses railpack.json, not Docker"
echo "⚠️  To deploy to Railway, use: railway deploy"
echo ""
echo "Press Ctrl+C to cancel, or any key to continue with local Docker test..."
read -n 1 -s

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="monkey-coder"
TAG="${1:-latest}"
PLATFORM="${2:-linux/amd64,linux/arm64}"

echo -e "${BLUE}🐳 Building ${IMAGE_NAME}:${TAG} with Docker buildx (LOCAL TESTING ONLY)${NC}"

# Check if buildx is available
if ! docker buildx version >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker buildx not available. Please install Docker Desktop or enable buildx${NC}"
    exit 1
fi

# Create buildx builder if it doesn't exist
BUILDER_NAME="monkey-coder-builder"
if ! docker buildx inspect $BUILDER_NAME >/dev/null 2>&1; then
    echo -e "${YELLOW}📦 Creating buildx builder: $BUILDER_NAME${NC}"
    docker buildx create --name $BUILDER_NAME --use --bootstrap
else
    echo -e "${GREEN}✅ Using existing buildx builder: $BUILDER_NAME${NC}"
    docker buildx use $BUILDER_NAME
fi

# Pre-build checks
echo -e "${BLUE}🔍 Running pre-build validation...${NC}"

# Check if web package exists
if [ ! -d "packages/web" ]; then
    echo -e "${RED}❌ packages/web directory not found${NC}"
    exit 1
fi

# Check if core package exists
if [ ! -d "packages/core" ]; then
    echo -e "${RED}❌ packages/core directory not found${NC}"
    exit 1
fi

# Check critical files
REQUIRED_FILES=(
    "packages/web/package.json"
    "packages/web/src/lib/utils.ts"
    "packages/web/next.config.js"
    "packages/web/tsconfig.json"
    "packages/core/setup.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Required file not found: $file${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ Pre-build validation passed${NC}"

# Build with buildx following Railway best practices
echo -e "${BLUE}🔨 Building multi-platform image...${NC}"

# Use buildx with optimizations for Railway deployment
docker buildx build \
    --platform $PLATFORM \
    --tag $IMAGE_NAME:$TAG \
    --cache-from type=local,src=/tmp/.buildx-cache \
    --cache-to type=local,dest=/tmp/.buildx-cache-new,mode=max \
    --load \
    --progress=plain \
    .

# Move cache (buildx cache management)
if [ -d "/tmp/.buildx-cache-new" ]; then
    rm -rf /tmp/.buildx-cache
    mv /tmp/.buildx-cache-new /tmp/.buildx-cache
fi

echo -e "${GREEN}✅ Build completed successfully${NC}"

# Test the built image
echo -e "${BLUE}🧪 Running container health test...${NC}"

# Test container startup
CONTAINER_ID=$(docker run -d -p 8000:8000 -e NODE_ENV=production $IMAGE_NAME:$TAG)

# Wait for health check
echo -e "${YELLOW}⏳ Waiting for health check...${NC}"
sleep 10

# Check if container is healthy
if docker ps | grep -q $CONTAINER_ID; then
    echo -e "${GREEN}✅ Container started successfully${NC}"
    
    # Test health endpoint
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Health check passed${NC}"
    else
        echo -e "${YELLOW}⚠️  Health check failed (container may still be starting)${NC}"
    fi
else
    echo -e "${RED}❌ Container failed to start${NC}"
    docker logs $CONTAINER_ID
fi

# Cleanup test container
docker stop $CONTAINER_ID >/dev/null 2>&1 || true
docker rm $CONTAINER_ID >/dev/null 2>&1 || true

echo -e "${BLUE}📊 Image information:${NC}"
docker images | grep $IMAGE_NAME

echo -e "${GREEN}🚀 Local Docker build completed!${NC}"
echo -e "${YELLOW}⚠️  REMINDER: This Docker image is for LOCAL testing only${NC}"
echo -e ""
echo -e "${BLUE}💡 To run this container locally:${NC}"
echo -e "   docker run -p 8000:8000 -e NODE_ENV=production $IMAGE_NAME:$TAG"
echo -e ""
echo -e "${BLUE}💡 For Railway deployment (production), use:${NC}"  
echo -e "   railway deploy  # Uses railpack.json, not this Docker image"