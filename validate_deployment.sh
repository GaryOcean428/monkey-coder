#!/bin/bash
set -e

echo "🔍 Monkey Coder Railway Deployment Validator"
echo "=============================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# Check 1: Validate railpack.json files
echo "📋 Checking railpack.json files..."
for file in railpack.json railpack-backend.json railpack-ml.json; do
    if [ -f "$file" ]; then
        if jq empty "$file" 2>/dev/null; then
            echo -e "${GREEN}✓${NC} $file is valid JSON"
        else
            echo -e "${RED}✗${NC} $file has invalid JSON syntax"
            ERRORS=$((ERRORS + 1))
        fi
    fi
done

# Check 2: Verify Next.js build configuration
echo ""
echo "🏗️  Checking Next.js build configuration..."
if [ -f "packages/web/next.config.js" ]; then
    echo -e "${GREEN}✓${NC} next.config.js found"
    
    # Check if output is configured for export
    if grep -q "output.*export" packages/web/next.config.js; then
        echo -e "${GREEN}✓${NC} Static export configured"
    else
        echo -e "${YELLOW}⚠${NC}  Static export might not be configured"
    fi
fi

# Check 3: Verify serve.json exists
echo ""
echo "📄 Checking serve.json configuration..."
if [ -f "serve.json" ]; then
    if jq empty serve.json 2>/dev/null; then
        echo -e "${GREEN}✓${NC} serve.json exists and is valid JSON"
    else
        echo -e "${RED}✗${NC} serve.json has invalid JSON"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠${NC}  serve.json not found (recommended for static file server)"
fi

# Check 4: Verify PORT binding in backend code
echo ""
echo "🔌 Checking PORT binding in code..."

# Check Python files
if grep -r "0\.0\.0\.0" --include="*.py" packages/core/monkey_coder/app/ 2>/dev/null | head -1 > /dev/null; then
    echo -e "${GREEN}✓${NC} Python backend binds to 0.0.0.0"
else
    echo -e "${YELLOW}⚠${NC}  Python backend might not bind to 0.0.0.0"
fi

# Check for hardcoded ports (excluding comments and PORT env var usage)
if grep -rn "port.*=.*[0-9]\{4\}" --include="*.py" packages/core/monkey_coder/app/ 2>/dev/null | grep -v "process.env\|os.environ\|PORT\|#" > /dev/null; then
    echo -e "${RED}✗${NC} Found potentially hardcoded ports in Python code"
    grep -rn "port.*=.*[0-9]\{4\}" --include="*.py" packages/core/monkey_coder/app/ 2>/dev/null | grep -v "process.env\|os.environ\|PORT\|#" | head -3
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓${NC} No hardcoded ports found"
fi

# Check 5: Health check endpoints
echo ""
echo "🏥 Checking health check endpoints..."
if grep -r "/health" --include="*.py" packages/core/monkey_coder/app/ 2>/dev/null > /dev/null; then
    echo -e "${GREEN}✓${NC} Health check endpoint exists in Python backend"
else
    echo -e "${RED}✗${NC} No health check endpoint found in backend"
    ERRORS=$((ERRORS + 1))
fi

# Check 6: Conflicting build configs
echo ""
echo "🗑️  Checking for conflicting build configurations..."
CONFLICTS=0

if [ -f "Dockerfile" ]; then
    echo -e "${YELLOW}⚠${NC}  Dockerfile exists - may conflict with railpack.json"
    CONFLICTS=$((CONFLICTS + 1))
fi

if [ -f "railway.toml" ]; then
    echo -e "${YELLOW}⚠${NC}  railway.toml exists - may conflict with railpack.json"
    CONFLICTS=$((CONFLICTS + 1))
fi

if [ -f "nixpacks.toml" ]; then
    echo -e "${YELLOW}⚠${NC}  nixpacks.toml exists - may conflict with railpack.json"
    CONFLICTS=$((CONFLICTS + 1))
fi

if [ $CONFLICTS -eq 0 ]; then
    echo -e "${GREEN}✓${NC} No conflicting build configs found"
else
    echo -e "${YELLOW}⚠${NC}  Found $CONFLICTS conflicting build config(s)"
    echo "   Recommendation: Remove competing configs when using railpack.json"
fi

# Check 7: Verify railpack.json uses correct start command
echo ""
echo "🚀 Checking start commands..."
if [ -f "railpack.json" ]; then
    if grep -q "serve.*packages/web/out" railpack.json; then
        echo -e "${GREEN}✓${NC} Frontend uses 'serve' for static files (correct)"
    elif grep -q "next start" railpack.json; then
        echo -e "${RED}✗${NC} Frontend uses 'next start' - incompatible with static export"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Check 8: Dependencies
echo ""
echo "📦 Checking package managers..."
if [ -f "yarn.lock" ]; then
    echo -e "${GREEN}✓${NC} Using Yarn"
fi

if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✓${NC} Python requirements.txt exists"
fi

# Final Summary
echo ""
echo "=============================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Validation passed!${NC} Ready for Railway deployment"
    echo ""
    echo "Next steps:"
    echo "1. Review changes: git status"
    echo "2. Test build locally: yarn workspace @monkey-coder/web build"
    echo "3. Push to Railway: git push"
    echo "4. Monitor logs: railway logs --service monkey-coder"
    exit 0
else
    echo -e "${RED}❌ Validation failed with $ERRORS error(s)${NC}"
    echo ""
    echo "Please fix the errors above before deploying to Railway"
    exit 1
fi
