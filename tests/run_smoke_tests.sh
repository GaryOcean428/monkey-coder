#!/bin/bash
set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=${BACKEND_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-3000}
BACKEND_URL=${BACKEND_URL:-"http://localhost:$BACKEND_PORT"}
FRONTEND_URL=${FRONTEND_URL:-"http://localhost:$FRONTEND_PORT"}

# Test results
BACKEND_PASSED=false
FRONTEND_PASSED=false
CLI_PASSED=false
INTEGRATION_PASSED=false

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}🚀 MONKEY CODER COMPREHENSIVE SMOKE TESTS${NC}"
echo -e "${CYAN}============================================${NC}"

echo ""
echo -e "${BLUE}Configuration:${NC}"
echo -e "  Backend URL: ${BACKEND_URL}"
echo -e "  Frontend URL: ${FRONTEND_URL}"
echo ""

# Function to check if service is running
check_service() {
    local url=$1
    local service_name=$2
    
    echo -e "${YELLOW}Checking if $service_name is running...${NC}"
    
    if curl -s --max-time 5 "$url/health" > /dev/null 2>&1 || \
       curl -s --max-time 5 "$url/api/health" > /dev/null 2>&1 || \
       curl -s --max-time 5 "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $service_name is running${NC}"
        return 0
    else
        echo -e "${RED}❌ $service_name is not running at $url${NC}"
        return 1
    fi
}

# Function to run backend tests
run_backend_tests() {
    echo ""
    echo -e "${PURPLE}=====================================${NC}"
    echo -e "${PURPLE}🔧 BACKEND API SMOKE TESTS${NC}"
    echo -e "${PURPLE}=====================================${NC}"
    
    if check_service "$BACKEND_URL" "Backend"; then
        echo ""
        echo "Running backend smoke tests..."
        
        cd "$SCRIPT_DIR"
        export BACKEND_URL
        
        if python3 smoke_test_backend.py; then
            echo -e "${GREEN}✅ Backend tests passed${NC}"
            BACKEND_PASSED=true
        else
            echo -e "${RED}❌ Backend tests failed${NC}"
            BACKEND_PASSED=false
        fi
    else
        echo -e "${YELLOW}⚠️ Skipping backend tests - service not available${NC}"
        BACKEND_PASSED=false
    fi
}

# Function to run frontend tests
run_frontend_tests() {
    echo ""
    echo -e "${PURPLE}=====================================${NC}"
    echo -e "${PURPLE}🌐 FRONTEND ROUTE SMOKE TESTS${NC}"
    echo -e "${PURPLE}=====================================${NC}"
    
    if check_service "$FRONTEND_URL" "Frontend"; then
        echo ""
        echo "Running frontend smoke tests..."
        
        cd "$SCRIPT_DIR"
        export FRONTEND_URL
        
        if node smoke_test_frontend.mjs; then
            echo -e "${GREEN}✅ Frontend tests passed${NC}"
            FRONTEND_PASSED=true
        else
            echo -e "${RED}❌ Frontend tests failed${NC}"
            FRONTEND_PASSED=false
        fi
    else
        echo -e "${YELLOW}⚠️ Skipping frontend tests - service not available${NC}"
        FRONTEND_PASSED=false
    fi
}

# Function to run CLI tests  
run_cli_tests() {
    echo ""
    echo -e "${PURPLE}=====================================${NC}"
    echo -e "${PURPLE}⚡ CLI SMOKE TESTS${NC}"
    echo -e "${PURPLE}=====================================${NC}"
    
    echo "Running CLI smoke tests..."
    
    # Use the script directory
    cd "$SCRIPT_DIR"
    
    if node smoke_test_cli.mjs; then
        echo -e "${GREEN}✅ CLI tests passed${NC}"
        CLI_PASSED=true
    else
        echo -e "${RED}❌ CLI tests failed${NC}"
        CLI_PASSED=false
    fi
}

# Function to run user flow integration tests
run_integration_tests() {
    echo ""
    echo -e "${PURPLE}=====================================${NC}"
    echo -e "${PURPLE}🔄 USER FLOW INTEGRATION TESTS${NC}"
    echo -e "${PURPLE}=====================================${NC}"
    
    # Check if both services are available for integration testing
    if check_service "$BACKEND_URL" "Backend" && check_service "$FRONTEND_URL" "Frontend"; then
        echo ""
        echo "Running integration tests..."
        
        cd "$SCRIPT_DIR"
        export BACKEND_URL
        export FRONTEND_URL
        
        if node user_flow_integration.mjs; then
            echo -e "${GREEN}✅ Integration tests passed${NC}"
            INTEGRATION_PASSED=true
        else
            echo -e "${RED}❌ Integration tests failed${NC}"
            INTEGRATION_PASSED=false
        fi
    else
        echo -e "${YELLOW}⚠️ Skipping integration tests - both services not available${NC}"
        INTEGRATION_PASSED=false
    fi
}

# Function to build necessary components
build_components() {
    echo ""
    echo -e "${YELLOW}🔧 Building Components...${NC}"
    
    # Get the absolute path to the project root
    cd "$SCRIPT_DIR/.."
    
    # Build CLI if it doesn't exist
    if [ ! -f "packages/cli/dist/cli.js" ]; then
        echo "Building CLI package..."
        if yarn workspace monkey-coder-cli build; then
            echo -e "${GREEN}✅ CLI built successfully${NC}"
        else
            echo -e "${RED}❌ CLI build failed${NC}"
        fi
    else
        echo -e "${GREEN}✅ CLI already built${NC}"
    fi
}

# Run all test suites
echo -e "${CYAN}Starting comprehensive smoke test suite...${NC}"

# Build components first
build_components

# Install dependencies if needed
echo "Ensuring Python dependencies are available..."
if ! python3 -c "import httpx" 2>/dev/null; then
    echo "Installing httpx for backend tests..."
    pip3 install httpx || echo "Warning: Could not install httpx"
fi

# Run test suites
run_backend_tests
run_frontend_tests  
run_cli_tests
run_integration_tests

# Summary
echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}📋 COMPREHENSIVE TEST SUMMARY${NC}"
echo -e "${CYAN}============================================${NC}"

# Count results
PASSED_COUNT=0
TOTAL_COUNT=4

if [ "$BACKEND_PASSED" = true ]; then
    echo -e "${GREEN}✅ Backend API Tests: PASSED${NC}"
    ((PASSED_COUNT++))
else
    echo -e "${RED}❌ Backend API Tests: FAILED${NC}"
fi

if [ "$FRONTEND_PASSED" = true ]; then
    echo -e "${GREEN}✅ Frontend Route Tests: PASSED${NC}"
    ((PASSED_COUNT++))
else
    echo -e "${RED}❌ Frontend Route Tests: FAILED${NC}"
fi

if [ "$CLI_PASSED" = true ]; then
    echo -e "${GREEN}✅ CLI Tests: PASSED${NC}"
    ((PASSED_COUNT++))
else
    echo -e "${RED}❌ CLI Tests: FAILED${NC}"
fi

if [ "$INTEGRATION_PASSED" = true ]; then
    echo -e "${GREEN}✅ Integration Tests: PASSED${NC}"
    ((PASSED_COUNT++))
else
    echo -e "${RED}❌ Integration Tests: FAILED${NC}"
fi

echo ""
echo -e "${BLUE}Total: $PASSED_COUNT/$TOTAL_COUNT test suites passed${NC}"

# Generate JSON report
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
cat > smoke_test_results.json << EOF
{
    "timestamp": "$TIMESTAMP",
    "backend_url": "$BACKEND_URL",
    "frontend_url": "$FRONTEND_URL",
    "results": {
        "backend": $BACKEND_PASSED,
        "frontend": $FRONTEND_PASSED,
        "cli": $CLI_PASSED,
        "integration": $INTEGRATION_PASSED
    },
    "summary": {
        "total_suites": $TOTAL_COUNT,
        "passed_suites": $PASSED_COUNT,
        "success_rate": $(echo "scale=2; $PASSED_COUNT * 100 / $TOTAL_COUNT" | bc -l)
    }
}
EOF

echo -e "${BLUE}📄 Results saved to: smoke_test_results.json${NC}"

# Exit with appropriate code
if [ $PASSED_COUNT -eq $TOTAL_COUNT ]; then
    echo -e "${GREEN}🎉 All smoke tests passed!${NC}"
    exit 0
else
    echo -e "${RED}💥 Some smoke tests failed.${NC}"
    exit 1
fi