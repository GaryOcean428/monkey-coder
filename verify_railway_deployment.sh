#!/bin/bash
set -e

echo "🔍 Railway Deployment Verification Script"
echo "=========================================="

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "   Current Python: $python_version"
if [[ "$python_version" == "3.13" ]]; then
    echo "   ✅ Python 3.13 detected (matches railpack.json)"
elif [[ "$python_version" == "3.12" ]]; then
    echo "   ⚠️ Python 3.12 detected (railpack.json specifies 3.13)"
    echo "   This may cause deployment issues on Railway"
else
    echo "   ❌ Unsupported Python version"
    exit 1
fi

# Check Yarn version
echo ""
echo "📋 Checking Yarn version..."
if command -v yarn &> /dev/null; then
    yarn_version=$(yarn --version)
    echo "   Current Yarn: $yarn_version"
    if [[ "$yarn_version" == "4.9.2" ]]; then
        echo "   ✅ Yarn 4.9.2 detected (matches railpack.json)"
    else
        echo "   ⚠️ Yarn $yarn_version detected (railpack.json expects 4.9.2)"
        echo "   Setting up Yarn 4.9.2 via corepack..."
        corepack enable
        corepack prepare yarn@4.9.2 --activate
        echo "   ✅ Yarn 4.9.2 activated"
    fi
else
    echo "   ❌ Yarn not found"
    exit 1
fi

# Check Node version
echo ""
echo "📋 Checking Node.js version..."
node_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
echo "   Current Node: v$(node --version | cut -d'v' -f2)"
if [[ "$node_version" -ge "20" ]]; then
    echo "   ✅ Node.js 20+ detected (matches railpack.json)"
else
    echo "   ❌ Node.js 20+ required"
    exit 1
fi

# Check if frontend build exists
echo ""
echo "📋 Checking frontend build..."
if [ -d "packages/web/out" ]; then
    file_count=$(ls -1 packages/web/out | wc -l)
    echo "   ✅ Frontend build found with $file_count files"
    
    # Check for critical files
    if [ -f "packages/web/out/index.html" ]; then
        echo "   ✅ index.html found"
    else
        echo "   ❌ index.html missing"
    fi
    
    if [ -d "packages/web/out/_next" ]; then
        echo "   ✅ _next directory found"
    else
        echo "   ❌ _next directory missing"
    fi
else
    echo "   ❌ Frontend build directory not found"
    echo "   Run: yarn workspace @monkey-coder/web export"
    exit 1
fi

# Validate railpack.json syntax
echo ""
echo "📋 Validating railpack.json..."
if command -v jq &> /dev/null; then
    if jq '.' railpack.json > /dev/null 2>&1; then
        echo "   ✅ railpack.json syntax valid"
    else
        echo "   ❌ railpack.json syntax invalid"
        exit 1
    fi
else
    echo "   ⚠️ jq not available, skipping JSON validation"
fi

# Check critical environment variables
echo ""
echo "📋 Checking environment configuration..."
if [ -f ".env.railway.template" ]; then
    echo "   ✅ Railway environment template found"
else
    echo "   ❌ Railway environment template missing"
fi

if [ -f ".env.railway" ]; then
    echo "   ✅ Railway environment file found"
else
    echo "   ⚠️ Railway environment file not found (expected for local dev)"
fi

# Test basic Python imports
echo ""
echo "📋 Testing Python imports..."
python3 -c "import fastapi; print('   ✅ FastAPI available')" 2>/dev/null || echo "   ❌ FastAPI not available"
python3 -c "import uvicorn; print('   ✅ Uvicorn available')" 2>/dev/null || echo "   ❌ Uvicorn not available" 
python3 -c "import pydantic; print('   ✅ Pydantic available')" 2>/dev/null || echo "   ❌ Pydantic not available"
python3 -c "import numpy; print('   ✅ NumPy available')" 2>/dev/null || echo "   ❌ NumPy not available"

# Check health endpoint structure
echo ""
echo "📋 Checking health endpoint implementation..."
if [ -f "packages/core/monkey_coder/app/main.py" ]; then
    if grep -q "@app.get(\"/health\"" packages/core/monkey_coder/app/main.py; then
        echo "   ✅ /health endpoint found"
    else
        echo "   ❌ /health endpoint not found"
    fi
    
    if grep -q "@app.get(\"/healthz\"" packages/core/monkey_coder/app/main.py; then
        echo "   ✅ /healthz endpoint found"
    else
        echo "   ⚠️ /healthz endpoint not found (optional)"
    fi
else
    echo "   ❌ Main FastAPI app not found"
fi

echo ""
echo "🎯 Deployment Readiness Summary"
echo "==============================="
echo "✅ = Ready  ⚠️ = Warning  ❌ = Critical Issue"
echo ""
echo "🚀 Next Steps for Railway Deployment:"
echo "1. Fix any ❌ critical issues above"
echo "2. Set environment variables in Railway dashboard"
echo "3. Deploy using: railway up --force"
echo "4. Monitor deployment with: railway logs --tail"
echo ""
echo "📋 Post-deployment verification:"
echo "curl https://your-app.railway.app/health"
echo "curl https://your-app.railway.app/api/v1/capabilities"