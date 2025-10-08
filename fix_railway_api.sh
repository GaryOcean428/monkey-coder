#!/bin/bash
# Railway API Direct Fix Script
# Uses Railway API to update service settings directly

set -e

echo "🚂 Railway API Configuration Fix"
echo "================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check for Railway API token
if [ -z "$RAILWAY_API_TOKEN" ]; then
    echo -e "${RED}❌ RAILWAY_API_TOKEN not set!${NC}"
    echo ""
    echo "Get your token from: https://railway.app/account/tokens"
    echo ""
    echo "Then run:"
    echo "  export RAILWAY_API_TOKEN='your-token-here'"
    echo "  ./fix_railway_api.sh"
    exit 1
fi

API_URL="https://backboard.railway.app/graphql/v2"

# GraphQL query to list projects
echo -e "${BLUE}📋 Fetching Railway projects...${NC}"

PROJECTS=$(curl -s "$API_URL" \
  -H "Authorization: Bearer $RAILWAY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { projects { edges { node { id name } } } }"
  }')

echo "$PROJECTS" | jq -r '.data.projects.edges[].node | "\(.id) - \(.name)"'
echo ""

echo -e "${YELLOW}📝 Enter your project ID (or name 'monkey-coder'):${NC}"
read PROJECT_INPUT

# Try to find project by name if not an ID
if [[ ! $PROJECT_INPUT =~ ^[a-f0-9-]{36}$ ]]; then
    PROJECT_ID=$(echo "$PROJECTS" | jq -r --arg name "$PROJECT_INPUT" '.data.projects.edges[] | select(.node.name == $name) | .node.id' | head -1)
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}❌ Project '$PROJECT_INPUT' not found${NC}"
        exit 1
    fi
else
    PROJECT_ID=$PROJECT_INPUT
fi

echo -e "${GREEN}✓ Using project: $PROJECT_ID${NC}"
echo ""

# Get services in project
echo -e "${BLUE}🔍 Fetching services...${NC}"

SERVICES=$(curl -s "$API_URL" \
  -H "Authorization: Bearer $RAILWAY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"query { project(id: \\\"$PROJECT_ID\\\") { services { edges { node { id name } } } } }\"
  }")

echo "$SERVICES" | jq -r '.data.project.services.edges[].node | "\(.id) - \(.name)"'
echo ""

# Function to update service source
update_service_source() {
    local service_id=$1
    local service_name=$2
    local config_file=$3
    
    echo -e "${BLUE}📝 Updating ${service_name}...${NC}"
    echo -e "  Config file: ${config_file}"
    
    # Update service to use the specified config file
    RESULT=$(curl -s "$API_URL" \
      -H "Authorization: Bearer $RAILWAY_API_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"query\": \"mutation { serviceUpdate(id: \\\"$service_id\\\", input: { rootDirectory: \\\"/\\\", source: { configFile: \\\"$config_file\\\" } }) { id } }\"
      }")
    
    if echo "$RESULT" | jq -e '.data.serviceUpdate.id' > /dev/null; then
        echo -e "${GREEN}  ✓ Updated successfully${NC}"
        
        # Trigger redeploy
        echo -e "  ${YELLOW}→${NC} Triggering redeploy..."
        DEPLOY=$(curl -s "$API_URL" \
          -H "Authorization: Bearer $RAILWAY_API_TOKEN" \
          -H "Content-Type: application/json" \
          -d "{
            \"query\": \"mutation { serviceInstanceRedeploy(serviceId: \\\"$service_id\\\") { id } }\"
          }")
        
        if echo "$DEPLOY" | jq -e '.data.serviceInstanceRedeploy.id' > /dev/null; then
            echo -e "${GREEN}  ✓ Redeployment triggered${NC}"
        else
            echo -e "${YELLOW}  ⚠ Could not trigger redeploy (may auto-deploy)${NC}"
        fi
    else
        echo -e "${RED}  ✗ Update failed${NC}"
        echo "$RESULT" | jq .
    fi
    echo ""
}

# Find and update each service
echo -e "${YELLOW}🔧 Configuring services...${NC}"
echo ""

# Extract service IDs
FRONTEND_ID=$(echo "$SERVICES" | jq -r '.data.project.services.edges[] | select(.node.name == "monkey-coder") | .node.id')
BACKEND_ID=$(echo "$SERVICES" | jq -r '.data.project.services.edges[] | select(.node.name == "monkey-coder-backend") | .node.id')
ML_ID=$(echo "$SERVICES" | jq -r '.data.project.services.edges[] | select(.node.name == "monkey-coder-ml") | .node.id')

# Update services
if [ -n "$FRONTEND_ID" ]; then
    update_service_source "$FRONTEND_ID" "monkey-coder" "railway.json"
else
    echo -e "${YELLOW}⚠ Service 'monkey-coder' not found${NC}"
fi

if [ -n "$BACKEND_ID" ]; then
    update_service_source "$BACKEND_ID" "monkey-coder-backend" "railway-backend.json"
else
    echo -e "${YELLOW}⚠ Service 'monkey-coder-backend' not found${NC}"
fi

if [ -n "$ML_ID" ]; then
    update_service_source "$ML_ID" "monkey-coder-ml" "railway-ml.json"
else
    echo -e "${YELLOW}⚠ Service 'monkey-coder-ml' not found${NC}"
fi

echo -e "${GREEN}✅ Configuration complete!${NC}"
echo ""
echo -e "${BLUE}🌐 Check deployments at:${NC}"
echo "  https://railway.app/project/$PROJECT_ID"
echo ""
echo -e "${YELLOW}⏱  Deployments will take 5-10 minutes${NC}"
echo ""
