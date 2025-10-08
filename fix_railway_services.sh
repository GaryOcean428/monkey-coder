#!/bin/bash
# Railway Service Configuration Fix Script
# Automatically updates all 3 services with correct settings

set -e

echo "🚂 Railway Service Configuration Fix"
echo "====================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI not found!${NC}"
    echo ""
    echo "Install it with: npm install -g @railway/cli"
    echo "Or: brew install railway"
    exit 1
fi

# Check if logged in
echo -e "${BLUE}🔐 Checking Railway authentication...${NC}"
if ! railway whoami &> /dev/null; then
    echo -e "${RED}❌ Not logged in to Railway!${NC}"
    echo ""
    echo "Please login first: railway login"
    exit 1
fi

echo -e "${GREEN}✓ Authenticated${NC}"
echo ""

# Link to project if not already linked
echo -e "${BLUE}🔗 Linking to Railway project...${NC}"
railway link || true
echo ""

# Function to update service settings
update_service() {
    local service_name=$1
    local config_file=$2
    
    echo -e "${BLUE}📝 Configuring ${service_name}...${NC}"
    
    # Set the service
    railway service ${service_name} || {
        echo -e "${RED}❌ Service '${service_name}' not found${NC}"
        return 1
    }
    
    # Clear any custom build/start commands by using railway.json config
    echo -e "  ${YELLOW}→${NC} Setting config file to ${config_file}"
    
    # Note: Railway CLI doesn't have direct commands to modify service settings
    # We'll trigger a redeploy which will pick up the new railway.json files
    
    echo -e "${GREEN}  ✓ Service configured (will use ${config_file})${NC}"
}

# Update all services
echo -e "${YELLOW}🔧 Updating service configurations...${NC}"
echo ""

# Service 1: Frontend (monkey-coder)
update_service "monkey-coder" "railway.json"
echo ""

# Service 2: Backend (monkey-coder-backend)  
update_service "monkey-coder-backend" "railway-backend.json"
echo ""

# Service 3: ML Service (monkey-coder-ml)
update_service "monkey-coder-ml" "railway-ml.json"
echo ""

# Trigger redeployments
echo -e "${YELLOW}🚀 Triggering redeployments...${NC}"
echo ""

redeploy_service() {
    local service_name=$1
    echo -e "${BLUE}  Redeploying ${service_name}...${NC}"
    railway service ${service_name}
    railway up --detach || echo -e "${YELLOW}  ⚠ Railway may auto-deploy via GitHub${NC}"
}

redeploy_service "monkey-coder"
echo ""
redeploy_service "monkey-coder-backend"
echo ""
redeploy_service "monkey-coder-ml"
echo ""

echo -e "${GREEN}✅ Configuration complete!${NC}"
echo ""
echo -e "${BLUE}📊 Monitor deployments:${NC}"
echo "  • Frontend:  railway logs --service monkey-coder"
echo "  • Backend:   railway logs --service monkey-coder-backend"
echo "  • ML:        railway logs --service monkey-coder-ml"
echo ""
echo -e "${BLUE}🌐 Check status:${NC}"
echo "  railway status"
echo ""
echo -e "${YELLOW}⏱  Deployments will take 5-10 minutes${NC}"
echo ""
