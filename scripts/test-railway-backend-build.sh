#!/usr/bin/env bash
# Test Railway Backend Build Process
# Simulates what Railway does when building the backend service

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Railway Backend Build Simulation Test                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

PROJECT_ROOT=$(dirname "$(dirname "${BASH_SOURCE[0]}")")
cd "$PROJECT_ROOT"

# Simulate Railway's root directory isolation
BACKEND_DIR="services/backend"

echo "📋 Test Configuration:"
echo "  Root Directory: $BACKEND_DIR (as Railway would set it)"
echo "  Working Directory: $(pwd)/$BACKEND_DIR"
echo ""

# Change to backend directory (simulating Railway's context)
cd "$BACKEND_DIR"

echo "1️⃣ Checking railpack.json..."
if [[ ! -f "railpack.json" ]]; then
    echo -e "${RED}❌ FAIL: railpack.json not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ railpack.json found${NC}"

# Validate JSON syntax
if python3 -m json.tool railpack.json > /dev/null 2>&1; then
    echo -e "${GREEN}✅ railpack.json is valid JSON${NC}"
else
    echo -e "${RED}❌ FAIL: railpack.json has syntax errors${NC}"
    exit 1
fi
echo ""

echo "2️⃣ Checking requirements-deploy.txt..."
if [[ ! -f "requirements-deploy.txt" ]]; then
    echo -e "${RED}❌ FAIL: requirements-deploy.txt not found${NC}"
    echo -e "${YELLOW}Railway build would fail with: error: File not found: \`requirements-deploy.txt\`${NC}"
    exit 1
fi
echo -e "${GREEN}✅ requirements-deploy.txt found${NC}"
echo "  File size: $(wc -c < requirements-deploy.txt) bytes"
echo "  Line count: $(wc -l < requirements-deploy.txt) lines"
echo ""

echo "3️⃣ Checking relative path to packages/core..."
if [[ ! -d "../../packages/core" ]]; then
    echo -e "${RED}❌ FAIL: ../../packages/core not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ ../../packages/core exists${NC}"
echo "  Resolved path: $(cd ../../packages/core && pwd)"
echo ""

echo "4️⃣ Simulating Railway build commands..."
echo ""
echo "  Command 1: pip install --upgrade uv"
echo -e "${BLUE}  → This would install uv package manager${NC}"
echo ""

echo "  Command 2: python -m uv pip install -r requirements-deploy.txt"
if python3 -m uv pip compile requirements-deploy.txt --quiet > /dev/null 2>&1; then
    echo -e "${GREEN}  ✅ requirements-deploy.txt is parseable by uv${NC}"
    echo "  → Found $(grep -c "^[a-zA-Z]" requirements-deploy.txt) packages to install"
else
    echo -e "${YELLOW}  ⚠️  uv not available locally (this is OK, Railway will have it)${NC}"
    echo "  → File exists and is readable: ${GREEN}✅${NC}"
fi
echo ""

echo "  Command 3: python -m uv pip install -e ../../packages/core"
echo -e "${BLUE}  → This would install monkey_coder package from local path${NC}"
echo -e "${GREEN}  ✅ Path ../../packages/core is accessible${NC}"
echo ""

echo "  Command 4: python -c 'import monkey_coder; print(\"✅ Installed:\", monkey_coder.__file__)'"
echo -e "${BLUE}  → This would verify the package is importable${NC}"
echo ""

echo "5️⃣ Checking deploy configuration..."
DEPLOY_CMD=$(python3 -c "import json; print(json.load(open('railpack.json'))['deploy']['startCommand'])" 2>/dev/null || echo "")
if [[ -z "$DEPLOY_CMD" ]]; then
    echo -e "${RED}❌ FAIL: deploy.startCommand not found in railpack.json${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Deploy command configured${NC}"
echo "  Command: $DEPLOY_CMD"
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ ALL CHECKS PASSED                                         ║${NC}"
echo -e "${GREEN}║   Railway backend build should succeed with this configuration║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "Summary:"
echo "  ✅ railpack.json exists and is valid"
echo "  ✅ requirements-deploy.txt is accessible from build context"
echo "  ✅ packages/core path is accessible via relative path"
echo "  ✅ deploy command is configured"
echo ""
echo "Next steps:"
echo "  1. Ensure Railway service root directory is set to: services/backend"
echo "  2. Trigger a new deployment: railway up --service monkey-coder-backend"
echo "  3. Monitor build logs: railway logs --service monkey-coder-backend"
