#!/bin/bash
#
# Railway Deployment Debug Script - Comprehensive Railway Build Debugging
# 
# This script provides comprehensive Railway deployment debugging using MCP tools
# and Railway best practices from the deployment documentation.
#
# Usage: bash scripts/railway-debug.sh [--service SERVICE_NAME] [--fix]
#
# Options:
#   --service SERVICE_NAME    Debug specific service (monkey-coder, monkey-coder-backend, monkey-coder-ml)
#   --fix                     Attempt to automatically fix detected issues
#   --verbose                 Enable verbose output
#

set -e

# Color codes
BOLD='\033[1m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default options
SERVICE_NAME=""
AUTO_FIX=false
VERBOSE=false
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --service)
            SERVICE_NAME="$2"
            shift 2
            ;;
        --fix)
            AUTO_FIX=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Print header
echo -e "${BOLD}${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║           Railway Deployment Comprehensive Debug Tool                ║
║                                                                       ║
║  Following Railway Best Practices from RAILWAY_DEPLOYMENT.md         ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check Railway CLI availability
echo -e "${BOLD}🔍 Step 1: Environment Check${NC}"
echo "─────────────────────────────────────────────────────────"
echo ""

if command -v railway &> /dev/null; then
    RAILWAY_VERSION=$(railway --version 2>&1 || echo "unknown")
    echo -e "${GREEN}✓ Railway CLI installed${NC} (${RAILWAY_VERSION})"
else
    echo -e "${YELLOW}⚠ Railway CLI not installed${NC}"
    echo ""
    echo "Install with:"
    echo "  npm install -g @railway/cli"
    echo "  or"
    echo "  curl -fsSL https://railway.app/install.sh | sh"
    echo ""
fi

# Check Node.js and Python
NODE_VERSION=$(node --version 2>/dev/null || echo "not installed")
PYTHON_VERSION=$(python3 --version 2>/dev/null || echo "not installed")
echo -e "  Node.js: ${NODE_VERSION}"
echo -e "  Python: ${PYTHON_VERSION}"
echo ""

# Step 2: Validate railpack.json files
echo -e "${BOLD}📋 Step 2: Railpack Configuration Validation${NC}"
echo "─────────────────────────────────────────────────────────"
echo ""

validate_railpack() {
    local file=$1
    local service=$2
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}✗ $file not found${NC}"
        return 1
    fi
    
    echo -e "${BLUE}Validating $file ($service)...${NC}"
    
    # Check if valid JSON
    if ! jq empty "$file" 2>/dev/null; then
        echo -e "${RED}✗ Invalid JSON syntax${NC}"
        return 1
    fi
    
    # Extract key fields
    local provider=$(jq -r '.build.provider // "unknown"' "$file")
    local start_cmd=$(jq -r '.deploy.startCommand // "missing"' "$file")
    local health_path=$(jq -r '.deploy.healthCheckPath // "missing"' "$file")
    local health_timeout=$(jq -r '.deploy.healthCheckTimeout // "missing"' "$file")
    
    echo -e "  Provider: ${provider}"
    echo -e "  Start Command: ${start_cmd}"
    echo -e "  Health Check: ${health_path} (timeout: ${health_timeout}s)"
    
    # Validate PORT binding
    if [[ "$start_cmd" == *'$PORT'* ]]; then
        echo -e "  ${GREEN}✓ Uses \$PORT variable${NC}"
    else
        echo -e "  ${RED}✗ Missing \$PORT variable - CRITICAL!${NC}"
    fi
    
    # Validate host binding
    if [[ "$start_cmd" == *'0.0.0.0'* ]]; then
        echo -e "  ${GREEN}✓ Binds to 0.0.0.0${NC}"
    else
        echo -e "  ${YELLOW}⚠ Not explicitly binding to 0.0.0.0${NC}"
    fi
    
    # Validate health check
    if [[ "$health_path" != "missing" ]]; then
        echo -e "  ${GREEN}✓ Health check configured${NC}"
    else
        echo -e "  ${RED}✗ Health check missing - CRITICAL!${NC}"
    fi
    
    echo ""
}

# Validate all railpack files
validate_railpack "$PROJECT_ROOT/railpack.json" "Frontend (monkey-coder)"
validate_railpack "$PROJECT_ROOT/railpack-backend.json" "Backend (monkey-coder-backend)"
validate_railpack "$PROJECT_ROOT/railpack-ml.json" "ML Service (monkey-coder-ml)"

# Step 3: Check for competing build files
echo -e "${BOLD}🔧 Step 3: Build System Conflicts Check${NC}"
echo "─────────────────────────────────────────────────────────"
echo ""

CONFLICTS=0

check_competing_file() {
    local file=$1
    if [ -f "$PROJECT_ROOT/$file" ]; then
        echo -e "${YELLOW}⚠ Found competing build file: $file${NC}"
        echo "  This may override railpack.json configuration"
        CONFLICTS=$((CONFLICTS + 1))
    fi
}

check_competing_file "Dockerfile"
check_competing_file "railway.toml"
check_competing_file "nixpacks.toml"

if [ $CONFLICTS -eq 0 ]; then
    echo -e "${GREEN}✓ No competing build files detected${NC}"
else
    echo -e "${RED}✗ Found $CONFLICTS competing build file(s)${NC}"
    echo -e "  ${YELLOW}Recommendation: Remove or rename competing files${NC}"
fi
echo ""

# Step 4: Service-specific debugging
if [ -n "$SERVICE_NAME" ]; then
    echo -e "${BOLD}🎯 Step 4: Service-Specific Debugging ($SERVICE_NAME)${NC}"
    echo "─────────────────────────────────────────────────────────"
    echo ""
    
    if command -v railway &> /dev/null; then
        echo -e "${BLUE}Checking Railway service configuration...${NC}"
        echo ""
        
        # Try to get service info
        railway service --json 2>/dev/null || {
            echo -e "${YELLOW}⚠ Could not retrieve service info (may not be linked)${NC}"
            echo "  Run: railway link"
        }
        
        echo ""
        echo -e "${BLUE}Checking environment variables...${NC}"
        railway variables --service "$SERVICE_NAME" 2>/dev/null || {
            echo -e "${YELLOW}⚠ Could not retrieve variables${NC}"
        }
    fi
    echo ""
fi

# Step 5: Common Railway Issues Checklist
echo -e "${BOLD}✅ Step 5: Railway Best Practices Checklist${NC}"
echo "─────────────────────────────────────────────────────────"
echo ""

echo "Based on Railway Deployment Master Cheat Sheet:"
echo ""

echo -e "${BOLD}Issue 1: Build System Conflicts${NC}"
if [ $CONFLICTS -eq 0 ]; then
    echo -e "  ${GREEN}✓ Only railpack.json exists${NC}"
else
    echo -e "  ${RED}✗ Competing build files detected${NC}"
fi

echo ""
echo -e "${BOLD}Issue 2: PORT Binding Failures${NC}"
echo -e "  Check each railpack.json file above for:"
echo -e "  - Uses \$PORT variable"
echo -e "  - Binds to 0.0.0.0"

echo ""
echo -e "${BOLD}Issue 3: Health Check Configuration${NC}"
echo -e "  Check each railpack.json file above for:"
echo -e "  - Health check endpoint configured"
echo -e "  - Endpoint returns 200 status"

echo ""
echo -e "${BOLD}Issue 4: Reference Variable Mistakes${NC}"
echo -e "  ${BLUE}Required environment variables:${NC}"
echo -e "  Frontend:"
echo -e "    NEXT_PUBLIC_API_URL=https://\${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}"
echo -e "  Backend:"
echo -e "    ML_SERVICE_URL=http://\${{monkey-coder-ml.RAILWAY_PRIVATE_DOMAIN}}"

echo ""
echo -e "${BOLD}Issue 5: Monorepo Service Configuration${NC}"
echo -e "  ${YELLOW}CRITICAL: All services MUST use root directory (/)${NC}"
echo -e "  Railway reads railpack.json from repo root only"
echo -e "  Yarn workspaces require execution from repo root"

echo ""

# Step 6: Generate fix commands if requested
if [ "$AUTO_FIX" = true ]; then
    echo -e "${BOLD}🔨 Step 6: Auto-Fix (Generating Fix Script)${NC}"
    echo "─────────────────────────────────────────────────────────"
    echo ""
    
    FIX_SCRIPT="$PROJECT_ROOT/railway-auto-fix.sh"
    
    cat > "$FIX_SCRIPT" << 'FIXSCRIPT'
#!/bin/bash
# Auto-generated Railway fix script
set -e

echo "Applying Railway configuration fixes..."

# Remove competing build files (if they exist and user confirms)
for file in Dockerfile railway.toml nixpacks.toml; do
    if [ -f "$file" ]; then
        echo "Remove $file? (y/n)"
        read -r answer
        if [ "$answer" = "y" ]; then
            git mv "$file" "$file.disabled" || mv "$file" "$file.disabled"
            echo "Disabled $file"
        fi
    fi
done

echo ""
echo "Fix script completed. Manual Railway Dashboard configuration still required:"
echo "1. Set Root Directory to '/' for all services"
echo "2. Clear any manual build/start commands"
echo "3. Ensure Config Path points to correct railpack file"
echo ""
echo "See RAILWAY_DEPLOYMENT.md for detailed instructions"
FIXSCRIPT
    
    chmod +x "$FIX_SCRIPT"
    echo -e "${GREEN}✓ Fix script generated: $FIX_SCRIPT${NC}"
    echo ""
fi

# Step 7: Summary and recommendations
echo -e "${BOLD}📊 Debug Summary${NC}"
echo "─────────────────────────────────────────────────────────"
echo ""

echo -e "${BOLD}Key Actions Required:${NC}"
echo ""
echo "1. In Railway Dashboard for EACH service:"
echo "   - Set Root Directory: / (or blank)"
echo "   - Clear Build Command (let railpack.json handle it)"
echo "   - Clear Start Command (let railpack.json handle it)"
echo "   - Set Config Path to correct railpack file:"
echo "     * monkey-coder: railpack.json"
echo "     * monkey-coder-backend: railpack-backend.json (or railpack.json with SERVICE_TYPE=backend)"
echo "     * monkey-coder-ml: railpack-ml.json (or railpack.json with SERVICE_TYPE=ml)"
echo ""
echo "2. Configure environment variables (see RAILWAY_DEPLOYMENT.md)"
echo ""
echo "3. Trigger manual redeploy:"
echo "   railway up --service <service-name>"
echo ""

echo -e "${BOLD}Useful Commands:${NC}"
echo "  railway link                                    # Link to project"
echo "  railway service                                 # Select service"
echo "  railway service update --root-directory /       # Fix root directory"
echo "  railway variables --service <name>              # Check variables"
echo "  railway logs --service <name>                   # View logs"
echo "  railway up --service <name>                     # Trigger deploy"
echo ""

echo -e "${BOLD}Documentation:${NC}"
echo "  RAILWAY_DEPLOYMENT.md        - Authoritative deployment guide"
echo "  RAILWAY_CRISIS_RESOLUTION.md - Emergency fix instructions"
echo "  scripts/fix-railway-services.sh - Interactive fix script"
echo ""

echo -e "${GREEN}✓ Debug complete!${NC}"
echo ""
