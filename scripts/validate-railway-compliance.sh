#!/bin/bash
# Railway Compliance Validator
# Ensures repository follows Railway deployment standards

set -e

echo "🚀 Railway Deployment Compliance Check"
echo "======================================="

ERRORS=0
WARNINGS=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m' 
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check railpack.json structure
echo -e "\n${YELLOW}1. Checking railpack.json structure...${NC}"

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
  
  # Check for required Railway structure
  if ! jq '.version' railpack.json > /dev/null 2>&1; then
    echo -e "${RED}❌ railpack.json missing 'version' field${NC}"
    ERRORS=$((ERRORS + 1))
  else
    echo -e "${GREEN}✅ railpack.json has version field${NC}"
  fi
  
  if ! jq '.metadata.name' railpack.json > /dev/null 2>&1; then
    echo -e "${RED}❌ railpack.json missing 'metadata.name' field${NC}"
    ERRORS=$((ERRORS + 1))
  else
    echo -e "${GREEN}✅ railpack.json has metadata.name field${NC}"
  fi
  
  if ! jq '.build.provider' railpack.json > /dev/null 2>&1; then
    echo -e "${RED}❌ railpack.json missing 'build.provider' field${NC}"
    ERRORS=$((ERRORS + 1))
  else
    echo -e "${GREEN}✅ railpack.json has build.provider field${NC}"
  fi
  
  if ! jq '.build.steps' railpack.json > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ railpack.json missing 'build.steps' structure${NC}"
    WARNINGS=$((WARNINGS + 1))
  else
    echo -e "${GREEN}✅ railpack.json has build.steps structure${NC}"
  fi
fi

# Check for conflicting build files
echo -e "\n${YELLOW}2. Checking for conflicting build files...${NC}"

CONFLICTS=()
if [ -f "Dockerfile" ]; then
  CONFLICTS+=("Dockerfile")
fi
if [ -f "railway.toml" ]; then
  CONFLICTS+=("railway.toml")
fi
if [ -f "nixpacks.toml" ]; then
  CONFLICTS+=("nixpacks.toml")
fi

if [ ${#CONFLICTS[@]} -gt 0 ]; then
  echo -e "${RED}❌ Found conflicting build files: ${CONFLICTS[*]}${NC}"
  echo -e "${YELLOW}   Railway priority: Dockerfile > railpack.json > railway.toml > nixpacks${NC}"
  ERRORS=$((ERRORS + 1))
else
  echo -e "${GREEN}✅ No conflicting build files found${NC}"
fi

# Check for localhost references in SDK
echo -e "\n${YELLOW}3. Checking for hardcoded localhost references...${NC}"

# Check for files with localhost:8000 and see if they have Railway domain handling
LOCALHOST_FILES=$(grep -l "localhost:8000" packages/sdk/**/*.{py,ts,js} 2>/dev/null || true)
COMPLIANT=true

for file in $LOCALHOST_FILES; do
  if ! grep -q "RAILWAY_PUBLIC_DOMAIN" "$file" 2>/dev/null; then
    echo -e "${RED}❌ Found hardcoded localhost in $file without Railway domain fallback${NC}"
    COMPLIANT=false
  fi
done

if [ "$COMPLIANT" = true ]; then
  echo -e "${GREEN}✅ All localhost references have Railway domain fallbacks${NC}"
else
  ERRORS=$((ERRORS + 1))
fi

# Check Railway domain variable usage
echo -e "\n${YELLOW}4. Checking Railway domain variable usage...${NC}"

if grep -r "RAILWAY_PUBLIC_DOMAIN" packages/sdk/ > /dev/null 2>&1; then
  echo -e "${GREEN}✅ Railway domain variables properly used in SDK${NC}"
else
  echo -e "${YELLOW}⚠️ Railway domain variables not found in SDK${NC}"
  WARNINGS=$((WARNINGS + 1))
fi

# Validate PORT usage
echo -e "\n${YELLOW}5. Checking PORT environment variable usage...${NC}"

if grep -r "process\.env\.PORT\|os\.getenv.*PORT" run_server.py packages/core/ > /dev/null 2>&1; then
  echo -e "${GREEN}✅ Server properly uses process.env.PORT${NC}"
else
  echo -e "${RED}❌ Server not using process.env.PORT${NC}"
  ERRORS=$((ERRORS + 1))
fi

# Check host binding
echo -e "\n${YELLOW}6. Checking host binding configuration...${NC}"

if grep -r "0\.0\.0\.0" run_server.py packages/core/ > /dev/null 2>&1; then
  echo -e "${GREEN}✅ Server binds to 0.0.0.0${NC}"
else
  echo -e "${RED}❌ Server not binding to 0.0.0.0${NC}"
  ERRORS=$((ERRORS + 1))
fi

# Check health endpoint
echo -e "\n${YELLOW}7. Checking health endpoint configuration...${NC}"

if grep -r "/health" packages/core/monkey_coder/app/main.py > /dev/null 2>&1; then
  echo -e "${GREEN}✅ Health endpoint found in main.py${NC}"
else
  echo -e "${RED}❌ Health endpoint not found${NC}"
  ERRORS=$((ERRORS + 1))
fi

if jq '.deploy.healthCheckPath' railpack.json | grep -q "/health"; then
  echo -e "${GREEN}✅ Health check path configured in railpack.json${NC}"
else
  echo -e "${RED}❌ Health check path not configured in railpack.json${NC}"
  ERRORS=$((ERRORS + 1))
fi

# Summary
echo -e "\n======================================="
echo -e "${YELLOW}COMPLIANCE SUMMARY${NC}"
echo -e "======================================="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  echo -e "${GREEN}✅ All compliance checks passed!${NC}"
  echo -e "${GREEN}   Repository is Railway deployment ready${NC}"
  exit 0
elif [ $ERRORS -eq 0 ]; then
  echo -e "${YELLOW}⚠️ $WARNINGS warning(s) found${NC}"
  echo -e "${YELLOW}   Deployment may succeed but review warnings${NC}"
  exit 0
else
  echo -e "${RED}❌ $ERRORS error(s) and $WARNINGS warning(s) found${NC}"
  echo -e "${RED}   Fix errors before deploying to Railway${NC}"
  exit 1
fi