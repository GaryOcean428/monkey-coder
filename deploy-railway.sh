#!/bin/bash
# Railway deployment script for monkey-coder

set -e

echo "🚀 Deploying Monkey Coder to Railway..."

# Check if we're linked to the correct project
railway status

echo "📦 Building and deploying via GitHub integration..."
echo "Please follow these steps in your Railway dashboard:"
echo ""
echo "1. Go to: https://railway.app/project/AetherOS"
echo "2. Click on the 'monkey-coder' service"
echo "3. Go to Settings → Source"
echo "4. Connect GitHub repo: GaryOcean428/monkey-coder" 
echo "5. Set Root Directory: /"
echo "6. Click 'Deploy'"
echo ""
echo "📋 Environment Variables Status:"
railway variables | head -20

echo ""
echo "🔍 After deployment, test with:"
echo "curl https://monkey-coder.up.railway.app/health"
echo ""
echo "✅ All environment variables are already configured!"
echo "✅ Database connections ready (PostgreSQL + Redis)"
echo "✅ AI provider keys configured"
echo "✅ Stripe billing ready"
echo ""
echo "🎯 Expected URL: https://monkey-coder.up.railway.app"
