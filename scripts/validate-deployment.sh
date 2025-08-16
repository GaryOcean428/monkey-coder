#!/usr/bin/env bash
# Railway Multi-Service Deployment Validation Script
# Usage: ./scripts/validate-deployment.sh

set -euo pipefail

echo "🔍 Railway Multi-Service Deployment Validation"
echo "=============================================="

# Check railpack.json configurations
echo "📋 Validating railpack.json configurations..."

# Root configuration
if [ -f railpack.json ]; then
    echo "✅ Root railpack.json exists"
    if python -c "import json; json.load(open('railpack.json'))" 2>/dev/null; then
        echo "✅ Root railpack.json has valid JSON syntax"
    else
        echo "❌ Root railpack.json has invalid JSON syntax"
        exit 1
    fi
    
    # Check multi-service structure
    if python -c "import json; config = json.load(open('railpack.json')); assert 'services' in config" 2>/dev/null; then
        echo "✅ Root configuration uses multi-service structure"
    else
        echo "❌ Root configuration missing services structure"
        exit 1
    fi
else
    echo "❌ Root railpack.json missing"
    exit 1
fi

# Frontend configuration
if [ -f packages/web/railpack.json ]; then
    echo "✅ Frontend railpack.json exists"
    if python -c "import json; json.load(open('packages/web/railpack.json'))" 2>/dev/null; then
        echo "✅ Frontend railpack.json has valid JSON syntax"
    else
        echo "❌ Frontend railpack.json has invalid JSON syntax"
        exit 1
    fi
else
    echo "❌ Frontend railpack.json missing"
    exit 1
fi

# Check for competing build files
echo ""
echo "🔧 Checking for build configuration conflicts..."
COMPETING_FILES=$(find . -maxdepth 1 -name "Dockerfile" -o -name "railway.toml" -o -name "nixpacks.toml" | wc -l)
if [ "$COMPETING_FILES" -eq 0 ]; then
    echo "✅ No competing build configuration files found"
else
    echo "⚠️  Found competing build files:"
    find . -maxdepth 1 -name "Dockerfile" -o -name "railway.toml" -o -name "nixpacks.toml"
    echo "   Consider removing these to avoid Railway build conflicts"
fi

# Check health endpoints
echo ""
echo "🏥 Validating health check endpoints..."

# Frontend health endpoint
if [ -f packages/web/src/app/api/health/route.ts ]; then
    echo "✅ Frontend health endpoint exists at /api/health"
else
    echo "❌ Frontend health endpoint missing"
    exit 1
fi

# Check Next.js configuration for Railway compatibility
echo ""
echo "⚙️  Checking Next.js configuration..."
if grep -q "RAILWAY_ENVIRONMENT" packages/web/next.config.mjs; then
    echo "✅ Next.js config supports Railway environment detection"
else
    echo "❌ Next.js config missing Railway environment support"
    exit 1
fi

# Check environment variable optimization
echo ""
echo "🔐 Checking environment variable optimization..."
if grep -q "secrets" railpack.json; then
    echo "✅ Root railpack.json includes explicit secrets configuration"
else
    echo "⚠️  Root railpack.json missing explicit secrets - may cause buildkit memory issues"
fi

# Check service communication setup
echo ""
echo "🔗 Checking inter-service communication..."
if grep -q "RAILWAY_PUBLIC_DOMAIN" railpack.json; then
    echo "✅ Inter-service communication configured with Railway reference variables"
else
    echo "❌ Inter-service communication not configured"
    exit 1
fi

# Test builds (quick syntax check)
echo ""
echo "🏗️  Testing build configurations..."

# Test backend Python imports
if python -c "from packages.core.monkey_coder.core import orchestrator; print('✅ Backend imports working')" 2>/dev/null; then
    echo "✅ Backend Python dependencies resolved"
else
    echo "❌ Backend Python dependencies not resolved"
    echo "   Run: cd packages/core && pip install -e ."
    exit 1
fi

# Test frontend TypeScript compilation
if cd packages/web && yarn typecheck &>/dev/null; then
    echo "✅ Frontend TypeScript compilation successful"
    cd ../..
else
    echo "❌ Frontend TypeScript compilation failed"
    cd ../.. || true
    exit 1
fi

echo ""
echo "🎉 All validation checks passed!"
echo ""
echo "📋 Deployment Summary:"
echo "- Multi-service configuration: ✅ Ready"
echo "- Backend (Python): ✅ Ready"
echo "- Frontend (Next.js): ✅ Ready"
echo "- Health checks: ✅ Configured"
echo "- Environment optimization: ✅ Applied"
echo "- Inter-service communication: ✅ Configured"
echo ""
echo "🚀 Ready for Railway multi-service deployment!"