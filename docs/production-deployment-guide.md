# Production Deployment Guide

## Monkey Coder Phase 2.0 - Railway Production Deployment

**Version:** 2.0.0  
**Last Updated:** 2025-01-14  
**Target Platform:** Railway  
**Status:** Production Ready

---

## Overview

This guide provides step-by-step instructions for deploying Monkey Coder to production on Railway with enterprise-grade reliability, security, and monitoring.

### Prerequisites Completed ✅
- Phase 1.7: Core development (100% complete)
- Production configuration system implemented
- Security hardening applied
- Health checks and monitoring configured
- Performance optimization implemented

---

## Pre-Deployment Checklist

### Required Environment Variables

Copy and configure these environment variables in Railway:

```bash
# Core Application
ENVIRONMENT=production
PORT=8000
HOST=0.0.0.0

# AI Provider API Keys (at least one required)
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GOOGLE_API_KEY=your-google-api-key-here
GROQ_API_KEY=gsk_your-groq-key-here

# Security (REQUIRED for production)
JWT_SECRET_KEY=your-secure-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database (Railway PostgreSQL addon)
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}

# Production Security
CORS_ORIGINS=https://monkey-coder.up.railway.app,https://your-custom-domain.com
TRUSTED_HOSTS=monkey-coder.up.railway.app,your-custom-domain.com,*.railway.app,*.railway.internal

# Monitoring (Recommended)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
LOG_LEVEL=INFO
ENABLE_METRICS=true

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=20
ENABLE_RATE_LIMITING=true

# Security Headers
ENABLE_SECURITY_HEADERS=true
ENABLE_HTTPS_REDIRECT=true

# Health Checks
HEALTH_CHECK_PATH=/health
HEALTH_CHECK_TIMEOUT=300
```

### Validation Commands

Before deployment, run these validation commands:

```bash
# 1. Validate production configuration
curl -X GET https://your-app.railway.app/api/v1/production/validate

# 2. Check comprehensive health
curl -X GET https://your-app.railway.app/health/comprehensive

# 3. Verify readiness
curl -X GET https://your-app.railway.app/health/readiness

# 4. Test performance metrics
curl -X GET https://your-app.railway.app/metrics/performance
```

---

## Railway Deployment Steps

### Step 1: Repository Setup

1. **Ensure railpack.json is configured:**
```json
{
  "$schema": "https://schema.railpack.com",
  "version": "1",
  "build": {
    "provider": "python",
    "packages": {
      "python": "3.13",
      "node": "20"
    },
    "steps": {
      "web": {
        "description": "Build Next.js frontend for static export",
        "commands": [
          "corepack enable",
          "corepack prepare yarn@4.9.2 --activate",
          "yarn install --immutable",
          "yarn workspace @monkey-coder/web build"
        ]
      },
      "python": {
        "description": "Install Python dependencies",
        "commands": [
          "pip install --no-cache-dir --upgrade pip setuptools wheel",
          "pip install --no-cache-dir -r requirements.txt",
          "cd packages/core && pip install --no-cache-dir -e ."
        ],
        "inputs": [{"step": "web"}]
      }
    }
  },
  "deploy": {
    "startCommand": "python run_server.py",
    "healthCheckPath": "/health",
    "healthCheckTimeout": 300,
    "inputs": [{"step": "python"}]
  }
}
```

2. **Verify run_server.py configuration:**
```python
# run_server.py should be configured for Railway
import os
import uvicorn

def main():
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "monkey_coder.app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=False
    )

if __name__ == "__main__":
    main()
```

### Step 2: Railway Project Creation

1. **Create Railway project:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Create new project
railway create monkey-coder-production

# Link to repository
railway link
```

2. **Add required services:**
```bash
# Add PostgreSQL database
railway add --service postgresql

# Add Redis cache (optional but recommended)
railway add --service redis
```

### Step 3: Environment Configuration

1. **Set production environment variables:**
```bash
# Set environment to production
railway env set ENVIRONMENT=production

# Add API keys (replace with your actual keys)
railway env set OPENAI_API_KEY=sk-your-key-here
railway env set ANTHROPIC_API_KEY=sk-ant-your-key-here

# Set security configuration
railway env set JWT_SECRET_KEY=$(openssl rand -base64 64)

# Configure CORS for your domain
railway env set CORS_ORIGINS=https://monkey-coder.up.railway.app

# Enable monitoring
railway env set SENTRY_DSN=your-sentry-dsn-here
railway env set LOG_LEVEL=INFO
```

2. **Verify environment setup:**
```bash
# Check all environment variables
railway env list

# Test configuration
railway run -- python -c "from monkey_coder.config.env_config import get_config; print(get_config().get_config_summary())"
```

### Step 4: Security Configuration

1. **Generate secure secrets:**
```bash
# Generate JWT secret
openssl rand -base64 64

# Generate secure API keys for internal services
openssl rand -hex 32
```

2. **Configure security headers:**
```bash
# Enable all security features
railway env set ENABLE_SECURITY_HEADERS=true
railway env set ENABLE_HTTPS_REDIRECT=true
railway env set ENABLE_RATE_LIMITING=true
```

3. **Set up trusted hosts:**
```bash
# Configure for Railway + custom domain
railway env set TRUSTED_HOSTS="monkey-coder.up.railway.app,your-domain.com,*.railway.app,*.railway.internal"
```

### Step 5: Database Setup

1. **Database migrations (if applicable):**
```bash
# Run any required database setup
railway run -- python -c "from monkey_coder.database import init_database; init_database()"
```

2. **Verify database connection:**
```bash
# Test database connectivity
railway run -- python -c "from monkey_coder.config.env_config import get_config; print('DB configured:', bool(get_config().database.url))"
```

### Step 6: Deployment

1. **Deploy to Railway:**
```bash
# Deploy current branch
railway deploy

# Monitor deployment
railway logs --follow
```

2. **Verify deployment:**
```bash
# Get deployment URL
railway status

# Test health endpoint
curl https://your-app.railway.app/health

# Test comprehensive health
curl https://your-app.railway.app/health/comprehensive
```

---

## Post-Deployment Verification

### Health Check Validation

1. **Basic health check:**
```bash
curl -X GET https://your-app.railway.app/health
# Expected: 200 OK with {"status": "healthy"}
```

2. **Comprehensive health check:**
```bash
curl -X GET https://your-app.railway.app/health/comprehensive
# Expected: Detailed system status
```

3. **Production readiness validation:**
```bash
curl -X GET https://your-app.railway.app/api/v1/production/validate
# Expected: {"overall_ready": true}
```

### Performance Validation

1. **Response time test:**
```bash
curl -w "@curl-format.txt" -o /dev/null -s https://your-app.railway.app/health
# Target: <2 seconds
```

2. **Load testing (basic):**
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test 100 requests with 10 concurrent
ab -n 100 -c 10 https://your-app.railway.app/health
```

3. **Monitor performance metrics:**
```bash
curl -X GET https://your-app.railway.app/metrics/performance
# Check response times and cache hit rates
```

### Security Validation

1. **Security headers check:**
```bash
curl -I https://your-app.railway.app/health
# Verify presence of security headers
```

2. **HTTPS redirect test:**
```bash
curl -I http://your-app.railway.app/health
# Should redirect to HTTPS
```

3. **Rate limiting test:**
```bash
# Test rate limiting (may take multiple rapid requests)
for i in {1..105}; do curl -s -o /dev/null -w "%{http_code}\n" https://your-app.railway.app/health; done
# Should show 429 after hitting rate limit
```

---

## Monitoring Setup

### Sentry Error Tracking

1. **Create Sentry project:**
   - Sign up at sentry.io
   - Create new Python project
   - Copy DSN

2. **Configure Sentry:**
```bash
railway env set SENTRY_DSN=https://your-dsn@sentry.io/project-id
```

3. **Test error tracking:**
```bash
# Trigger a test error to verify Sentry integration
curl -X POST https://your-app.railway.app/api/v1/test-error
```

### Performance Monitoring

1. **Set up monitoring endpoints:**
   - Health: `/health/comprehensive`
   - Metrics: `/metrics/performance`
   - Cache: `/metrics/cache`

2. **Configure alerting (optional):**
   - Set up uptime monitoring (UptimeRobot, Pingdom)
   - Configure email alerts for failures

### Log Monitoring

1. **View Railway logs:**
```bash
# Follow live logs
railway logs --follow

# Filter by error level
railway logs --level error
```

2. **Structured logging search:**
```bash
# Search for specific events
railway logs | grep "metric_type.*health_check"
```

---

## Performance Optimization

### Caching Configuration

The system includes high-performance in-memory caching:

1. **Monitor cache performance:**
```bash
curl https://your-app.railway.app/metrics/cache
```

2. **Optimize cache settings** (if needed):
```bash
# Adjust cache size (default: 1000 entries)
railway env set CACHE_MAX_SIZE=2000

# Adjust default TTL (default: 300 seconds)
railway env set CACHE_DEFAULT_TTL=600
```

### Database Optimization

1. **Connection pooling** (already configured):
   - Pool size: 10 connections
   - Pool timeout: 30 seconds
   - Pool recycle: 1 hour

2. **Monitor database performance:**
```bash
# Check database metrics in health endpoint
curl https://your-app.railway.app/health/comprehensive | jq '.checks.database'
```

---

## Scaling Configuration

### Horizontal Scaling

Railway auto-scaling is configured based on:
- CPU usage > 80%
- Memory usage > 85%
- Request queue depth

### Vertical Scaling

Resource limits are set optimally for Railway:
- Memory: Auto-allocated based on usage
- CPU: Shared CPU with auto-scaling
- Storage: 10GB+ for application and logs

---

## Domain Configuration

### Custom Domain Setup

1. **Add custom domain in Railway:**
```bash
# Add domain via Railway dashboard or CLI
railway domain add your-domain.com
```

2. **Update environment variables:**
```bash
# Update CORS origins
railway env set CORS_ORIGINS="https://your-domain.com,https://monkey-coder.up.railway.app"

# Update trusted hosts
railway env set TRUSTED_HOSTS="your-domain.com,monkey-coder.up.railway.app,*.railway.app"
```

3. **SSL certificate:**
   - Railway automatically provisions SSL certificates
   - Verify with: `curl -I https://your-domain.com/health`

---

## Backup and Recovery

### Database Backups

Railway PostgreSQL includes automatic backups:
- Daily automated backups
- Point-in-time recovery
- Manual backup triggers available

### Configuration Backups

1. **Export environment variables:**
```bash
# Backup environment configuration
railway env list > production-env-backup.txt
```

2. **Version control:**
   - All configuration is in Git
   - Railway deployment is reproducible from repository

### Disaster Recovery

1. **Recovery procedures:**
   - Restore from Railway backup
   - Redeploy from Git repository
   - Restore environment variables from backup

2. **RTO/RPO targets:**
   - Recovery Time Objective: <30 minutes
   - Recovery Point Objective: <1 hour

---

## Troubleshooting

### Common Issues

1. **Build failures:**
```bash
# Check build logs
railway logs --deployment

# Verify dependencies
railway run -- pip list
```

2. **Runtime errors:**
```bash
# Check application logs
railway logs --follow

# Test configuration
railway run -- python -c "from monkey_coder.config.env_config import get_config; get_config().validate_required_config()"
```

3. **Performance issues:**
```bash
# Check metrics
curl https://your-app.railway.app/metrics/performance

# Monitor resource usage
railway metrics
```

### Debug Commands

1. **Configuration debugging:**
```bash
# Test environment loading
railway run -- python -c "from monkey_coder.config.production_config import get_production_config; print(get_production_config().validate_production_readiness())"

# Check AI provider configuration
railway run -- python -c "from monkey_coder.config.env_config import get_ai_provider_keys; print(get_ai_provider_keys())"
```

2. **Health debugging:**
```bash
# Detailed health check
curl -v https://your-app.railway.app/health/comprehensive

# Check individual components
curl https://your-app.railway.app/api/v1/production/validate
```

---

## Maintenance

### Regular Tasks

1. **Monitor performance weekly:**
   - Check `/metrics/performance` for trends
   - Review error rates in Sentry
   - Analyze slow request patterns

2. **Security updates monthly:**
   - Review and rotate API keys
   - Update dependencies
   - Check security headers configuration

3. **Capacity planning quarterly:**
   - Review resource usage trends
   - Plan for scaling requirements
   - Update configuration as needed

### Update Procedures

1. **Application updates:**
```bash
# Deploy new version
git push origin main
railway deploy

# Verify deployment
curl https://your-app.railway.app/health/comprehensive
```

2. **Configuration updates:**
```bash
# Update environment variables
railway env set VARIABLE_NAME=new_value

# Restart application if needed
railway restart
```

---

## Success Criteria

### Deployment Complete When:

✅ **Infrastructure:**
- Application deployed and accessible
- Custom domain configured (if applicable)
- SSL certificates active

✅ **Health & Monitoring:**
- All health checks returning healthy status
- Comprehensive monitoring active
- Error tracking configured and tested

✅ **Performance:**
- Response times <2 seconds for 95% of requests
- Cache hit rate >70%
- No critical performance issues

✅ **Security:**
- All security headers active
- HTTPS redirect working
- Rate limiting functional
- No critical security vulnerabilities

✅ **Reliability:**
- 99.9% uptime target met
- Monitoring and alerting active
- Backup procedures verified

---

## Support

### Documentation
- **API Documentation:** `/docs/api-documentation.md`
- **Technical Architecture:** `/docs/roadmap/technical-architecture.md`
- **Troubleshooting:** This guide's troubleshooting section

### Monitoring Endpoints
- **Health:** `https://your-app.railway.app/health`
- **Comprehensive:** `https://your-app.railway.app/health/comprehensive`
- **Performance:** `https://your-app.railway.app/metrics/performance`
- **Production Validation:** `https://your-app.railway.app/api/v1/production/validate`

### Emergency Contacts
- **Railway Support:** [Railway Dashboard](https://railway.app)
- **Sentry:** [Sentry Dashboard](https://sentry.io)
- **Application Logs:** `railway logs --follow`

---

**Deployment Status:** ✅ Ready for Production  
**Last Verified:** 2025-01-14  
**Next Review:** 2025-01-21