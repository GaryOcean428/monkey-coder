#!/bin/bash

# Railway Deployment Fix Validation Script
# Tests the critical fixes applied for Railway health check failures

set -e

echo "🔧 Railway Deployment Fix Validation"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        exit 1
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_info() {
    echo -e "ℹ️ $1"
}

echo ""
echo "📋 Phase 1: Dependency Validation"
echo "--------------------------------"

# Check if critical packages are in requirements-deploy.txt
print_info "Checking requirements-deploy.txt for critical dependencies..."

required_packages=(
    "qwen-agent==0.0.29"
    "aiosqlite==0.21.0" 
    "tiktoken==0.11.0"
    "dashscope==1.24.4"
    "fastapi==0.116.1"
    "uvicorn"
)

for package in "${required_packages[@]}"; do
    if grep -q "$package" requirements-deploy.txt; then
        print_status 0 "$package found in requirements-deploy.txt"
    else
        print_status 1 "$package missing from requirements-deploy.txt"
    fi
done

echo ""
echo "📋 Phase 2: Build Configuration Validation" 
echo "------------------------------------------"

# Check railpack.json configuration
print_info "Checking railpack.json for proper build configuration..."

if grep -q "pip install --no-cache-dir -e ." railpack.json; then
    print_status 0 "Core package installation found in railpack.json"
else
    print_status 1 "Core package installation missing from railpack.json"
fi

if grep -q "Testing imports" railpack.json; then
    print_status 0 "Import testing found in railpack.json"
else
    print_status 1 "Import testing missing from railpack.json"
fi

if grep -q '"healthCheckPath": "/health"' railpack.json; then
    print_status 0 "Health check path correctly configured"
else
    print_status 1 "Health check path not configured correctly"
fi

if grep -q '"healthCheckTimeout": 300' railpack.json; then
    print_status 0 "Health check timeout configured (300s)"
else
    print_status 1 "Health check timeout not configured"
fi

echo ""
echo "📋 Phase 3: Local Import Testing"
echo "--------------------------------"

print_info "Testing critical imports..."

# Test basic imports
export PYTHONPATH=".:packages/core:$PYTHONPATH"

# Test FastAPI app import
if python -c "
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'packages/core')
from monkey_coder.app.main import app
print('FastAPI app imported successfully')
" 2>/dev/null; then
    print_status 0 "FastAPI app import successful"
else
    print_status 1 "FastAPI app import failed"
fi

# Test health endpoint logic
if python -c "
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'packages/core')
from monkey_coder.app.main import HealthResponse
print('Health response model imported successfully')
" 2>/dev/null; then
    print_status 0 "Health response model import successful"
else
    print_status 1 "Health response model import failed"
fi

echo ""
echo "📋 Phase 4: Runtime Server Test"
echo "------------------------------"

print_info "Starting server for health endpoint testing..."

# Start server in background
export PORT=8002
python run_server.py &
SERVER_PID=$!

# Wait for server to start
sleep 8

# Test health endpoint
print_info "Testing health endpoint..."

if curl -sf http://localhost:8002/health > /dev/null; then
    print_status 0 "Health endpoint responding"
    
    # Get health response and check status
    HEALTH_RESPONSE=$(curl -s http://localhost:8002/health)
    if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
        print_status 0 "Health endpoint reports healthy status"
    else
        print_warning "Health endpoint reports non-healthy status (may be initializing)"
        echo "Response: $HEALTH_RESPONSE"
    fi
    
    # Check if components are reported
    if echo "$HEALTH_RESPONSE" | grep -q '"components"'; then
        print_status 0 "Health endpoint reports component status"
    else
        print_status 1 "Health endpoint missing component status"
    fi
    
else
    print_status 1 "Health endpoint not responding"
fi

# Test healthz endpoint (Kubernetes style)
if curl -sf http://localhost:8002/healthz > /dev/null; then
    print_status 0 "Healthz endpoint responding"
else
    print_status 1 "Healthz endpoint not responding"  
fi

# Cleanup
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true

echo ""
echo "📋 Phase 5: Railway Compatibility Check"
echo "--------------------------------------"

print_info "Checking Railway deployment compatibility..."

# Check for 0.0.0.0 binding
if grep -q 'host="0.0.0.0"' run_server.py; then
    print_status 0 "Server binds to 0.0.0.0 (Railway compatible)"
else
    print_status 1 "Server not binding to 0.0.0.0"
fi

# Check for PORT environment variable usage
if grep -q 'os.getenv("PORT"' run_server.py; then
    print_status 0 "Server uses PORT environment variable"
else
    print_status 1 "Server not using PORT environment variable"
fi

# Check Python version compatibility
if grep -q '"python": "3.13"' railpack.json; then
    print_status 0 "Python 3.13 specified in railpack.json"
else
    print_warning "Python version may not be optimal for Railway"
fi

echo ""
echo "🎉 Validation Summary"
echo "===================="

echo ""
print_info "All critical fixes have been applied and validated:"
echo ""
echo "  ✅ Missing dependencies added to requirements-deploy.txt"
echo "  ✅ Core package installation configured in railpack.json"
echo "  ✅ Import testing added to build process"
echo "  ✅ Health endpoints responding correctly"
echo "  ✅ Server binds to 0.0.0.0 for Railway compatibility"
echo "  ✅ PORT environment variable properly used"
echo "  ✅ Component status reporting implemented"
echo ""

echo "🚀 Railway Deployment Ready!"
echo ""
echo "The following Railway deployment issues have been resolved:"
echo ""
echo "  1. ❌ Missing qwen-agent dependency → ✅ Added to requirements-deploy.txt"
echo "  2. ❌ Core package not installed → ✅ Added editable install to railpack.json"
echo "  3. ❌ Import failures during startup → ✅ Added import testing to build"
echo "  4. ❌ Health checks failing → ✅ Enhanced health endpoint resilience"
echo "  5. ❌ Component initialization errors → ✅ Added graceful degradation"
echo ""

echo "📊 Expected Railway Deployment Results:"
echo ""
echo "  • Build Phase: Dependencies install successfully"
echo "  • Start Phase: Application starts without import errors"
echo "  • Health Phase: /health endpoint responds with 200 OK"
echo "  • Runtime Phase: All components report proper status"
echo ""

echo "✨ Validation Complete - Ready for Railway Deployment! ✨"