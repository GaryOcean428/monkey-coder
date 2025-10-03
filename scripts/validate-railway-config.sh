#!/bin/bash
#
# Railway Configuration Validator
# 
# This script validates that the Railway configuration files are correct
# and that the repository structure supports the Shared Monorepo pattern
#
# Usage: bash scripts/validate-railway-config.sh
#

set -e

BOLD='\033[1m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BOLD}${BLUE}"
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                                                                    ║"
echo "║         Railway Configuration Validator                           ║"
echo "║                                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

ERRORS=0
WARNINGS=0

# Helper functions
pass() {
    echo -e "${GREEN}✓${NC} $1"
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((ERRORS++))
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check 1: Validate railpack.json files exist and are valid JSON
echo -e "${BOLD}1. Validating railpack.json files...${NC}"
echo "────────────────────────────────────────────────────────"

for file in railpack.json railpack-backend.json railpack-ml.json; do
    if [ -f "$file" ]; then
        if python3 -m json.tool "$file" > /dev/null 2>&1; then
            pass "$file - Valid JSON"
        else
            fail "$file - Invalid JSON syntax"
        fi
    else
        fail "$file - File not found"
    fi
done

for file in services/*/railpack.json; do
    if [ -f "$file" ]; then
        if python3 -m json.tool "$file" > /dev/null 2>&1; then
            pass "$file - Valid JSON (should be deprecated)"
        else
            fail "$file - Invalid JSON syntax"
        fi
    fi
done

echo ""

# Check 2: Verify no competing build configurations at root
echo -e "${BOLD}2. Checking for competing build configurations...${NC}"
echo "────────────────────────────────────────────────────────"

COMPETING_FILES=("Dockerfile" "railway.toml" "railway.json" "nixpacks.toml")
FOUND_COMPETING=false

for file in "${COMPETING_FILES[@]}"; do
    if [ -f "$file" ]; then
        fail "Found competing config: $file (should be removed)"
        FOUND_COMPETING=true
    fi
done

if [ "$FOUND_COMPETING" = false ]; then
    pass "No competing build configurations found"
fi

echo ""

# Check 3: Verify Yarn workspace structure
echo -e "${BOLD}3. Validating Yarn workspace structure...${NC}"
echo "────────────────────────────────────────────────────────"

if [ -f "package.json" ]; then
    pass "Root package.json exists"
    
    # Check for workspace configuration
    if grep -q '"workspaces"' package.json; then
        pass "Workspaces configured in package.json"
    else
        fail "No workspaces configuration found in package.json"
    fi
else
    fail "Root package.json not found"
fi

if [ -f "yarn.lock" ]; then
    pass "yarn.lock exists"
else
    warn "yarn.lock not found (run 'yarn install')"
fi

if [ -f ".yarnrc.yml" ]; then
    pass ".yarnrc.yml exists"
else
    warn ".yarnrc.yml not found"
fi

echo ""

# Check 4: Verify required directories exist
echo -e "${BOLD}4. Checking repository structure...${NC}"
echo "────────────────────────────────────────────────────────"

REQUIRED_DIRS=("packages/web" "packages/core" "packages/cli" "packages/sdk")

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        pass "Directory exists: $dir"
    else
        fail "Missing directory: $dir"
    fi
done

echo ""

# Check 5: Verify package.json in workspaces
echo -e "${BOLD}5. Validating workspace package.json files...${NC}"
echo "────────────────────────────────────────────────────────"

for dir in packages/*; do
    if [ -d "$dir" ]; then
        dirname=$(basename $dir)
        if [ -f "$dir/package.json" ]; then
            pass "$dirname has package.json (Node.js workspace)"
        elif [ -f "$dir/pyproject.toml" ] || [ -f "$dir/setup.py" ]; then
            pass "$dirname has Python package config (pyproject.toml/setup.py)"
        else
            warn "$dirname missing package configuration"
        fi
    fi
done

echo ""

# Check 6: Test Yarn commands (if Yarn is available)
echo -e "${BOLD}6. Testing Yarn workspace commands...${NC}"
echo "────────────────────────────────────────────────────────"

if command -v yarn &> /dev/null; then
    pass "Yarn is available"
    
    # Test workspace list command
    if yarn workspaces list --json > /dev/null 2>&1; then
        pass "Yarn workspace commands work"
        
        # Count workspaces
        WORKSPACE_COUNT=$(yarn workspaces list --json 2>/dev/null | wc -l)
        info "Found $WORKSPACE_COUNT workspaces"
    else
        fail "Yarn workspace commands failed (run 'yarn install' first)"
    fi
else
    warn "Yarn not installed (will be installed by Railway during build)"
fi

echo ""

# Check 7: Verify Python structure for backend
echo -e "${BOLD}7. Validating Python backend structure...${NC}"
echo "────────────────────────────────────────────────────────"

if [ -f "requirements.txt" ]; then
    pass "Root requirements.txt exists"
else
    warn "Root requirements.txt not found"
fi

if [ -f "packages/core/monkey_coder/app/main.py" ]; then
    pass "Backend entry point exists (monkey_coder.app.main)"
else
    fail "Backend entry point not found"
fi

if [ -d "packages/core/monkey_coder" ]; then
    pass "Python package structure exists"
else
    fail "Python package directory not found"
fi

echo ""

# Check 8: Verify ML service structure
echo -e "${BOLD}8. Validating ML service structure...${NC}"
echo "────────────────────────────────────────────────────────"

if [ -f "services/ml/ml_server.py" ]; then
    pass "ML server entry point exists"
else
    warn "ML server entry point not found (services/ml/ml_server.py)"
fi

if [ -f "services/ml/requirements.txt" ]; then
    pass "ML requirements.txt exists"
else
    warn "ML requirements.txt not found"
fi

echo ""

# Check 9: Verify railpack.json configurations
echo -e "${BOLD}9. Validating railpack.json content...${NC}"
echo "────────────────────────────────────────────────────────"

# Check frontend config (railpack.json)
if grep -q '"yarn workspace @monkey-coder/web build"' railpack.json; then
    pass "Frontend build command uses workspace syntax"
else
    fail "Frontend build command incorrect in railpack.json"
fi

if grep -q '"corepack enable"' railpack.json; then
    pass "Corepack setup included in railpack.json"
else
    warn "Corepack setup missing in railpack.json"
fi

# Check backend config (railpack-backend.json)
if grep -q '"python".*"3.12"' railpack-backend.json; then
    pass "Backend uses Python 3.12"
else
    warn "Backend Python version may be incorrect"
fi

if grep -q 'uvicorn monkey_coder.app.main:app' railpack-backend.json; then
    pass "Backend start command correct"
else
    fail "Backend start command incorrect in railpack-backend.json"
fi

# Check ML config (railpack-ml.json)
if grep -q 'services.ml.ml_server:app' railpack-ml.json || grep -q 'ml_server:app' railpack-ml.json; then
    pass "ML start command appears correct"
else
    warn "ML start command may need verification"
fi

echo ""

# Check 10: Environment variable examples
echo -e "${BOLD}10. Checking environment variable documentation...${NC}"
echo "────────────────────────────────────────────────────────"

if [ -f ".env.example" ]; then
    pass "Environment variable example file exists"
else
    warn "No .env.example file (consider creating one)"
fi

echo ""

# Summary
echo -e "${BOLD}${BLUE}"
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                      Validation Summary                           ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
else
    echo -e "${RED}✗ Found $ERRORS error(s)${NC}"
fi

if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠ Found $WARNINGS warning(s)${NC}"
fi

echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}${BOLD}Railway Configuration Status: READY ✓${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Apply Railway service configuration: bash scripts/fix-railway-services.sh"
    echo "2. Or follow manual instructions: RAILWAY_FIX_INSTRUCTIONS.md"
    echo "3. Deploy and verify health endpoints"
    exit 0
else
    echo -e "${RED}${BOLD}Railway Configuration Status: NEEDS FIXES ✗${NC}"
    echo ""
    echo "Fix the errors above before deploying to Railway."
    exit 1
fi
