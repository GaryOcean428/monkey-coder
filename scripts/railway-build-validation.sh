#!/bin/bash

# Railway Build Configuration Validation Script
# Prevents build system conflicts by ensuring only one build config exists

echo "🔍 Checking for competing Railway build configurations..."

# Check for competing build files
COMPETING_FILES=()
if [ -f "railway.json" ]; then
    COMPETING_FILES+=("railway.json")
fi
if [ -f "Dockerfile" ]; then
    COMPETING_FILES+=("Dockerfile")
fi
if [ -f "railway.toml" ]; then
    COMPETING_FILES+=("railway.toml")
fi
if [ -f "nixpacks.toml" ]; then
    COMPETING_FILES+=("nixpacks.toml")
fi

# Check if railpack.json exists
if [ ! -f "railpack.json" ]; then
    echo "❌ ERROR: railpack.json not found!"
    echo "   This project requires railpack.json for Railway deployment."
    exit 1
fi

# Validate railpack.json syntax
if ! jq '.' railpack.json > /dev/null 2>&1; then
    echo "❌ ERROR: railpack.json has invalid JSON syntax!"
    echo "   Please fix the JSON syntax before deploying."
    exit 1
fi

# Check for competing files
if [ ${#COMPETING_FILES[@]} -gt 0 ]; then
    echo "❌ ERROR: Found competing build configuration files:"
    for file in "${COMPETING_FILES[@]}"; do
        echo "   - $file"
    done
    echo ""
    echo "   Railway build priority order:"
    echo "   1. Dockerfile (if exists)"
    echo "   2. railpack.json (if exists)"
    echo "   3. railway.json/railway.toml"
    echo "   4. Nixpacks (auto-detection)"
    echo ""
    echo "   SOLUTION: Remove competing files to use railpack.json:"
    for file in "${COMPETING_FILES[@]}"; do
        echo "   rm $file"
    done
    exit 1
fi

# Check for health endpoint in railpack.json
if ! jq -e '.deploy.healthCheckPath // .deploy.healthcheck.path' railpack.json > /dev/null 2>&1; then
    echo "⚠️  WARNING: No healthCheckPath found in railpack.json"
    echo "   Consider adding a health check endpoint for better deployment reliability."
fi

echo "✅ Build configuration validation passed!"
echo "   - Only railpack.json exists (no conflicts)"
echo "   - railpack.json has valid JSON syntax"
echo "   - Ready for Railway deployment"

# Show railpack.json summary
echo ""
echo "📋 railpack.json configuration summary:"
echo "   - Python version: $(jq -r '.build.packages.python // .packages.python // "not specified"' railpack.json)"
echo "   - Node.js version: $(jq -r '.build.packages.node // .packages.node // "not specified"' railpack.json)"
echo "   - Health check: $(jq -r '.deploy.healthCheckPath // .deploy.healthcheck.path // "not configured"' railpack.json)"
echo "   - Start command: $(jq -r '.deploy.startCommand // .deploy.command // "not specified"' railpack.json | cut -c1-50)..."
