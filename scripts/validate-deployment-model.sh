#!/bin/bash

# Railway Deployment Model Validator
# Ensures repository correctly uses Railway's railpack system, not Docker

echo "🔍 Validating Railway Deployment Model..."
echo "========================================"

VALID=true

# 1. Check that railpack.json exists and is valid
echo -e "\n1. Checking railpack.json..."
if [ ! -f "railpack.json" ]; then
    echo "❌ ERROR: railpack.json not found!"
    echo "   Railway deployment requires railpack.json configuration"
    VALID=false
else
    echo "✅ railpack.json exists"
    
    # Validate JSON syntax
    if jq '.' railpack.json > /dev/null 2>&1; then
        echo "✅ railpack.json has valid JSON syntax"
    else
        echo "❌ ERROR: railpack.json has invalid JSON syntax"
        VALID=false
    fi
fi

# 2. Check that no competing build files exist in root
echo -e "\n2. Checking for competing build files..."
COMPETING_FILES=()

if [ -f "Dockerfile" ]; then
    COMPETING_FILES+=("Dockerfile")
fi
if [ -f "railway.toml" ]; then
    COMPETING_FILES+=("railway.toml")
fi
if [ -f "railway.json" ]; then
    COMPETING_FILES+=("railway.json")
fi
if [ -f "nixpacks.toml" ]; then
    COMPETING_FILES+=("nixpacks.toml")
fi

if [ ${#COMPETING_FILES[@]} -gt 0 ]; then
    echo "❌ ERROR: Found competing build files:"
    for file in "${COMPETING_FILES[@]}"; do
        echo "   - $file"
    done
    echo "   Remove these files to use railpack.json for Railway deployment"
    VALID=false
else
    echo "✅ No competing build files found"
fi

# 3. Verify .dockerignore exists (needed for Railway's internal Docker process)
echo -e "\n3. Checking .dockerignore..."
if [ ! -f ".dockerignore" ]; then
    echo "❌ WARNING: .dockerignore not found"
    echo "   Railway's internal build process uses Docker and needs .dockerignore"
else
    echo "✅ .dockerignore exists (required for Railway's internal build)"
fi

# 4. Check services/sandbox/Dockerfile (should exist as separate service)
echo -e "\n4. Checking sandbox service..."
if [ -f "services/sandbox/Dockerfile" ]; then
    echo "✅ services/sandbox/Dockerfile exists (separate optional service)"
else
    echo "ℹ️  services/sandbox/Dockerfile not found (optional)"
fi

# 5. Validate Docker scripts are marked as local testing only
echo -e "\n5. Checking Docker scripts..."
if [ -f "scripts/build-docker.sh" ]; then
    if grep -q "LOCAL.*TESTING.*ONLY" scripts/build-docker.sh; then
        echo "✅ build-docker.sh correctly marked as local testing only"
    else
        echo "⚠️  build-docker.sh should be marked as local testing only"
    fi
else
    echo "ℹ️  scripts/build-docker.sh not found"
fi

# 6. Verify health check configuration
echo -e "\n6. Checking health check configuration..."
if [ -f "railpack.json" ] && jq -e '.deploy.healthCheckPath' railpack.json > /dev/null 2>&1; then
    HEALTH_PATH=$(jq -r '.deploy.healthCheckPath' railpack.json)
    echo "✅ Health check configured at: $HEALTH_PATH"
else
    echo "⚠️  No health check path configured in railpack.json"
fi

# Summary
echo -e "\n========================================"
if [ "$VALID" = true ]; then
    echo "✅ VALIDATION PASSED"
    echo ""
    echo "Repository correctly configured for Railway deployment:"
    echo "• Uses railpack.json as primary build configuration"
    echo "• No competing Docker/Railway build files"
    echo "• Railway will automatically create containers internally"
    echo "• .dockerignore controls Railway's internal build process"
    echo ""
    echo "Ready to deploy with: railway deploy"
else
    echo "❌ VALIDATION FAILED"
    echo ""
    echo "Issues found that need to be resolved before Railway deployment."
    echo "See errors above for details."
    echo ""
    echo "Deployment Model Reference:"
    echo "https://github.com/GaryOcean428/monkey-coder/blob/main/docs/deployment/railway-architecture.md"
    exit 1
fi