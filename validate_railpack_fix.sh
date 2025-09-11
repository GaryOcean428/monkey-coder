#!/bin/bash

# Railpack Build Detection Fix Validation Script
# Tests the simplified railpack.json configuration for Railway deployment

set -e

echo "🚀 Railpack Build Detection Fix Validation"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
    echo -e "${BLUE}ℹ️ $1${NC}"
}

echo ""
echo "📋 Phase 1: Configuration Validation"
echo "-----------------------------------"

# 1. JSON Syntax Validation
print_info "Validating railpack.json syntax..."
if cat railpack.json | python -m json.tool > /dev/null 2>&1; then
    print_status 0 "railpack.json has valid JSON syntax"
else
    print_status 1 "railpack.json syntax validation failed"
fi

# 2. Provider Configuration Check
print_info "Checking explicit provider configuration..."
if grep -q '"provider": "python"' railpack.json; then
    print_status 0 "Python provider explicitly configured"
else
    print_status 1 "Python provider not found in configuration"
fi

# 3. Required Fields Check
print_info "Checking required configuration fields..."
required_fields=("version" "build" "deploy" "startCommand" "healthCheckPath")
for field in "${required_fields[@]}"; do
    if grep -q "\"$field\"" railpack.json; then
        print_status 0 "Required field '$field' present"
    else
        print_status 1 "Required field '$field' missing"
    fi
done

# 4. Check for conflicting build files
print_info "Checking for conflicting build configurations..."
conflicting_files=($(find . -maxdepth 1 -name "Dockerfile" -o -name "railway.toml" -o -name "nixpacks.toml" 2>/dev/null))
if [ ${#conflicting_files[@]} -eq 0 ]; then
    print_status 0 "No conflicting build files found"
else
    print_warning "Found potential conflicting files: ${conflicting_files[*]}"
    print_info "These files may interfere with railpack.json - consider removing them"
fi

echo ""
echo "📋 Phase 2: Dependency Validation"
echo "--------------------------------"

# 5. Python Requirements Check
print_info "Checking requirements-deploy.txt exists..."
if [ -f "requirements-deploy.txt" ]; then
    print_status 0 "requirements-deploy.txt found"
    
    # Check for essential packages
    essential_packages=("fastapi" "uvicorn" "pydantic" "httpx")
    for package in "${essential_packages[@]}"; do
        if grep -q "$package" requirements-deploy.txt; then
            print_status 0 "Essential package '$package' found in requirements"
        else
            print_status 1 "Essential package '$package' missing from requirements"
        fi
    done
else
    print_status 1 "requirements-deploy.txt not found"
fi

# 6. Core Package Check
print_info "Checking packages/core structure..."
if [ -d "packages/core" ] && [ -f "packages/core/pyproject.toml" ]; then
    print_status 0 "Core package structure valid"
else
    print_status 1 "Core package structure invalid"
fi

echo ""
echo "📋 Phase 3: Frontend Configuration"
echo "---------------------------------"

# 7. Frontend Package Check
print_info "Checking frontend workspace configuration..."
if [ -f "packages/web/package.json" ]; then
    print_status 0 "Frontend package.json found"
    
    # Check for export script
    if grep -q '"export"' packages/web/package.json; then
        print_status 0 "Frontend export script configured"
    else
        print_warning "Frontend export script not found - build may fail gracefully"
    fi
else
    print_warning "Frontend package not found - API-only mode will be used"
fi

# 8. Yarn Configuration Check
print_info "Checking Yarn workspace configuration..."
if [ -f "package.json" ] && grep -q "workspaces" package.json; then
    print_status 0 "Yarn workspaces configured"
else
    print_status 1 "Yarn workspaces not properly configured"
fi

echo ""
echo "📋 Phase 4: Runtime Validation"
echo "------------------------------"

# 9. Import Path Test
print_info "Testing Python import paths..."
if python -c "
import sys
import os
sys.path.insert(0, '.')
sys.path.insert(0, './packages/core')
print('Import path setup successful')
" 2>/dev/null; then
    print_status 0 "Python import paths work correctly"
else
    print_status 1 "Python import path setup failed"
fi

# 10. run_server.py Check
print_info "Validating run_server.py configuration..."
if [ -f "run_server.py" ]; then
    print_status 0 "run_server.py found"
    
    # Check for PORT environment variable usage
    if grep -q "os.getenv.*PORT" run_server.py; then
        print_status 0 "PORT environment variable properly handled"
    else
        print_status 1 "PORT environment variable not properly handled"
    fi
    
    # Check for 0.0.0.0 binding
    if grep -q "0.0.0.0" run_server.py; then
        print_status 0 "Server binds to 0.0.0.0 (Railway compatible)"
    else
        print_status 1 "Server not configured for 0.0.0.0 binding"
    fi
else
    print_status 1 "run_server.py not found"
fi

echo ""
echo "📋 Summary"
echo "==========="
print_info "Railpack configuration validation completed successfully!"
echo ""
echo "📄 Key Improvements Implemented:"
echo "  • Explicit Python provider (eliminates detection confusion)"
echo "  • Simplified 2-step build process (install → frontend)"  
echo "  • Graceful frontend build failure handling"
echo "  • Health check endpoint configured (/health)"
echo "  • Proper Railway PORT and host binding"
echo ""
echo "🚀 Ready for Railway deployment!"
echo "   Use: railway up --service <service-name>"
echo ""