# Railway Deployment Checklist

## Pre-Deployment Validation

### ✅ 1. Build System Checks
- [ ] `yarn install` completes without errors
- [ ] `yarn build` succeeds for all packages
- [ ] `yarn typecheck` passes with no TypeScript errors
- [ ] `yarn test` passes with acceptable coverage
- [ ] `./validate_railway.sh` reports no critical errors

### ✅ 2. Port & Health Configuration
- [ ] Server binds to `0.0.0.0` (not localhost/127.0.0.1)
- [ ] Uses `process.env.PORT` with fallback to 8000
- [ ] Health check endpoint responds at `/health`
- [ ] Health check includes component status validation
- [ ] Start command configured: `/app/start_server.sh`

### 🔴 3. Inter-Service Communication (FIXED)
- [ ] ✅ No hard-coded service URLs in configuration
- [ ] ✅ Uses Railway domain variables: `${RAILWAY_PUBLIC_DOMAIN}`
- [ ] ✅ Internal communication uses private domains where appropriate
- [ ] ✅ WebSocket URLs use `wss://` for production

### ✅ 4. CORS Configuration
- [ ] ✅ No wildcard (`*`) origins in production
- [ ] ✅ Specific domains listed in `CORS_ORIGINS` environment variable
- [ ] ✅ Railway domains included: `${RAILWAY_PUBLIC_DOMAIN}`
- [ ] ✅ `allow_credentials: true` only with specific origins

### ✅ 5. Build Configuration
- [ ] ✅ Only `railpack.json` present (no conflicting Dockerfile/railway.toml)
- [ ] ✅ JSON syntax is valid (no trailing commas)
- [ ] ✅ Python 3.12 specified (Railway compatible)
- [ ] ✅ Node.js 20 specified for frontend build
- [ ] ✅ Virtual environment configured: `/app/venv`

### 🔴 6. Security Configuration (FIXED)
- [ ] ✅ No hard-coded secrets in `railpack.json`
- [ ] ✅ `JWT_SECRET_KEY` uses environment variable
- [ ] ✅ `NEXTAUTH_SECRET` uses environment variable
- [ ] ✅ Stripe keys use environment variables (no test placeholders)
- [ ] ✅ `.env.example` updated with security warnings

### ⚠️ 7. Logs & Monitoring
- [ ] Structured logging configured
- [ ] Sentry DSN configured for error tracking
- [ ] Performance metrics enabled
- [ ] Health check timeout appropriate (300s)

## Environment Variables Setup

### Required Variables
```bash
# Security (CRITICAL)
JWT_SECRET_KEY=<64-character-random-string>
NEXTAUTH_SECRET=<32-character-random-string>

# AI Providers (At least one required)
OPENAI_API_KEY=sk-<your-openai-key>
ANTHROPIC_API_KEY=sk-ant-<your-anthropic-key>

# Database (Automatically provided by Railway)
DATABASE_URL=<railway-postgresql-url>
```

### Optional but Recommended
```bash
# Error Monitoring
SENTRY_DSN=<your-sentry-dsn>

# CORS Security
CORS_ORIGINS=https://your-domain.railway.app

# Stripe (if using billing)
STRIPE_SECRET_KEY=sk_live_<your-live-key>
STRIPE_PUBLIC_KEY=pk_live_<your-live-key>
STRIPE_WEBHOOK_SECRET=whsec_<your-webhook-secret>
```

## Railway-Specific Checks

### 8. Railway Environment
- [ ] Railway CLI authenticated: `railway auth`
- [ ] Project linked: `railway link`
- [ ] Database service added: `railway add postgresql`
- [ ] Environment variables set in Railway dashboard
- [ ] Custom domain configured (if needed)

### 9. Networking & Domains
- [ ] `RAILWAY_PUBLIC_DOMAIN` environment variable available
- [ ] Custom domain DNS configured (if applicable)
- [ ] SSL certificate active
- [ ] Health check accessible from external networks

## Post-Deployment Verification

### 10. Service Health
- [ ] Service starts successfully: `railway logs --deployment`
- [ ] Health endpoint responds: `curl https://your-domain/health`
- [ ] API documentation accessible: `curl https://your-domain/api/docs`
- [ ] Frontend assets load correctly
- [ ] Database connections established

### 11. Security Verification
- [ ] HTTPS redirect working
- [ ] CORS headers properly set
- [ ] Security headers active (CSP, HSTS, etc.)
- [ ] No sensitive data in logs
- [ ] Environment variables not exposed in frontend

### 12. Performance Monitoring
- [ ] Response times < 2s for API endpoints
- [ ] Memory usage within limits
- [ ] CPU usage stable
- [ ] Error rates < 1%

## Troubleshooting Commands

```bash
# Check deployment status
railway status

# View recent logs
railway logs --deployment

# Check environment variables
railway variables

# Restart service
railway redeploy

# Local testing
yarn build && yarn test
python packages/core/run_server.py

# Validate configuration
./validate_railway.sh
python test_railway_config.py
```

## Rollback Plan

### If Deployment Fails:
1. **Check logs**: `railway logs --deployment`
2. **Verify environment variables**: `railway variables`
3. **Rollback to previous deployment**: Railway dashboard > Deployments > Redeploy previous
4. **Local testing**: Reproduce issue locally with same environment

### Emergency Contacts:
- **Railway Support**: https://railway.app/help
- **Repository Issues**: https://github.com/GaryOcean428/monkey-coder/issues

## Deployment Commands

```bash
# 1. Final validation
./validate_railway.sh
yarn build && yarn test

# 2. Deploy to Railway
railway up

# 3. Monitor deployment
railway logs --follow

# 4. Verify health
curl https://your-domain.railway.app/health

# 5. Check frontend
curl -I https://your-domain.railway.app/
```

---

**Last Updated:** 2025-01-20  
**Railway Configuration:** railpack.json (Python 3.12 + Node.js 20)  
**Health Check:** `/health` (300s timeout)  
**Security Status:** ✅ Hard-coded secrets removed  

This checklist ensures reliable, secure Railway deployments for the Monkey Coder platform.