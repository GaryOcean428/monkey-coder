#!/bin/bash
# Railway Environment Variables Setup
# Run this after: railway login && railway link

railway variables set NODE_ENV="production"
railway variables set PYTHON_ENV="production"
railway variables set RAILWAY_ENVIRONMENT="production"
railway variables set JWT_SECRET_KEY="QwfZ4DUMAXpQIm010ntVFsiIh9T9Nlxf"
railway variables set NEXTAUTH_SECRET="52TLtnB8u95dfcfnqwsAfJP88e6NZkoO"
railway variables set NEXTAUTH_URL="https://coder.fastmonkey.au"
railway variables set NEXT_PUBLIC_API_URL="https://coder.fastmonkey.au"
railway variables set NEXT_PUBLIC_APP_URL="https://coder.fastmonkey.au"
railway variables set NEXT_OUTPUT_EXPORT="true"
railway variables set NEXT_TELEMETRY_DISABLED="1"
railway variables set OPENAI_API_KEY="your_real_openai_key_here"
railway variables set ANTHROPIC_API_KEY="your_real_anthropic_key_here"
railway variables set GOOGLE_API_KEY="your_real_google_key_here"
railway variables set GROQ_API_KEY="your_real_groq_key_here"
railway variables set RESEND_API_KEY="your_resend_api_key_here"
railway variables set NOTIFICATION_EMAIL_FROM="notifications@fastmonkey.au"
railway variables set ADMIN_NOTIFICATION_EMAILS="admin@fastmonkey.au"
railway variables set ENQUIRY_NOTIFICATION_EMAILS="support@fastmonkey.au"
railway variables set ROLLBACK_NOTIFICATION_EMAILS="devops@fastmonkey.au,admin@fastmonkey.au"
railway variables set STRIPE_PUBLIC_KEY="pk_test_placeholder"
railway variables set STRIPE_SECRET_KEY="sk_test_placeholder"
railway variables set STRIPE_WEBHOOK_SECRET="whsec_placeholder"
railway variables set SENTRY_DSN="your_sentry_dsn_here"

echo '✅ Environment variables setup completed!'
echo 'Now redeploy: railway redeploy'
