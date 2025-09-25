#!/bin/bash

# 🚀 Railway Deployment Cheatsheet Validation Script
# Implements all validation checks from the AI Agent Railway Deployment Cheatsheet

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Railway Deployment Cheatsheet Validation${NC}"
echo "=============================================="

ERRORS=0
WARNINGS=0

# 1. Build System Conflict Check
echo -e "\n${YELLOW}1. Checking for build system conflicts...${NC}"

COMPETING_FILES=()
if [ -f "Dockerfile" ] && [ ! -d "services/sandbox" ] || [ -f "Dockerfile" ] && [ "$(dirname $(find . -name "Dockerfile" -not -path "./services/*"))" = "." ]; then
    COMPETING_FILES+=("Dockerfile")
fi
if [ -f "railway.toml" ]; then
    COMPETING_FILES+=("railway.toml")
fi
if [ -f "nixpacks.toml" ]; then
    COMPETING_FILES+=("nixpacks.toml")
fi

if [ ${#COMPETING_FILES[@]} -gt 0 ]; then
    echo -e "${RED}❌ Found competing build configuration files:${NC}"
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
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ No competing build files found${NC}"
fi

# 2. railpack.json Structure Validation
echo -e "\n${YELLOW}2. Checking railpack.json structure...${NC}"

if [ ! -f "railpack.json" ]; then
    echo -e "${RED}❌ railpack.json not found${NC}"
    ERRORS=$((ERRORS + 1))
else
    # Validate JSON syntax
    if ! jq '.' railpack.json > /dev/null 2>&1; then
        echo -e "${RED}❌ railpack.json has invalid JSON syntax${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✅ railpack.json syntax valid${NC}"
    fi
    
    # Check required fields
    if ! jq -e '.version' railpack.json > /dev/null 2>&1; then
        echo -e "${RED}❌ Missing required field: version${NC}"
        ERRORS=$((ERRORS + 1))
    fi
    
    if ! jq -e '.metadata.name' railpack.json > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Missing recommended field: metadata.name${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    if ! jq -e '.build.provider' railpack.json > /dev/null 2>&1; then
        echo -e "${RED}❌ Missing required field: build.provider${NC}"
        ERRORS=$((ERRORS + 1))
    fi
    
    if jq -e '.build.provider' railpack.json > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Build provider specified${NC}"
    fi
fi

# 3. Health Check Configuration
echo -e "\n${YELLOW}3. Checking health check configuration...${NC}"

if jq -e '.deploy.healthCheckPath // .deploy.healthcheck.path' railpack.json > /dev/null 2>&1; then
    HEALTH_PATH=$(jq -r '.deploy.healthCheckPath // .deploy.healthcheck.path' railpack.json)
    echo -e "${GREEN}✅ Health check path configured: ${HEALTH_PATH}${NC}"
    
    # Verify health endpoint exists in code
    if grep -r "${HEALTH_PATH}" packages/core/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Health endpoint implemented in code${NC}"
    else
        echo -e "${YELLOW}⚠️  Health endpoint path not found in source code${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${RED}❌ No health check path configured${NC}"
    echo "   Add: \"healthCheckPath\": \"/health\" to deploy section"
    ERRORS=$((ERRORS + 1))
fi

# 4. PORT Binding Validation
echo -e "\n${YELLOW}4. Checking PORT binding...${NC}"

# Check for hardcoded ports (common mistake)
HARDCODED_PORTS=$(grep -r "listen.*[0-9][0-9][0-9][0-9]" . --include="*.py" --include="*.js" --include="*.ts" --exclude-dir=node_modules --exclude-dir=.git || true)
if [ -n "$HARDCODED_PORTS" ]; then
    echo -e "${YELLOW}⚠️  Potential hardcoded ports found:${NC}"
    echo "$HARDCODED_PORTS"
    WARNINGS=$((WARNINGS + 1))
fi

# Check for proper PORT environment usage
if grep -r "process\.env\.PORT\|os\.getenv.*PORT\|PORT.*=" . --include="*.py" --include="*.js" --include="*.ts" --exclude-dir=node_modules --exclude-dir=.git > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PORT environment variable usage found${NC}"
else
    echo -e "${RED}❌ No PORT environment variable usage found${NC}"
    echo "   Ensure your app reads port from: process.env.PORT (Node.js) or os.getenv('PORT') (Python)"
    ERRORS=$((ERRORS + 1))
fi

# 5. Host Binding Validation
echo -e "\n${YELLOW}5. Checking host binding...${NC}"

if grep -r "0\.0\.0\.0" . --include="*.py" --include="*.js" --include="*.ts" --exclude-dir=node_modules --exclude-dir=.git > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Correct host binding (0.0.0.0) found${NC}"
else
    echo -e "${RED}❌ Host binding not set to 0.0.0.0${NC}"
    echo "   Ensure your app binds to 0.0.0.0, not localhost or 127.0.0.1"
    ERRORS=$((ERRORS + 1))
fi

# Check for localhost/127.0.0.1 usage (anti-pattern)
BAD_HOSTS=$(grep -r "localhost\|127\.0\.0\.1" . --include="*.py" --include="*.js" --include="*.ts" --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=packages/web/src || true)
if [ -n "$BAD_HOSTS" ]; then
    echo -e "${YELLOW}⚠️  Potential localhost/127.0.0.1 usage found:${NC}"
    echo "$BAD_HOSTS" | head -5
    WARNINGS=$((WARNINGS + 1))
fi

# 6. Reference Variable Usage
echo -e "\n${YELLOW}6. Checking Railway reference variables...${NC}"

# Look for proper Railway variable references
if grep -r "RAILWAY_PUBLIC_DOMAIN\|RAILWAY_PRIVATE_DOMAIN" . --include="*.py" --include="*.js" --include="*.ts" --include="*.json" --exclude-dir=node_modules --exclude-dir=.git > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Railway reference variables found${NC}"
else
    echo -e "${YELLOW}⚠️  No Railway reference variables found${NC}"
    echo "   Consider using \${RAILWAY_PUBLIC_DOMAIN} for service communication"
    WARNINGS=$((WARNINGS + 1))
fi

# Check for incorrect PORT references in variables
BAD_REFS=$(grep -r "\${{.*\.PORT}}" . --include="*.py" --include="*.js" --include="*.ts" --include="*.json" --exclude-dir=node_modules --exclude-dir=.git || true)
if [ -n "$BAD_REFS" ]; then
    echo -e "${RED}❌ Incorrect PORT references found:${NC}"
    echo "$BAD_REFS"
    echo "   Use RAILWAY_PUBLIC_DOMAIN instead of PORT references"
    ERRORS=$((ERRORS + 1))
fi

# 7. Start Command Validation
echo -e "\n${YELLOW}7. Checking start command...${NC}"

if jq -e '.deploy.startCommand // .deploy.command' railpack.json > /dev/null 2>&1; then
    START_CMD=$(jq -r '.deploy.startCommand // .deploy.command' railpack.json)
    echo -e "${GREEN}✅ Start command configured: ${START_CMD}${NC}"
    
    # Check if start command hardcodes port
    if echo "$START_CMD" | grep -E "(--port|:)[0-9]" > /dev/null; then
        echo -e "${RED}❌ Start command contains hardcoded port${NC}"
        echo "   Remove hardcoded port from: $START_CMD"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${RED}❌ No start command configured${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Summary
echo -e "\n${BLUE}📋 Validation Summary${NC}"
echo "===================="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}🎉 Perfect! All Railway deployment best practices followed${NC}"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Ready for deployment with ${WARNINGS} warnings${NC}"
    echo -e "${YELLOW}   Address warnings for optimal Railway deployment${NC}"
else
    echo -e "${RED}❌ ${ERRORS} errors must be fixed before deployment${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}   Also ${WARNINGS} warnings to address${NC}"
    fi
fi

echo ""
echo -e "${BLUE}🚀 Railway Deployment Golden Rules:${NC}"
echo "1. ONE build system (remove competing configs)"
echo "2. NEVER hardcode ports (use process.env.PORT)"
echo "3. ALWAYS bind to 0.0.0.0 (not localhost)"
echo "4. Health endpoint required (/health returning 200)"
echo "5. Reference domains, not ports (RAILWAY_PUBLIC_DOMAIN)"
echo "6. Validate before deploy (this script)"

# Exit with error code if there are errors
if [ $ERRORS -gt 0 ]; then
    exit 1
fi

exit 0