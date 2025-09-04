#!/bin/bash
# Railway Deployment Validator - Pre-deployment checks for monkey-coder

set -e

echo "🔍 Railway Deployment Validator v1.0"
echo "===================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track errors
ERRORS=0
WARNINGS=0

# 1. Check Python version in railpack.json
echo -e "\n${YELLOW}1. Checking Python version...${NC}"
PYTHON_VERSION=$(jq -r '.build.packages.python' railpack.json 2>/dev/null)
if [[ "$PYTHON_VERSION" == "3.13" ]]; then
    echo -e "${RED}❌ ERROR: Python 3.13 not supported by Railway/Nixpacks${NC}"
    echo "   Current: $PYTHON_VERSION"
    echo "   Supported: 3.8, 3.9, 3.10, 3.11, 3.12"
    ERRORS=$((ERRORS + 1))
elif [[ "$PYTHON_VERSION" == "3.12" ]]; then
    echo -e "${GREEN}✅ Python version OK: $PYTHON_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️ WARNING: Python version $PYTHON_VERSION - verify Railway support${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# 2. Check for conflicting build files
echo -e "\n${YELLOW}2. Checking for conflicting build files...${NC}"
if [ -f "Dockerfile" ]; then
    echo -e "${RED}❌ ERROR: Dockerfile found - will override railpack.json${NC}"
    echo "   Remove Dockerfile or use it exclusively"
    ERRORS=$((ERRORS + 1))
fi
if [ -f "railway.toml" ]; then
    echo -e "${RED}❌ ERROR: railway.toml found - conflicts with railpack.json${NC}"
    echo "   Remove railway.toml to use railpack.json"
    ERRORS=$((ERRORS + 1))
fi
if [ -f "nixpacks.toml" ]; then
    echo -e "${YELLOW}⚠️ WARNING: nixpacks.toml found - may conflict with railpack.json${NC}"
    WARNINGS=$((WARNINGS + 1))
fi
if [ ! -f "Dockerfile" ] && [ ! -f "railway.toml" ] && [ ! -f "nixpacks.toml" ]; then
    echo -e "${GREEN}✅ No conflicting build files found${NC}"
fi

# 3. Validate railpack.json syntax
echo -e "\n${YELLOW}3. Validating railpack.json syntax...${NC}"
if jq empty railpack.json 2>/dev/null; then
    echo -e "${GREEN}✅ railpack.json syntax valid${NC}"
else
    echo -e "${RED}❌ ERROR: Invalid JSON in railpack.json${NC}"
    jq . railpack.json 2>&1 | head -5
    ERRORS=$((ERRORS + 1))
fi

# 4. Check Next.js configuration
echo -e "\n${YELLOW}4. Checking Next.js configuration...${NC}"
if [ -f "packages/web/next.config.cjs" ] || [ -f "packages/web/next.config.mjs" ]; then
    OUTPUT_MODE=$(grep -E "output.*:.*['\"]export['\"]" packages/web/next.config.* 2>/dev/null)
    if [[ -n "$OUTPUT_MODE" ]]; then
        echo -e "${GREEN}✅ Next.js configured for static export${NC}"
    else
        echo -e "${RED}❌ ERROR: Next.js not configured for static export${NC}"
        echo "   Add: output: 'export' to next.config"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠️ WARNING: Next.js config not found${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# 5. Check for export script in package.json
echo -e "\n${YELLOW}5. Checking Next.js export script...${NC}"
if [ -f "packages/web/package.json" ]; then
    if grep -q '"export":' packages/web/package.json; then
        echo -e "${GREEN}✅ Export script found in package.json${NC}"
    else
        echo -e "${RED}❌ ERROR: No export script in packages/web/package.json${NC}"
        echo "   Add: \"export\": \"next build\" to scripts"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${RED}❌ ERROR: packages/web/package.json not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 6. Check Yarn version configuration
echo -e "\n${YELLOW}6. Checking Yarn configuration...${NC}"
YARN_VERSION=$(yarn --version 2>/dev/null)
if [[ "$YARN_VERSION" == "4.9.2" ]]; then
    echo -e "${GREEN}✅ Yarn 4.9.2 configured${NC}"
elif [[ -n "$YARN_VERSION" ]]; then
    echo -e "${YELLOW}⚠️ WARNING: Yarn version $YARN_VERSION (expected 4.9.2)${NC}"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${RED}❌ ERROR: Yarn not installed${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 7. Check health endpoint
echo -e "\n${YELLOW}7. Checking health endpoint configuration...${NC}"
HEALTH_PATH=$(jq -r '.deploy.healthCheckPath' railpack.json 2>/dev/null)
if [[ "$HEALTH_PATH" == "/health" ]]; then
    echo -e "${GREEN}✅ Health check path configured: $HEALTH_PATH${NC}"
    # Check if endpoint exists in code
    if grep -r "app.get.*['\"]$HEALTH_PATH['\"]" packages/core 2>/dev/null | head -1; then
        echo -e "${GREEN}✅ Health endpoint found in code${NC}"
    else
        echo -e "${YELLOW}⚠️ WARNING: Health endpoint not found in code${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${YELLOW}⚠️ WARNING: Non-standard health path: $HEALTH_PATH${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# 8. Check PORT binding in code
echo -e "\n${YELLOW}8. Checking PORT binding...${NC}"
if grep -r "process.env.PORT" run_server.py packages/core 2>/dev/null | head -1 > /dev/null; then
    echo -e "${GREEN}✅ PORT environment variable used${NC}"
    if grep -E "0\.0\.0\.0|::" run_server.py packages/core 2>/dev/null | head -1 > /dev/null; then
        echo -e "${GREEN}✅ Binding to 0.0.0.0 or :: found${NC}"
    else
        echo -e "${RED}❌ ERROR: Not binding to 0.0.0.0 or ::${NC}"
        echo "   Must bind to 0.0.0.0 not localhost/127.0.0.1"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠️ WARNING: PORT environment variable not found${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Summary
echo -e "\n${YELLOW}===================================="
echo "VALIDATION SUMMARY"
echo -e "====================================${NC}"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Ready for Railway deployment.${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️ $WARNINGS warning(s) found. Deployment may succeed.${NC}"
    exit 0
else
    echo -e "${RED}❌ $ERRORS error(s) and $WARNINGS warning(s) found.${NC}"
    echo -e "${RED}Fix errors before deploying to Railway.${NC}"
    exit 1
fi
