#!/usr/bin/env bash
#
# Configure Railway Environment Variables for AetherOS Project
#
# This script configures environment variables for monkey-coder services
# in the Railway AetherOS project (ID: 9n) following best practices for
# internal networking and secrets management.
#
# Prerequisites:
#   - Railway CLI installed: npm install -g @railway/cli
#   - Logged in: railway login
#   - Project linked: railway link 9n
#
# Usage:
#   ./scripts/configure-railway-aetheros.sh
#   ./scripts/configure-railway-aetheros.sh --dry-run  # Preview only
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="9n"
PROJECT_NAME="AetherOS"
DRY_RUN=false

# Parse arguments
for arg in "$@"; do
  case $arg in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [--dry-run] [--help]"
      echo ""
      echo "Options:"
      echo "  --dry-run    Preview changes without applying them"
      echo "  --help       Show this help message"
      exit 0
      ;;
  esac
done

# Helper functions
log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Railway CLI is available
if ! command -v railway &> /dev/null; then
  log_error "Railway CLI not found. Please install it first:"
  echo "  npm install -g @railway/cli"
  exit 1
fi

log_info "Starting Railway environment variable configuration for $PROJECT_NAME (ID: $PROJECT_ID)"

if [ "$DRY_RUN" = true ]; then
  log_warning "DRY RUN MODE - No changes will be applied"
fi

# Generate secure SANDBOX_TOKEN_SECRET
log_info "Generating secure SANDBOX_TOKEN_SECRET..."
SANDBOX_TOKEN=$(openssl rand -hex 32)
log_success "Generated 64-character token: ${SANDBOX_TOKEN:0:8}...(truncated for security)"

# Store the token securely for both services
SANDBOX_TOKEN_FILE="/tmp/sandbox_token_secret_$$.txt"
echo "$SANDBOX_TOKEN" > "$SANDBOX_TOKEN_FILE"
chmod 600 "$SANDBOX_TOKEN_FILE"
log_success "Token temporarily stored at: $SANDBOX_TOKEN_FILE"

echo ""
log_info "================================================================"
log_info "Configuration Plan:"
log_info "================================================================"
echo ""

# Service 1: monkey-coder-sandbox
echo "1. monkey-coder-sandbox service:"
echo "   - SANDBOX_TOKEN_SECRET=<generated-secure-token>"
echo "   - SANDBOX_ALLOW_ORIGINS=https://\${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}"
echo "   - SANDBOX_ALLOW_ORIGIN_REGEX=^https?://([a-z0-9-]+\.)*railway\.app$"
echo "   - LOG_LEVEL=info"
echo "   - PYTHONUNBUFFERED=1"
echo ""

# Service 2: monkey-coder-backend
echo "2. monkey-coder-backend service:"
echo "   - SANDBOX_SERVICE_URL=http://\${{monkey-coder-sandbox.RAILWAY_PRIVATE_DOMAIN}}"
echo "   - SANDBOX_TOKEN_SECRET=<same-as-sandbox>"
echo "   - PYTHON_ENV=production"
echo "   - PYTHONUNBUFFERED=1"
echo "   - LOG_LEVEL=info"
echo ""

# Service 3: monkey-coder (frontend)
echo "3. monkey-coder service (frontend):"
echo "   - NEXT_PUBLIC_API_URL=https://\${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}"
echo "   - NODE_ENV=production"
echo "   - NEXT_TELEMETRY_DISABLED=1"
echo ""

# Service 4: monkey-coder-ml (no changes)
echo "4. monkey-coder-ml service:"
echo "   - No changes needed (already configured)"
echo ""

log_info "================================================================"
echo ""

if [ "$DRY_RUN" = true ]; then
  log_info "Dry run complete. No changes were applied."
  rm -f "$SANDBOX_TOKEN_FILE"
  exit 0
fi

# Confirm with user
read -p "Do you want to apply these configurations? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
  log_warning "Configuration cancelled by user."
  rm -f "$SANDBOX_TOKEN_FILE"
  exit 0
fi

log_info "Applying configurations..."
echo ""

# Function to set variable with error handling
set_railway_variable() {
  local service=$1
  local var_name=$2
  local var_value=$3
  
  if railway variables set --service "$service" "$var_name=$var_value" 2>&1; then
    log_success "Set $var_name for $service"
    return 0
  else
    log_error "Failed to set $var_name for $service"
    return 1
  fi
}

# Configure monkey-coder-sandbox service
log_info "Configuring monkey-coder-sandbox service..."
set_railway_variable "monkey-coder-sandbox" "SANDBOX_TOKEN_SECRET" "$SANDBOX_TOKEN"
set_railway_variable "monkey-coder-sandbox" "SANDBOX_ALLOW_ORIGINS" 'https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}'
set_railway_variable "monkey-coder-sandbox" "SANDBOX_ALLOW_ORIGIN_REGEX" '^https?://([a-z0-9-]+\.)*railway\.app$'
set_railway_variable "monkey-coder-sandbox" "LOG_LEVEL" "info"
set_railway_variable "monkey-coder-sandbox" "PYTHONUNBUFFERED" "1"
echo ""

# Configure monkey-coder-backend service
log_info "Configuring monkey-coder-backend service..."
set_railway_variable "monkey-coder-backend" "SANDBOX_SERVICE_URL" 'http://${{monkey-coder-sandbox.RAILWAY_PRIVATE_DOMAIN}}'
set_railway_variable "monkey-coder-backend" "SANDBOX_TOKEN_SECRET" "$SANDBOX_TOKEN"
set_railway_variable "monkey-coder-backend" "PYTHON_ENV" "production"
set_railway_variable "monkey-coder-backend" "PYTHONUNBUFFERED" "1"
set_railway_variable "monkey-coder-backend" "LOG_LEVEL" "info"
echo ""

# Configure monkey-coder (frontend) service
log_info "Configuring monkey-coder (frontend) service..."
set_railway_variable "monkey-coder" "NEXT_PUBLIC_API_URL" 'https://${{monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}}'
set_railway_variable "monkey-coder" "NODE_ENV" "production"
set_railway_variable "monkey-coder" "NEXT_TELEMETRY_DISABLED" "1"
echo ""

# Clean up
rm -f "$SANDBOX_TOKEN_FILE"

echo ""
log_info "================================================================"
log_success "Configuration completed successfully!"
log_info "================================================================"
echo ""

log_info "Next steps:"
echo "  1. Verify the configuration:"
echo "     railway variables --service monkey-coder-sandbox"
echo "     railway variables --service monkey-coder-backend"
echo "     railway variables --service monkey-coder"
echo ""
echo "  2. Redeploy services for changes to take effect:"
echo "     railway redeploy --service monkey-coder-sandbox"
echo "     railway redeploy --service monkey-coder-backend"
echo "     railway redeploy --service monkey-coder"
echo ""
echo "  3. Check service health:"
echo "     railway logs --service monkey-coder-sandbox"
echo "     railway logs --service monkey-coder-backend"
echo ""
echo "  4. Test connectivity:"
echo "     curl https://<sandbox-domain>/health"
echo "     curl https://<backend-domain>/api/health"
echo ""

log_info "For detailed documentation, see:"
echo "  docs/deployment/railway-aetheros-config.md"
echo ""
