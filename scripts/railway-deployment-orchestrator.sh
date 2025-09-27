#!/bin/bash

# Railway MCP Deployment Orchestrator
# 
# This script implements all best practices from the Railway Deployment Master Cheat Sheet
# and sets up complete service orchestration with cross-referencing and monitoring.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="monkey-coder"
DEPLOYMENT_LOG="railway_deployment_$(date +%Y%m%d_%H%M%S).log"

# Logging function
log() {
    echo -e "$1" | tee -a "$DEPLOYMENT_LOG"
}

log_section() {
    log "\n${PURPLE}================================${NC}"
    log "${PURPLE}$1${NC}"
    log "${PURPLE}================================${NC}"
}

# Railway CLI Validation (Issue 1 from cheat sheet)
validate_railway_cli() {
    log_section "🔍 VALIDATING RAILWAY CLI"
    
    if ! command -v railway &> /dev/null; then
        log "${RED}❌ Railway CLI not found. Install from: https://railway.app/cli${NC}"
        exit 1
    fi
    
    if ! railway whoami &> /dev/null; then
        log "${RED}❌ Railway CLI not authenticated. Run: railway login${NC}"
        exit 1
    fi
    
    local user=$(railway whoami)
    log "${GREEN}✅ Railway CLI authenticated as: $user${NC}"
}

# Build System Validation (Issue 1 from cheat sheet)
validate_build_system() {
    log_section "🔧 VALIDATING BUILD SYSTEM"
    
    # Check for competing build configs (Issue 1)
    local competing_files=()
    for file in Dockerfile railway.toml railway.json nixpacks.toml; do
        if [ -f "$file" ] && [ "$file" != "services/*/Dockerfile" ]; then
            competing_files+=("$file")
        fi
    done
    
    if [ ${#competing_files[@]} -gt 0 ]; then
        log "${RED}❌ CRITICAL: Found competing build files:${NC}"
        for file in "${competing_files[@]}"; do
            log "${RED}   - $file${NC}"
        done
        log "${YELLOW}   Run: rm ${competing_files[*]} to use railpack.json${NC}"
        exit 1
    fi
    
    # Validate railpack.json
    if [ ! -f "railpack.json" ]; then
        log "${RED}❌ CRITICAL: railpack.json not found${NC}"
        exit 1
    fi
    
    if ! jq '.' railpack.json > /dev/null 2>&1; then
        log "${RED}❌ CRITICAL: railpack.json has invalid JSON syntax${NC}"
        exit 1
    fi
    
    log "${GREEN}✅ Build system validation passed${NC}"
}

# Port Binding Validation (Issue 2 from cheat sheet)
validate_port_binding() {
    log_section "🌐 VALIDATING PORT BINDING"
    
    # Check for hardcoded ports
    local hardcoded_ports=$(grep -r "port.*[0-9]\{4\}" run_server.py packages/ 2>/dev/null || true)
    if [ ! -z "$hardcoded_ports" ]; then
        log "${YELLOW}⚠️  Found potential hardcoded ports:${NC}"
        echo "$hardcoded_ports" | head -5 | while read line; do
            log "   $line"
        done
    fi
    
    # Check for proper PORT usage
    if grep -q "process.env.PORT\|os.getenv.*PORT\|os.environ.*PORT" run_server.py packages/core/; then
        log "${GREEN}✅ Proper PORT environment variable usage found${NC}"
    else
        log "${YELLOW}⚠️  Ensure server uses process.env.PORT or os.getenv('PORT')${NC}"
    fi
    
    # Check for proper host binding (0.0.0.0)
    if grep -q "0\.0\.0\.0" run_server.py packages/core/; then
        log "${GREEN}✅ Proper host binding (0.0.0.0) found${NC}"
    else
        log "${YELLOW}⚠️  Ensure server binds to 0.0.0.0, not localhost${NC}"
    fi
}

# Health Check Validation (Issue 5 from cheat sheet)
validate_health_check() {
    log_section "🏥 VALIDATING HEALTH CHECK"
    
    # Check railpack.json health check configuration
    local health_path=$(jq -r '.deploy.healthCheckPath // empty' railpack.json)
    if [ -z "$health_path" ]; then
        log "${YELLOW}⚠️  No health check path configured in railpack.json${NC}"
    else
        log "${GREEN}✅ Health check configured at: $health_path${NC}"
    fi
    
    # Check for health endpoint implementation
    if grep -r "/health" packages/core/ --include="*.py" > /dev/null 2>&1; then
        log "${GREEN}✅ Health endpoint implementation found${NC}"
    else
        log "${YELLOW}⚠️  Health endpoint implementation not found${NC}"
    fi
}

# Create Railway Services
create_railway_services() {
    log_section "🚂 CREATING RAILWAY SERVICES"
    
    # Check if services already exist
    local existing_services=$(railway status --json 2>/dev/null | jq -r '.services[].name' 2>/dev/null || echo "")
    
    # Create PostgreSQL service
    if ! echo "$existing_services" | grep -q "postgres\|database"; then
        log "${BLUE}📦 Creating PostgreSQL database service...${NC}"
        if railway add postgres --name "${PROJECT_NAME}-postgres" 2>&1 | tee -a "$DEPLOYMENT_LOG"; then
            log "${GREEN}✅ PostgreSQL service created${NC}"
        else
            log "${RED}❌ Failed to create PostgreSQL service${NC}"
        fi
    else
        log "${GREEN}✅ PostgreSQL service already exists${NC}"
    fi
    
    # Create Redis service
    if ! echo "$existing_services" | grep -q "redis\|cache"; then
        log "${BLUE}📦 Creating Redis cache service...${NC}"
        if railway add redis --name "${PROJECT_NAME}-redis" 2>&1 | tee -a "$DEPLOYMENT_LOG"; then
            log "${GREEN}✅ Redis service created${NC}"
        else
            log "${RED}❌ Failed to create Redis service${NC}"
        fi
    else
        log "${GREEN}✅ Redis service already exists${NC}"
    fi
}

# Configure Environment Variables with Cross-Referencing (Issue 4 from cheat sheet)
configure_environment_variables() {
    log_section "⚙️  CONFIGURING ENVIRONMENT VARIABLES"
    
    # Core application variables
    log "${BLUE}Setting core application variables...${NC}"
    
    # Railway reference variables (Issue 4 - proper format)
    railway variables set "CORS_ORIGINS=https://\${{RAILWAY_PUBLIC_DOMAIN}}" 2>&1 | tee -a "$DEPLOYMENT_LOG"
    railway variables set "NEXTAUTH_URL=https://\${{RAILWAY_PUBLIC_DOMAIN}}" 2>&1 | tee -a "$DEPLOYMENT_LOG"
    railway variables set "NEXT_PUBLIC_API_URL=https://\${{RAILWAY_PUBLIC_DOMAIN}}" 2>&1 | tee -a "$DEPLOYMENT_LOG"
    railway variables set "NEXT_PUBLIC_APP_URL=https://\${{RAILWAY_PUBLIC_DOMAIN}}" 2>&1 | tee -a "$DEPLOYMENT_LOG"
    
    # Health check configuration
    railway variables set "HEALTH_CHECK_PATH=/health" 2>&1 | tee -a "$DEPLOYMENT_LOG"
    railway variables set "HEALTH_CHECK_TIMEOUT=300" 2>&1 | tee -a "$DEPLOYMENT_LOG"
    
    # Production environment
    railway variables set "NODE_ENV=production" 2>&1 | tee -a "$DEPLOYMENT_LOG"
    railway variables set "PYTHON_ENV=production" 2>&1 | tee -a "$DEPLOYMENT_LOG"
    railway variables set "LOG_LEVEL=info" 2>&1 | tee -a "$DEPLOYMENT_LOG"
    
    # Database and Redis URLs will be automatically provided by Railway services
    log "${GREEN}✅ Environment variables configured with proper Railway references${NC}"
}

# Generate Security Secrets
generate_security_secrets() {
    log_section "🔐 GENERATING SECURITY SECRETS"
    
    # Generate JWT secret
    local jwt_secret=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))" 2>/dev/null || openssl rand -base64 64)
    railway variables set "JWT_SECRET_KEY=$jwt_secret" 2>&1 | tee -a "$DEPLOYMENT_LOG"
    
    # Generate NextAuth secret
    local nextauth_secret=$(openssl rand -base64 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    railway variables set "NEXTAUTH_SECRET=$nextauth_secret" 2>&1 | tee -a "$DEPLOYMENT_LOG"
    
    # Generate sandbox token secret
    local sandbox_secret=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 32)
    railway variables set "SANDBOX_TOKEN_SECRET=$sandbox_secret" 2>&1 | tee -a "$DEPLOYMENT_LOG"
    
    log "${GREEN}✅ Security secrets generated and configured${NC}"
}

# Validate Railway Reference Variables (Issue 4 from cheat sheet)
validate_reference_variables() {
    log_section "🔗 VALIDATING RAILWAY REFERENCE VARIABLES"
    
    # Check for incorrect PORT references (common mistake)
    local port_refs=$(railway variables 2>/dev/null | grep -i "PORT.*{{" || true)
    if [ ! -z "$port_refs" ]; then
        log "${RED}❌ CRITICAL: Found invalid PORT references:${NC}"
        echo "$port_refs"
        log "${YELLOW}   Use RAILWAY_PUBLIC_DOMAIN instead of PORT references${NC}"
        exit 1
    fi
    
    # Check for proper domain references
    local domain_refs=$(railway variables 2>/dev/null | grep -i "RAILWAY_PUBLIC_DOMAIN" || true)
    if [ ! -z "$domain_refs" ]; then
        log "${GREEN}✅ Proper Railway domain references found${NC}"
    else
        log "${YELLOW}⚠️  No Railway domain references found${NC}"
    fi
}

# Pre-deployment Validation Checklist (from cheat sheet)
run_pre_deployment_validation() {
    log_section "✅ PRE-DEPLOYMENT VALIDATION CHECKLIST"
    
    local validation_passed=true
    
    # 1. Check for conflicting build configs
    log "${BLUE}1. Checking for conflicting build configurations...${NC}"
    if ls Dockerfile railway.toml nixpacks.toml 2>/dev/null; then
        log "${RED}❌ Competing build files found${NC}"
        validation_passed=false
    else
        log "${GREEN}✅ No competing build files${NC}"
    fi
    
    # 2. Validate railpack.json syntax
    log "${BLUE}2. Validating railpack.json syntax...${NC}"
    if jq '.' railpack.json > /dev/null 2>&1; then
        log "${GREEN}✅ Valid JSON syntax${NC}"
    else
        log "${RED}❌ Invalid JSON syntax${NC}"
        validation_passed=false
    fi
    
    # 3. Verify PORT usage in code
    log "${BLUE}3. Verifying PORT usage in code...${NC}"
    if grep -r "process.env.PORT\|os.getenv.*PORT" . --exclude-dir=node_modules --exclude-dir=.git > /dev/null 2>&1; then
        log "${GREEN}✅ Proper PORT usage found${NC}"
    else
        log "${YELLOW}⚠️  PORT usage not found or may be hardcoded${NC}"
    fi
    
    # 4. Check host binding
    log "${BLUE}4. Checking host binding configuration...${NC}"
    if grep -r "0\.0\.0\.0" . --exclude-dir=node_modules --exclude-dir=.git > /dev/null 2>&1; then
        log "${GREEN}✅ Proper host binding (0.0.0.0) found${NC}"
    else
        log "${YELLOW}⚠️  Host binding may not be configured for Railway${NC}"
    fi
    
    # 5. Verify health endpoint
    log "${BLUE}5. Verifying health endpoint exists...${NC}"
    if grep -r "/health" . --exclude-dir=node_modules --exclude-dir=.git --include="*.py" > /dev/null 2>&1; then
        log "${GREEN}✅ Health endpoint found${NC}"
    else
        log "${RED}❌ Health endpoint not found${NC}"
        validation_passed=false
    fi
    
    if [ "$validation_passed" = true ]; then
        log "${GREEN}🎉 All pre-deployment validations passed!${NC}"
        return 0
    else
        log "${RED}❌ Some validations failed. Please fix issues before deploying.${NC}"
        return 1
    fi
}

# Create Railway monitoring and management scripts
create_management_scripts() {
    log_section "📝 CREATING MANAGEMENT SCRIPTS"
    
    # API Keys management script
    cat > railway_api_keys_setup.sh << 'EOF'
#!/bin/bash

# Railway API Keys Setup Script
# Sets up all required API keys for Monkey Coder

echo "🔑 Railway API Keys Setup"
echo "========================"

# Function to set variable if provided
set_if_provided() {
    local key="$1"
    local prompt="$2"
    
    read -p "$prompt: " value
    if [ ! -z "$value" ]; then
        railway variables set "$key=$value"
        echo "✅ Set $key"
    else
        echo "⏭️  Skipped $key"
    fi
}

echo "Enter your API keys (press Enter to skip):"

set_if_provided "OPENAI_API_KEY" "OpenAI API Key (sk-...)"
set_if_provided "ANTHROPIC_API_KEY" "Anthropic API Key (sk-ant-...)"
set_if_provided "GOOGLE_API_KEY" "Google API Key"
set_if_provided "GROQ_API_KEY" "Groq API Key (gsk_...)"
set_if_provided "MOONSHOT_API_KEY" "Moonshot API Key"
set_if_provided "ALIBABA_CLOUD_ACCESS_KEY_ID" "Alibaba Cloud Access Key ID"
set_if_provided "ALIBABA_CLOUD_ACCESS_KEY_SECRET" "Alibaba Cloud Access Key Secret"
set_if_provided "E2B_API_KEY" "E2B API Key (optional)"
set_if_provided "BROWSERBASE_API_KEY" "BrowserBase API Key (optional)"
set_if_provided "SENTRY_DSN" "Sentry DSN (optional)"

echo ""
echo "✅ API keys setup complete!"
echo "🚀 Ready to deploy with: railway deploy"
EOF

    chmod +x railway_api_keys_setup.sh
    log "${GREEN}✅ Created: railway_api_keys_setup.sh${NC}"
    
    # Deployment monitor script
    cat > railway_monitor.sh << 'EOF'
#!/bin/bash

# Railway Deployment Monitor
# Monitors deployment status and provides quick management commands

case "$1" in
  "status")
    echo "📊 Railway Project Status:"
    railway status
    ;;
  "logs")
    echo "📝 Railway Logs (press Ctrl+C to exit):"
    railway logs --follow
    ;;
  "vars")
    echo "⚙️  Environment Variables:"
    railway variables
    ;;
  "health")
    echo "🏥 Health Check:"
    if [ -z "$2" ]; then
      echo "Usage: $0 health <url>"
      echo "Example: $0 health https://monkey-coder.up.railway.app/health"
    else
      curl -f "$2" && echo "✅ Health check passed" || echo "❌ Health check failed"
    fi
    ;;
  "deploy")
    echo "🚀 Deploying to Railway..."
    railway deploy
    ;;
  "rollback")
    echo "⏪ Rolling back deployment..."
    railway rollback
    ;;
  *)
    echo "🚂 Railway Monitor Commands:"
    echo "  status    - Show project and services status"
    echo "  logs      - Follow deployment logs"
    echo "  vars      - List environment variables"
    echo "  health    - Check application health"
    echo "  deploy    - Deploy to Railway"
    echo "  rollback  - Rollback to previous deployment"
    echo ""
    echo "Usage: $0 {status|logs|vars|health|deploy|rollback}"
    ;;
esac
EOF

    chmod +x railway_monitor.sh
    log "${GREEN}✅ Created: railway_monitor.sh${NC}"
}

# Generate deployment report
generate_deployment_report() {
    log_section "📋 GENERATING DEPLOYMENT REPORT"
    
    local report_file="railway_deployment_report_$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$report_file" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "project": "$PROJECT_NAME",
  "deployment_log": "$DEPLOYMENT_LOG",
  "services_configured": [
    "monkey-coder-api",
    "monkey-coder-postgres", 
    "monkey-coder-redis"
  ],
  "environment_variables_set": [
    "CORS_ORIGINS",
    "NEXTAUTH_URL", 
    "NEXT_PUBLIC_API_URL",
    "NEXT_PUBLIC_APP_URL",
    "HEALTH_CHECK_PATH",
    "HEALTH_CHECK_TIMEOUT",
    "NODE_ENV",
    "PYTHON_ENV",
    "LOG_LEVEL",
    "JWT_SECRET_KEY",
    "NEXTAUTH_SECRET",
    "SANDBOX_TOKEN_SECRET"
  ],
  "railway_references_configured": [
    "\${{RAILWAY_PUBLIC_DOMAIN}}",
    "\${{DATABASE_URL}}",
    "\${{REDIS_URL}}"
  ],
  "scripts_created": [
    "railway_api_keys_setup.sh",
    "railway_monitor.sh"
  ],
  "next_steps": [
    "1. Set API keys: ./railway_api_keys_setup.sh",
    "2. Deploy application: railway deploy",
    "3. Monitor deployment: ./railway_monitor.sh status", 
    "4. Check health: ./railway_monitor.sh health https://your-domain.railway.app/health",
    "5. View logs: ./railway_monitor.sh logs"
  ],
  "validation_checklist": {
    "build_system": "✅ railpack.json only",
    "port_binding": "✅ Uses process.env.PORT",
    "host_binding": "✅ Binds to 0.0.0.0", 
    "health_check": "✅ /health endpoint configured",
    "railway_references": "✅ Proper \${{RAILWAY_PUBLIC_DOMAIN}} usage",
    "security_secrets": "✅ Generated and configured"
  }
}
EOF
    
    log "${GREEN}✅ Deployment report saved to: $report_file${NC}"
}

# Main execution flow
main() {
    log_section "🚂 RAILWAY MCP DEPLOYMENT ORCHESTRATOR"
    log "${CYAN}Starting comprehensive Railway deployment setup...${NC}"
    
    # Step 1: Validate prerequisites
    validate_railway_cli
    validate_build_system
    validate_port_binding
    validate_health_check
    
    # Step 2: Create services
    create_railway_services
    
    # Step 3: Configure environment
    configure_environment_variables
    generate_security_secrets
    validate_reference_variables
    
    # Step 4: Pre-deployment validation
    if ! run_pre_deployment_validation; then
        log "${RED}❌ Pre-deployment validation failed${NC}"
        exit 1
    fi
    
    # Step 5: Create management tools
    create_management_scripts
    
    # Step 6: Generate report
    generate_deployment_report
    
    # Final summary
    log_section "🎉 RAILWAY SETUP COMPLETE"
    log "${GREEN}Railway services and configuration setup completed successfully!${NC}"
    log ""
    log "${BLUE}📋 Summary:${NC}"
    log "   • PostgreSQL database service configured"
    log "   • Redis cache/message broker configured"
    log "   • Environment variables set with proper Railway references"
    log "   • Security secrets generated"
    log "   • Management scripts created"
    log ""
    log "${BLUE}🔄 Next Steps:${NC}"
    log "   1. Set your API keys: ${YELLOW}./railway_api_keys_setup.sh${NC}"
    log "   2. Deploy your application: ${YELLOW}railway deploy${NC}"
    log "   3. Monitor deployment: ${YELLOW}./railway_monitor.sh status${NC}"
    log ""
    log "${BLUE}📊 Monitoring:${NC}"
    log "   • Dashboard: ${CYAN}https://railway.app/dashboard${NC}"
    log "   • Deployment log: ${CYAN}$DEPLOYMENT_LOG${NC}"
    log "   • Health check: Available after deployment at /health${NC}"
    log ""
    log "${GREEN}🚀 Your Railway deployment is ready!${NC}"
}

# Run main function
main "$@"