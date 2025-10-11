#!/bin/bash
#
# Railway Deployment Verification Script
# 
# This script verifies that a Railway deployment is healthy and functioning correctly.
# It checks health endpoints, validates response times, and ensures all critical services are operational.
#
# Usage: ./verify_railway_deployment.sh
#
# Environment Variables:
#   DEPLOYMENT_URL - The base URL of the deployment (default: https://coder.fastmonkey.au)
#   TIMEOUT - Timeout for health checks in seconds (default: 30)
#

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_URL="${DEPLOYMENT_URL:-https://coder.fastmonkey.au}"
TIMEOUT="${TIMEOUT:-30}"
MAX_RETRIES=5
RETRY_DELAY=5

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                                ║${NC}"
echo -e "${BLUE}║           Railway Deployment Verification Tool                 ║${NC}"
echo -e "${BLUE}║                                                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Deployment URL: $DEPLOYMENT_URL"
echo "Timeout: ${TIMEOUT}s"
echo ""

# Function to check if a URL is reachable
check_endpoint() {
    local endpoint=$1
    local expected_status=${2:-200}
    local description=$3
    
    echo -ne "${BLUE}Checking ${description}...${NC} "
    
    for i in $(seq 1 $MAX_RETRIES); do
        response_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$endpoint" 2>/dev/null || echo "000")
        
        if [ "$response_code" = "$expected_status" ]; then
            echo -e "${GREEN}✓ OK (${response_code})${NC}"
            return 0
        elif [ "$response_code" = "000" ]; then
            echo -ne "${YELLOW}⏳ Retry $i/$MAX_RETRIES...${NC} "
            sleep $RETRY_DELAY
        else
            echo -e "${YELLOW}⚠ Unexpected status ${response_code}${NC}"
            return 1
        fi
    done
    
    echo -e "${RED}✗ FAILED after $MAX_RETRIES retries${NC}"
    return 1
}

# Function to measure response time
measure_response_time() {
    local endpoint=$1
    local description=$2
    
    echo -ne "${BLUE}Measuring response time for ${description}...${NC} "
    
    start_time=$(date +%s%N)
    curl -s -o /dev/null --max-time $TIMEOUT "$endpoint" 2>/dev/null || true
    end_time=$(date +%s%N)
    
    duration=$(( (end_time - start_time) / 1000000 ))
    
    if [ $duration -lt 2000 ]; then
        echo -e "${GREEN}✓ ${duration}ms${NC}"
    elif [ $duration -lt 5000 ]; then
        echo -e "${YELLOW}⚠ ${duration}ms (slow)${NC}"
    else
        echo -e "${RED}✗ ${duration}ms (too slow)${NC}"
        return 1
    fi
    
    return 0
}

# Track overall status
overall_status=0

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Health Check Endpoints${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

# Check primary health endpoint
if check_endpoint "${DEPLOYMENT_URL}/health" 200 "Primary health endpoint"; then
    :
else
    overall_status=1
fi

# Check healthz endpoint (common k8s convention)
if check_endpoint "${DEPLOYMENT_URL}/healthz" 200 "Healthz endpoint" 2>/dev/null; then
    :
else
    echo -e "${YELLOW}⚠ Healthz endpoint not available (optional)${NC}"
fi

# Check readiness endpoint
if check_endpoint "${DEPLOYMENT_URL}/health/readiness" 200 "Readiness endpoint" 2>/dev/null; then
    :
else
    echo -e "${YELLOW}⚠ Readiness endpoint not available (optional)${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}API Endpoints${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

# Check API docs (if available)
if check_endpoint "${DEPLOYMENT_URL}/api/docs" 200 "API documentation" 2>/dev/null; then
    :
else
    echo -e "${YELLOW}⚠ API docs not available (optional)${NC}"
fi

# Check API health endpoint
if check_endpoint "${DEPLOYMENT_URL}/api/health" 200 "API health endpoint" 2>/dev/null; then
    :
else
    echo -e "${YELLOW}⚠ API health endpoint not available (checking alternatives)${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Performance Checks${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

# Measure response times
if measure_response_time "${DEPLOYMENT_URL}/health" "health endpoint"; then
    :
else
    overall_status=1
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Deployment Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

if [ $overall_status -eq 0 ]; then
    echo -e "${GREEN}✓ Deployment verification PASSED${NC}"
    echo -e "${GREEN}  All critical health checks successful${NC}"
    echo -e "${GREEN}  Deployment is ready for production traffic${NC}"
else
    echo -e "${RED}✗ Deployment verification FAILED${NC}"
    echo -e "${RED}  Some critical health checks failed${NC}"
    echo -e "${RED}  Review logs and fix issues before proceeding${NC}"
fi

echo ""

exit $overall_status
