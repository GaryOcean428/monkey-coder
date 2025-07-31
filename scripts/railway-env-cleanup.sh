#!/bin/bash

# Railway Environment Variables Cleanup Script
# Updates URLs and removes deprecated variables for single-service deployment

set -e

echo "🧹 Updating Railway environment variables for single-service deployment..."

# Remove deprecated AI provider keys (now handled by GROQ)
echo "🗑️  Removing deprecated AI provider variables..."
railway variables --remove QWEN_API_KEY || echo "QWEN_API_KEY not found"
railway variables --remove MOONSHOT_API_KEY || echo "MOONSHOT_API_KEY not found"

# Remove Docker-specific variables (not needed for Railway deployment)
echo "🗑️  Removing Docker variables (Railway doesn't need these)..."
railway variables --remove DOCKER_PAT || echo "DOCKER_PAT not found"
railway variables --remove DOCKER_USERNAME || echo "DOCKER_USERNAME not found" 
railway variables --remove BUILDER_NAME || echo "BUILDER_NAME not found"

# Remove legacy service URLs from when there were separate frontend/backend services
echo "🗑️  Removing legacy separate service URLs..."
railway variables --remove MONKEY_CODER_WEB_URL || echo "MONKEY_CODER_WEB_URL not found (was for separate frontend service)"
railway variables --remove RAILWAY_SERVICE_NEXTJS_URL || echo "RAILWAY_SERVICE_NEXTJS_URL not found"

# Update URL variables for single-service deployment
echo "✅ Updating URL variables for single FastAPI service with static frontend..."

# Set correct NEXT_PUBLIC_APP_URL to custom domain
railway variables --set NEXT_PUBLIC_APP_URL=https://coder.fastmonkey.au || echo "NEXT_PUBLIC_APP_URL already set"

# Verify MONKEY_CODER_API_URL points to the Railway app URL (fallback)
railway variables --set MONKEY_CODER_API_URL=https://monkey-coder.up.railway.app || echo "MONKEY_CODER_API_URL already set"

# Update CORS origins for both custom domain and Railway URL
railway variables --set ALLOWED_ORIGINS="coder.fastmonkey.au,monkey-coder.up.railway.app,https://coder.fastmonkey.au,https://monkey-coder.up.railway.app,http://localhost:*" || echo "ALLOWED_ORIGINS already set"

# Ensure production environment is properly set
railway variables --set NODE_ENV=production || echo "NODE_ENV already set"
railway variables --set PYTHONUNBUFFERED=1 || echo "PYTHONUNBUFFERED already set"

echo "🎉 Environment variable updates completed!"
echo ""
echo "📋 Updated URL configuration:"
echo "   • Custom Domain: coder.fastmonkey.au (NEXT_PUBLIC_APP_URL)"
echo "   • Railway Fallback: monkey-coder.up.railway.app (MONKEY_CODER_API_URL)"
echo "   • Single Service: FastAPI serves both API and static frontend"
echo ""
echo "📋 Current critical variables:"
railway variables | grep -E "(NEXT_PUBLIC_APP_URL|MONKEY_CODER_API_URL|BASE_URL|ALLOWED_ORIGINS)" || echo "Error displaying variables"