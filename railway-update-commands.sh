#!/bin/bash
#
# Railway Service Configuration Commands
# Generated: 2025-10-13T08:25:24.152657
#
# This script contains all commands to update Railway services
# for the AetherOS Monkey Coder project.
#
# Usage: 
#   1. Review the commands below
#   2. Execute manually or run: bash railway-update-commands.sh
#   3. Set critical secrets separately (marked with TODO)
#

set -e

echo "======================================"
echo "Railway Service Configuration Update"
echo "======================================"
echo ""

# Check Railway CLI
if ! command -v railway &> /dev/null; then
    echo "✗ Railway CLI not found!"
    echo "  Install with: npm install -g @railway/cli"
    echo "  Or use: yarn dlx @railway/cli@latest"
    exit 1
fi

echo "✓ Railway CLI available"
echo ""


# ============================================================================
# Service: monkey-coder
# Service ID: ccc58ca2-1f4b-4086-beb6-2321ac7dab40
# Config File: railpack.json
# ============================================================================

echo "🔧 Updating monkey-coder..."
echo "  Service ID: ccc58ca2-1f4b-4086-beb6-2321ac7dab40"

# Required Variables
railway variables set --service ccc58ca2-1f4b-4086-beb6-2321ac7dab40 "RAILWAY_CONFIG_FILE=railpack.json"
railway variables set --service ccc58ca2-1f4b-4086-beb6-2321ac7dab40 "NODE_ENV=production"
railway variables set --service ccc58ca2-1f4b-4086-beb6-2321ac7dab40 "NEXT_OUTPUT_EXPORT=true"
railway variables set --service ccc58ca2-1f4b-4086-beb6-2321ac7dab40 "NEXT_TELEMETRY_DISABLED=1"
railway variables set --service ccc58ca2-1f4b-4086-beb6-2321ac7dab40 "NEXT_PUBLIC_APP_URL=https://coder.fastmonkey.au"
railway variables set --service ccc58ca2-1f4b-4086-beb6-2321ac7dab40 "NEXT_PUBLIC_API_URL=https://monkey-coder-backend-production.up.railway.app"

# Optional Variables (uncomment if needed)
# railway variables set --service ccc58ca2-1f4b-4086-beb6-2321ac7dab40 "NEXT_PUBLIC_ENV=production"

echo "✓ monkey-coder variables set"
echo ""

# ============================================================================
# Service: monkey-coder-backend
# Service ID: 6af98d25-621b-4a2d-bbcb-7acb314fbfed
# Config File: railpack-backend.json
# ============================================================================

echo "🔧 Updating monkey-coder-backend..."
echo "  Service ID: 6af98d25-621b-4a2d-bbcb-7acb314fbfed"

# Required Variables
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "RAILWAY_CONFIG_FILE=railpack-backend.json"
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "ENV=production"
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "NODE_ENV=production"
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "PYTHON_ENV=production"
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "LOG_LEVEL=info"
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "NEXT_PUBLIC_APP_URL=https://coder.fastmonkey.au"
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "PUBLIC_APP_URL=https://coder.fastmonkey.au"
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "NEXT_PUBLIC_API_URL=https://monkey-coder-backend-production.up.railway.app"
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "CORS_ORIGINS=https://coder.fastmonkey.au"
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "TRUSTED_HOSTS=coder.fastmonkey.au,*.railway.app,*.railway.internal"
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "ENABLE_SECURITY_HEADERS=true"
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "ENABLE_CORS=true"
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "HEALTH_CHECK_PATH=/api/health"
railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "ENABLE_HEALTH_CHECKS=true"

# Critical Secrets (SET THESE MANUALLY)
# TODO: railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "JWT_SECRET_KEY=YOUR_VALUE_HERE"
# TODO: railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "NEXTAUTH_SECRET=YOUR_VALUE_HERE"
# TODO: railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "OPENAI_API_KEY=YOUR_VALUE_HERE"
# TODO: railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "ANTHROPIC_API_KEY=YOUR_VALUE_HERE"

# Optional Variables (uncomment if needed)
# railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "GOOGLE_API_KEY=YOUR_VALUE_HERE"
# railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "GROQ_API_KEY=YOUR_VALUE_HERE"
# railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "XAI_API_KEY=YOUR_VALUE_HERE"
# railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "RESEND_API_KEY=YOUR_VALUE_HERE"
# railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "NOTIFICATION_EMAIL_FROM=noreply@fastmonkey.au"
# railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "EMAIL_PROVIDER=resend"
# railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "SENTRY_DSN=YOUR_VALUE_HERE"
# railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "SESSION_BACKEND=redis"
# railway variables set --service 6af98d25-621b-4a2d-bbcb-7acb314fbfed "RATE_LIMIT_BACKEND=redis"

echo "✓ monkey-coder-backend variables set"
echo ""

# ============================================================================
# Service: monkey-coder-ml
# Service ID: 07ef6ac7-e412-4a24-a0dc-74e301413eaa
# Config File: railpack-ml.json
# ============================================================================

echo "🔧 Updating monkey-coder-ml..."
echo "  Service ID: 07ef6ac7-e412-4a24-a0dc-74e301413eaa"

# Required Variables
railway variables set --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa "RAILWAY_CONFIG_FILE=railpack-ml.json"
railway variables set --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa "ENV=production"
railway variables set --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa "NODE_ENV=production"
railway variables set --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa "PYTHON_ENV=production"
railway variables set --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa "LOG_LEVEL=info"
railway variables set --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa "TRANSFORMERS_CACHE=/app/.cache/huggingface"
railway variables set --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa "HEALTH_CHECK_PATH=/api/health"

# Optional Variables (uncomment if needed)
# railway variables set --service 07ef6ac7-e412-4a24-a0dc-74e301413eaa "CUDA_VISIBLE_DEVICES=0"

echo "✓ monkey-coder-ml variables set"
echo ""

echo "======================================"
echo "Configuration Update Complete"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Set critical secrets in Railway Dashboard"
echo "2. Verify: railway variables --service <SERVICE_ID>"
echo "3. Redeploy: railway up --service <SERVICE_ID>"
echo ""
