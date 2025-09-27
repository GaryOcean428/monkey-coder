#!/bin/bash

# Clean build artifacts script for monkey-coder
# Removes all build cache and artifacts for fresh builds

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧹 Cleaning build artifacts and cache...${NC}"

# Next.js build artifacts
echo -e "${YELLOW}🗑️  Removing Next.js build artifacts...${NC}"
rm -rf packages/web/.next
rm -rf packages/web/out
rm -rf packages/web/build
rm -rf packages/web/dist
rm -rf packages/web/.vercel
rm -rf packages/web/*.tsbuildinfo

# Node.js dependencies and cache
echo -e "${YELLOW}🗑️  Removing Node.js cache...${NC}"
rm -rf packages/web/node_modules/.cache
rm -rf packages/web/.yarn/cache
rm -rf packages/web/.npm
rm -rf packages/cli/node_modules/.cache
rm -rf packages/sdk/node_modules/.cache

# Python build artifacts
echo -e "${YELLOW}🗑️  Removing Python build artifacts...${NC}"
find packages/core -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find packages/core -name "*.pyc" -delete 2>/dev/null || true
find packages/core -name "*.pyo" -delete 2>/dev/null || true
find packages/core -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true
rm -rf packages/core/build
rm -rf packages/core/dist

# Docker build cache
echo -e "${YELLOW}🗑️  Removing Docker build cache...${NC}"
rm -rf /tmp/.buildx-cache
rm -rf /tmp/.buildx-cache-new

# General cache and temp files
echo -e "${YELLOW}🗑️  Removing general cache files...${NC}"
find . -name "*.log" -delete 2>/dev/null || true
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true

# Optional: Clean Docker images (commented out for safety)
# echo -e "${YELLOW}🗑️  Removing Docker images...${NC}"
# docker image prune -f
# docker rmi monkey-coder:latest 2>/dev/null || true

echo -e "${GREEN}✅ Clean completed!${NC}"
echo -e "${BLUE}📊 Cleaned items:${NC}"
echo -e "   • Next.js build cache (.next, out, build, dist)"
echo -e "   • Python bytecode (__pycache__, *.pyc)"
echo -e "   • Node.js cache directories"
echo -e "   • Docker buildx cache"
echo -e "   • Temporary and log files"
echo -e ""
echo -e "${GREEN}🔧 Ready for fresh build with:${NC}"
echo -e "   ./scripts/build-docker.sh  # LOCAL Docker testing only"
echo -e "   railway deploy            # Production deployment"