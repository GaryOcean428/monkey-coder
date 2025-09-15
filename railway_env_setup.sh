#!/bin/bash
# Railway Environment Variables Setup Script
# Run this script with Railway CLI to configure all environment variables

set -e

echo '🚀 Setting up Railway environment variables...'
echo 'Make sure you have Railway CLI installed and are logged in'
echo 'Run: railway login'
echo 'Run: railway link'
echo ''

# Check if Railway CLI is available
if ! command -v railway &> /dev/null; then
    echo '❌ Railway CLI not found. Install it first:'
    echo '   npm install -g @railway/cli'
    exit 1
fi

railway variables set NODE_ENV="production"
railway variables set PYTHON_ENV="production"
railway variables set RAILWAY_ENVIRONMENT="production"
railway variables set JWT_SECRET_KEY="Yh3DZpNGikV4ZQBJtpWcF5ZdvhaueBjs"
railway variables set NEXTAUTH_SECRET="5rn2xTDuVrkG7V6OMvUK6Asui32Sl11Y"
railway variables set NEXTAUTH_URL="https://coder.fastmonkey.au"
railway variables set NEXT_PUBLIC_API_URL="https://coder.fastmonkey.au"
railway variables set NEXT_PUBLIC_APP_URL="https://coder.fastmonkey.au"
railway variables set NEXT_OUTPUT_EXPORT="true"
railway variables set NEXT_TELEMETRY_DISABLED="1"
railway variables set OPENAI_API_KEY="KloSl9r8OMcVehcCu55keT3mTGRPMst4"
railway variables set ANTHROPIC_API_KEY="9lEFj3ERIVsprjHmIfsMocVbWLJhDHzg"
railway variables set GOOGLE_API_KEY="YxCkFdqKcMPm4cin9laL3jpU0bsJ069W"
railway variables set GROQ_API_KEY="i6iK5ac7fxrBOw5a7Qvn1JCq7bZxJsuT"
# DATABASE_URL is already configured
railway variables set STRIPE_PUBLIC_KEY="pk_test_placeholder"
railway variables set STRIPE_SECRET_KEY="sk_test_placeholder"
railway variables set STRIPE_WEBHOOK_SECRET="whsec_placeholder"
railway variables set SENTRY_DSN="nLhzfZZSxJ6b9YMU1JXDmc7ONWo2RVS9"

echo '✅ Environment variables setup completed!'
echo 'Now redeploy your service:'
echo '   railway redeploy'