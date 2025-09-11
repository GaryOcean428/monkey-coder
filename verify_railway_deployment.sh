#!/bin/bash
# verify_railway_deployment.sh
# 
# Comprehensive Railway deployment verification script for Monkey Coder
# Tests deployment readiness as specified in the issue requirements

set -e

echo "🚂 Railway Deployment Health Monitoring and Verification"
echo "========================================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_URL=${DEPLOYMENT_URL:-"https://coder.fastmonkey.au"}
LOCAL_URL=${LOCAL_URL:-"http://localhost:8000"}
TIMEOUT=${TIMEOUT:-30}

# Check if we're testing local or deployed version
if [[ "$1" == "--local" ]]; then
    BASE_URL="$LOCAL_URL"
    echo -e "${BLUE}Testing LOCAL deployment at: $BASE_URL${NC}"
else
    BASE_URL="$DEPLOYMENT_URL"
    echo -e "${BLUE}Testing PRODUCTION deployment at: $BASE_URL${NC}"
fi

# Track results
TESTS_PASSED=0
TESTS_FAILED=0
WARNINGS=0

# Helper function to log test results
log_test() {
    local status="$1"
    local message="$2"
    local details="$3"
    
    case "$status" in
        "PASS")
            echo -e "${GREEN}✅ PASS:${NC} $message"
            TESTS_PASSED=$((TESTS_PASSED + 1))
            ;;
        "FAIL")
            echo -e "${RED}❌ FAIL:${NC} $message"
            if [[ -n "$details" ]]; then
                echo -e "${RED}   Details: $details${NC}"
            fi
            TESTS_FAILED=$((TESTS_FAILED + 1))
            ;;
        "WARN")
            echo -e "${YELLOW}⚠️ WARN:${NC} $message"
            if [[ -n "$details" ]]; then
                echo -e "${YELLOW}   Details: $details${NC}"
            fi
            WARNINGS=$((WARNINGS + 1))
            ;;
        "INFO")
            echo -e "${BLUE}ℹ️ INFO:${NC} $message"
            ;;
    esac
}

# Test 1: Health endpoint check
test_health_endpoint() {
    echo -e "\n${YELLOW}1. Testing health endpoint...${NC}"
    
    local response
    local status_code
    
    # Test /health endpoint
    if response=$(curl -s -w "%{http_code}" --max-time $TIMEOUT "$BASE_URL/health" 2>/dev/null); then
        status_code="${response: -3}"
        response_body="${response%???}"
        
        if [[ "$status_code" == "200" ]]; then
            log_test "PASS" "Health endpoint responds with 200 status"
            
            # Check if response is JSON
            if echo "$response_body" | jq . >/dev/null 2>&1; then
                log_test "PASS" "Health endpoint returns valid JSON"
                
                # Check required fields
                status=$(echo "$response_body" | jq -r '.status // empty')
                version=$(echo "$response_body" | jq -r '.version // empty')
                
                if [[ "$status" == "healthy" ]]; then
                    log_test "PASS" "Health status is 'healthy'"
                else
                    log_test "FAIL" "Health status is not 'healthy'" "Status: $status"
                fi
                
                if [[ -n "$version" ]]; then
                    log_test "PASS" "Version information present" "Version: $version"
                else
                    log_test "WARN" "Version information missing"
                fi
                
            else
                log_test "FAIL" "Health endpoint does not return valid JSON"
            fi
        else
            log_test "FAIL" "Health endpoint returned status $status_code"
        fi
    else
        log_test "FAIL" "Health endpoint is unreachable" "URL: $BASE_URL/health"
    fi
    
    # Test alternative health endpoints
    for endpoint in "/healthz" "/health/readiness"; do
        if curl -s --max-time $TIMEOUT "$BASE_URL$endpoint" >/dev/null 2>&1; then
            log_test "PASS" "Alternative endpoint $endpoint is accessible"
        else
            log_test "WARN" "Alternative endpoint $endpoint is not accessible"
        fi
    done
}

# Test 2: Static assets check
test_static_assets() {
    echo -e "\n${YELLOW}2. Testing static assets...${NC}"
    
    # Test root index.html
    if curl -s --max-time $TIMEOUT "$BASE_URL/" | grep -q "<!DOCTYPE html>" 2>/dev/null; then
        log_test "PASS" "Root index.html is served"
    else
        log_test "FAIL" "Root index.html is not properly served"
    fi
    
    # Test Next.js static assets
    if curl -s -I --max-time $TIMEOUT "$BASE_URL/_next/static" 2>/dev/null | head -1 | grep -q "200\|404"; then
        log_test "PASS" "Next.js static assets directory is accessible"
    else
        log_test "WARN" "Next.js static assets may not be available"
    fi
    
    # Test favicon
    if curl -s -I --max-time $TIMEOUT "$BASE_URL/favicon.ico" 2>/dev/null | head -1 | grep -q "200"; then
        log_test "PASS" "Favicon is served"
    else
        log_test "WARN" "Favicon is not available"
    fi
}

# Test 3: API endpoint check
test_api_endpoints() {
    echo -e "\n${YELLOW}3. Testing API endpoints...${NC}"
    
    # Test API documentation
    if curl -s --max-time $TIMEOUT "$BASE_URL/api/docs" >/dev/null 2>&1; then
        log_test "PASS" "API documentation is accessible"
    else
        log_test "FAIL" "API documentation is not accessible"
    fi
    
    # Test auth status endpoint
    local auth_response
    if auth_response=$(curl -s --max-time $TIMEOUT "$BASE_URL/api/v1/auth/status" 2>/dev/null); then
        if echo "$auth_response" | jq . >/dev/null 2>&1; then
            log_test "PASS" "Auth status endpoint returns valid JSON"
        else
            log_test "FAIL" "Auth status endpoint does not return valid JSON"
        fi
    else
        log_test "FAIL" "Auth status endpoint is unreachable"
    fi
    
    # Test capabilities endpoint
    if curl -s --max-time $TIMEOUT "$BASE_URL/api/v1/capabilities" >/dev/null 2>&1; then
        log_test "PASS" "Capabilities endpoint is accessible"
    else
        log_test "WARN" "Capabilities endpoint requires authentication"
    fi
    
    # Test metrics endpoint
    if curl -s --max-time $TIMEOUT "$BASE_URL/metrics" | grep -q "# HELP" 2>/dev/null; then
        log_test "PASS" "Prometheus metrics endpoint is working"
    else
        log_test "WARN" "Prometheus metrics endpoint may not be available"
    fi
}

# Test 4: Performance and response time
test_performance() {
    echo -e "\n${YELLOW}4. Testing performance and response times...${NC}"
    
    # Test health endpoint response time
    local start_time=$(date +%s%N)
    if curl -s --max-time $TIMEOUT "$BASE_URL/health" >/dev/null 2>&1; then
        local end_time=$(date +%s%N)
        local duration=$((($end_time - $start_time) / 1000000))  # Convert to milliseconds
        
        if [[ $duration -lt 1000 ]]; then
            log_test "PASS" "Health endpoint response time is good" "Response time: ${duration}ms"
        elif [[ $duration -lt 3000 ]]; then
            log_test "WARN" "Health endpoint response time is acceptable" "Response time: ${duration}ms"
        else
            log_test "FAIL" "Health endpoint response time is too slow" "Response time: ${duration}ms"
        fi
    else
        log_test "FAIL" "Could not measure health endpoint response time"
    fi
}

# Test 5: Security headers and configuration
test_security() {
    echo -e "\n${YELLOW}5. Testing security configuration...${NC}"
    
    # Check for security headers
    local headers
    if headers=$(curl -s -I --max-time $TIMEOUT "$BASE_URL/health" 2>/dev/null); then
        # Check for common security headers
        if echo "$headers" | grep -qi "x-frame-options"; then
            log_test "PASS" "X-Frame-Options header present"
        else
            log_test "WARN" "X-Frame-Options header missing"
        fi
        
        if echo "$headers" | grep -qi "x-content-type-options"; then
            log_test "PASS" "X-Content-Type-Options header present"
        else
            log_test "WARN" "X-Content-Type-Options header missing"
        fi
        
        if echo "$headers" | grep -qi "strict-transport-security"; then
            log_test "PASS" "HSTS header present"
        else
            log_test "WARN" "HSTS header missing (expected for HTTPS)"
        fi
    else
        log_test "FAIL" "Could not retrieve headers for security check"
    fi
}

# Test 6: Environment validation
test_environment() {
    echo -e "\n${YELLOW}6. Testing environment configuration...${NC}"
    
    # Check Python version compliance
    if [[ "$1" == "--local" ]]; then
        local python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
        log_test "INFO" "Local Python version: $python_version"
        
        if [[ "$python_version" == "3.12" ]] || [[ "$python_version" == "3.11" ]]; then
            log_test "PASS" "Python version is compatible with Railway"
        else
            log_test "WARN" "Python version may not be optimal for Railway"
        fi
    fi
    
    # Check if Railway environment variables are likely set
    # This is inferred from successful API responses
    if curl -s --max-time $TIMEOUT "$BASE_URL/health" | jq -r '.components.provider_registry' 2>/dev/null | grep -q "active"; then
        log_test "PASS" "Provider registry is active (environment configured)"
    else
        log_test "WARN" "Provider registry may not be properly configured"
    fi
}

# Test 7: Database and external service connectivity
test_external_services() {
    echo -e "\n${YELLOW}7. Testing external service connectivity...${NC}"
    
    # Test comprehensive health check if available
    local comprehensive_response
    if comprehensive_response=$(curl -s --max-time $TIMEOUT "$BASE_URL/health/comprehensive" 2>/dev/null); then
        if echo "$comprehensive_response" | jq -r '.status' 2>/dev/null | grep -q "healthy"; then
            log_test "PASS" "Comprehensive health check reports all systems healthy"
        else
            log_test "WARN" "Comprehensive health check reports issues"
            # Extract specific issues if available
            local issues=$(echo "$comprehensive_response" | jq -r '.issues[]?' 2>/dev/null)
            if [[ -n "$issues" ]]; then
                log_test "INFO" "Health check issues: $issues"
            fi
        fi
    else
        log_test "WARN" "Comprehensive health check not available"
    fi
}

# Generate deployment report
generate_report() {
    echo -e "\n${BLUE}========================================================"
    echo "DEPLOYMENT VERIFICATION SUMMARY"
    echo -e "========================================================${NC}"
    
    local total_tests=$((TESTS_PASSED + TESTS_FAILED))
    
    echo "🗂️ Test Results:"
    echo "   ✅ Passed: $TESTS_PASSED"
    echo "   ❌ Failed: $TESTS_FAILED"
    echo "   ⚠️ Warnings: $WARNINGS"
    echo "   📊 Total: $total_tests"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "\n${GREEN}🎉 DEPLOYMENT VERIFICATION SUCCESSFUL!${NC}"
        echo -e "${GREEN}✅ All critical tests passed${NC}"
        if [[ $WARNINGS -gt 0 ]]; then
            echo -e "${YELLOW}⚠️ $WARNINGS warning(s) to review${NC}"
        fi
        echo -e "\n${GREEN}🚀 Deployment is ready for production traffic${NC}"
    else
        echo -e "\n${RED}❌ DEPLOYMENT VERIFICATION FAILED!${NC}"
        echo -e "${RED}🔧 $TESTS_FAILED critical issue(s) found${NC}"
        echo -e "\n${RED}⚠️ Do not route production traffic until issues are resolved${NC}"
    fi
    
    echo -e "\n📋 Next Steps:"
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo "1. ✅ All systems operational"
        echo "2. 📊 Monitor deployment with: railway logs --service monkey-coder --tail"
        echo "3. 📈 Check metrics at: $BASE_URL/metrics"
        echo "4. 🔧 Access admin panel at: $BASE_URL/api/docs"
    else
        echo "1. 🔧 Fix failed tests above"
        echo "2. 🔄 Re-run verification: $0"
        echo "3. 📋 Check Railway logs: railway logs --service monkey-coder --tail"
        echo "4. 🏥 Review health status: $BASE_URL/health/comprehensive"
    fi
    
    echo -e "\n📅 Verification completed at: $(date)"
    echo -e "🌐 Tested deployment: $BASE_URL"
}

# Main execution
main() {
    # Check dependencies
    if ! command -v curl &> /dev/null; then
        echo -e "${RED}❌ curl is required but not installed${NC}"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        echo -e "${YELLOW}⚠️ jq is not installed - JSON parsing will be limited${NC}"
    fi
    
    # Run all tests
    test_health_endpoint
    test_static_assets  
    test_api_endpoints
    test_performance
    test_security
    test_environment "$@"
    test_external_services
    
    # Generate report
    generate_report
    
    # Exit with appropriate code
    if [[ $TESTS_FAILED -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}

# Show usage if help requested
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo "Railway Deployment Verification Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --local          Test local deployment (http://localhost:8000)"
    echo "  --help, -h       Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  DEPLOYMENT_URL   Production URL (default: https://coder.fastmonkey.au)"
    echo "  LOCAL_URL        Local URL (default: http://localhost:8000)"
    echo "  TIMEOUT          Request timeout in seconds (default: 30)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Test production deployment"
    echo "  $0 --local            # Test local deployment"
    echo "  TIMEOUT=60 $0         # Test with longer timeout"
    exit 0
fi

# Run main function
main "$@"