#!/bin/bash

# Railway Deployment Readiness Check
# Quick pre-deployment validation

echo "🔍 Railway Deployment Readiness Check"
echo "===================================="

READY=true

# Check railpack.json exists and is valid
if [ ! -f "railpack.json" ]; then
    echo "❌ railpack.json not found"
    READY=false
elif ! jq '.' railpack.json > /dev/null 2>&1; then
    echo "❌ railpack.json has invalid JSON"
    READY=false
else
    echo "✅ railpack.json exists and is valid"
fi

# Check for competing build files
COMPETING=0
for file in Dockerfile railway.toml railway.json nixpacks.toml; do
    if [ -f "$file" ] && [ "$file" != "services/*/Dockerfile" ]; then
        echo "❌ Found competing build file: $file"
        COMPETING=$((COMPETING + 1))
        READY=false
    fi
done

if [ $COMPETING -eq 0 ]; then
    echo "✅ No competing build files found"
fi

# Check health endpoint
if [ -f "railpack.json" ] && jq '.deploy.healthCheckPath' railpack.json | grep -q '"/health"'; then
    echo "✅ Health check configured"
else
    echo "⚠️  Health check not configured"
fi

# Final verdict
echo ""
if [ "$READY" = true ]; then
    echo "✅ READY FOR RAILWAY DEPLOYMENT!"
    exit 0
else
    echo "❌ NOT READY - Please fix issues above"
    exit 1
fi
