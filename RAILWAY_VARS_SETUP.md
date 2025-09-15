# RAILWAY DASHBOARD ENVIRONMENT SETUP

## Step 1: Access Railway Dashboard
1. Go to: https://railway.app/dashboard
2. Select your project (AetherOS or similar)
3. Click on the monkey-coder service
4. Go to the "Variables" tab

## Step 2: Add Environment Variables
Copy and paste these variables one by one:

NODE_ENV=production
PYTHON_ENV=production
RAILWAY_ENVIRONMENT=production
JWT_SECRET_KEY=QwfZ4DUMAXpQIm010ntVFsiIh9T9Nlxf
NEXTAUTH_SECRET=52TLtnB8u95dfcfnqwsAfJP88e6NZkoO
NEXTAUTH_URL=https://coder.fastmonkey.au
NEXT_PUBLIC_API_URL=https://coder.fastmonkey.au
NEXT_PUBLIC_APP_URL=https://coder.fastmonkey.au
NEXT_OUTPUT_EXPORT=true
NEXT_TELEMETRY_DISABLED=1
OPENAI_API_KEY=your_real_openai_key_here
ANTHROPIC_API_KEY=your_real_anthropic_key_here
GOOGLE_API_KEY=your_real_google_key_here
GROQ_API_KEY=your_real_groq_key_here
STRIPE_PUBLIC_KEY=pk_test_placeholder
STRIPE_SECRET_KEY=sk_test_placeholder
STRIPE_WEBHOOK_SECRET=whsec_placeholder
SENTRY_DSN=your_sentry_dsn_here

## Step 3: Verify Build Configuration
1. Go to "Settings" tab
2. Ensure "Build Method" is set to "Railpack"
3. Ensure "Start Command" is: python run_server.py

## Step 4: Redeploy
1. Go to "Deployments" tab
2. Click "Redeploy"
3. Monitor logs for successful frontend build

## Critical Variables for Frontend:
- NEXT_OUTPUT_EXPORT=true (enables static export)
- NEXTAUTH_URL=https://coder.fastmonkey.au (correct URL)
- NEXT_PUBLIC_API_URL=https://coder.fastmonkey.au (API endpoint)

## Security Notes:
- Replace JWT_SECRET_KEY with a real secure key
- Replace NEXTAUTH_SECRET with a real secure key
- Replace AI provider API keys with real keys

Generated: Mon Sep 15 09:19:08 UTC 2025