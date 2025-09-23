#!/bin/bash
# Railway Deployment Validation Test
# Simulates the Railway build environment to ensure deployment will succeed

set -e

echo "🚂 Railway Deployment Validation Test"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Test 1: Validate railpack.json structure
echo -e "\n${YELLOW}1. Validating railpack.json structure...${NC}"

if [ ! -f "railpack.json" ]; then
    echo -e "${RED}❌ railpack.json not found${NC}"
    ERRORS=$((ERRORS + 1))
else
    if jq '.' railpack.json > /dev/null 2>&1; then
        echo -e "${GREEN}✅ railpack.json syntax valid${NC}"
    else
        echo -e "${RED}❌ railpack.json has invalid JSON syntax${NC}"
        ERRORS=$((ERRORS + 1))
    fi
    
    # Check for problematic source command
    if grep -q "source.*activate" railpack.json; then
        echo -e "${RED}❌ Found problematic 'source' command in railpack.json${NC}"
        echo "   This will cause build hangs in Railway's environment"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✅ No problematic 'source' commands found${NC}"
    fi
    
    # Check for direct venv path usage
    if grep -q "/app/.venv/bin/pip" railpack.json; then
        echo -e "${GREEN}✅ Uses direct venv binary paths${NC}"
    else
        echo -e "${RED}❌ Missing direct venv binary paths${NC}"
        ERRORS=$((ERRORS + 1))
    fi
    
    # Check for timeout on build command
    if grep -q "timeout.*yarn.*build" railpack.json; then
        echo -e "${GREEN}✅ Frontend build has timeout protection${NC}"
    else
        echo -e "${YELLOW}⚠️ Frontend build lacks timeout protection${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # Check health check configuration
    if jq '.deploy.healthCheckPath' railpack.json | grep -q "/health"; then
        echo -e "${GREEN}✅ Health check endpoint configured${NC}"
    else
        echo -e "${RED}❌ Health check endpoint not configured${NC}"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Test 2: Validate Python environment
echo -e "\n${YELLOW}2. Validating Python environment...${NC}"

TEMP_VENV="/tmp/railway_validation_venv"
rm -rf "$TEMP_VENV"

echo "   Creating virtual environment..."
python3 -m venv "$TEMP_VENV"

echo "   Installing dependencies..."
"$TEMP_VENV/bin/pip" install --upgrade pip setuptools wheel > /dev/null 2>&1
if "$TEMP_VENV/bin/pip" install -r requirements.txt > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Python dependencies install successfully${NC}"
else
    echo -e "${RED}❌ Python dependencies installation failed${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Test critical imports
if "$TEMP_VENV/bin/python" -c "import uvicorn; import fastapi; import pydantic" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Critical Python packages import successfully${NC}"
else
    echo -e "${RED}❌ Critical Python packages import failed${NC}"
    ERRORS=$((ERRORS + 1))
fi

rm -rf "$TEMP_VENV"

# Test 3: Validate Node.js/Yarn environment
echo -e "\n${YELLOW}3. Validating Node.js/Yarn environment...${NC}"

if command -v node > /dev/null 2>&1; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js available: $NODE_VERSION${NC}"
else
    echo -e "${RED}❌ Node.js not available${NC}"
    ERRORS=$((ERRORS + 1))
fi

if command -v corepack > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Corepack available${NC}"
else
    echo -e "${RED}❌ Corepack not available${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Test Yarn workspace command
if yarn workspace @monkey-coder/web --version > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Yarn workspace command works${NC}"
else
    echo -e "${YELLOW}⚠️ Yarn workspace command issues (may need yarn install)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Test 4: Validate frontend build
echo -e "\n${YELLOW}4. Validating frontend build...${NC}"

if [ -d "packages/web/out" ]; then
    FILE_COUNT=$(ls packages/web/out/ | wc -l)
    if [ "$FILE_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✅ Frontend build exists with $FILE_COUNT files${NC}"
    else
        echo -e "${RED}❌ Frontend build directory empty${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠️ Frontend build directory missing (will be created during deployment)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Test 5: Validate server configuration
echo -e "\n${YELLOW}5. Validating server configuration...${NC}"

if python3 -m py_compile run_server.py; then
    echo -e "${GREEN}✅ run_server.py compiles successfully${NC}"
else
    echo -e "${RED}❌ run_server.py compilation failed${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check for health endpoint in server
if grep -q "/health" run_server.py; then
    echo -e "${GREEN}✅ Health endpoint found in server code${NC}"
else
    echo -e "${RED}❌ Health endpoint missing from server code${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Test 6: Validate Railway-specific configurations
echo -e "\n${YELLOW}6. Validating Railway-specific configurations...${NC}"

# Check for conflicting build files
COMPETING_FILES=()
if [ -f "Dockerfile" ]; then COMPETING_FILES+=("Dockerfile"); fi
if [ -f "railway.toml" ]; then COMPETING_FILES+=("railway.toml"); fi
if [ -f "nixpacks.toml" ]; then COMPETING_FILES+=("nixpacks.toml"); fi

if [ ${#COMPETING_FILES[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ No competing build configuration files${NC}"
else
    echo -e "${RED}❌ Found competing build files: ${COMPETING_FILES[*]}${NC}"
    echo "   These may override railpack.json configuration"
    ERRORS=$((ERRORS + 1))
fi

# Check environment variables setup
if grep -q "PYTHONUNBUFFERED" railpack.json; then
    echo -e "${GREEN}✅ PYTHONUNBUFFERED configured for Railway logs${NC}"
else
    echo -e "${YELLOW}⚠️ PYTHONUNBUFFERED not configured${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Summary
echo -e "\n=================================================="
echo -e "${YELLOW}VALIDATION SUMMARY${NC}"
echo -e "=================================================="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All validations passed! Ready for Railway deployment.${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️ Validation completed with $WARNINGS warnings.${NC}"
    echo -e "${GREEN}✅ No critical errors found. Deployment should succeed.${NC}"
    exit 0
else
    echo -e "${RED}❌ Validation failed with $ERRORS errors and $WARNINGS warnings.${NC}"
    echo -e "${RED}🚫 Fix errors before attempting Railway deployment.${NC}"
    exit 1
fi