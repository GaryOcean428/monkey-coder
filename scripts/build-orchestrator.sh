#!/bin/bash
# Build orchestration script with progress reporting
# Usage: ./scripts/build-orchestrator.sh [mode]
# Modes: sequential (default), parallel, watch

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

MODE=${1:-sequential}

echo -e "${BLUE}🏗️  Monkey Coder Build Orchestrator${NC}"
echo -e "${BLUE}Mode: ${MODE}${NC}\n"

function build_package() {
    local package=$1
    local name=$2
    
    echo -e "${YELLOW}Building ${name}...${NC}"
    start_time=$(date +%s)
    
    if yarn workspace "${package}" run build; then
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        echo -e "${GREEN}✓ ${name} built in ${duration}s${NC}\n"
        return 0
    else
        echo -e "${RED}✗ ${name} build failed${NC}\n"
        return 1
    fi
}

function build_sequential() {
    echo "Building packages sequentially..."
    
    build_package "monkey-coder-cli" "CLI" || exit 1
    build_package "@monkey-coder/sdk" "SDK" || exit 1
    build_package "@monkey-coder/web" "Web" || exit 1
    
    echo -e "${YELLOW}Building Python Core...${NC}"
    start_time=$(date +%s)
    if (cd packages/core && python -m build); then
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        echo -e "${GREEN}✓ Core built in ${duration}s${NC}\n"
    else
        echo -e "${RED}✗ Core build failed${NC}\n"
        exit 1
    fi
}

function build_parallel() {
    echo "Building packages in parallel..."
    
    # Build TypeScript packages in parallel
    npm-run-all --parallel \
        "build:cli" \
        "build:sdk" \
        "build:web" || exit 1
    
    # Build Python separately (it's independent)
    yarn build:core || exit 1
}

function build_watch() {
    echo "Starting watch mode for all packages..."
    
    # Use run-p for parallel watch
    npm-run-all --parallel \
        "dev:cli" \
        "dev:web"
}

case $MODE in
    sequential)
        build_sequential
        ;;
    parallel)
        build_parallel
        ;;
    watch)
        build_watch
        ;;
    *)
        echo "Unknown mode: $MODE"
        echo "Usage: $0 [sequential|parallel|watch]"
        exit 1
        ;;
esac

echo -e "${GREEN}✅ Build complete!${NC}"
