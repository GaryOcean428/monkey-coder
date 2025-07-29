# Environment Variables Checklist for Unified Deployment

This document lists all environment variables required for the unified Monkey Coder service deployment on Railway.

## 🚨 Critical Variables (Required)

### AI Provider API Keys
```bash
# Required for quantum routing and AI orchestration
OPENAI_API_KEY=sk-xxxxx                    # OpenAI GPT models
ANTHROPIC_API_KEY=sk-ant-xxxxx            # Claude models  
GOOGLE_API_KEY=xxxxx                      # Gemini models

# Optional but recommended for extended model support
GROQ_API_KEY=gsk_xxxxx                    # Groq models (optional)
GROK_API_KEY=xxxxx                        # Grok/X.AI models (optional)
GROK_BASE_URL=https://api.x.ai/v1         # Grok API base URL (optional)
```

### Database & Cache (Auto-configured by Railway)
```bash
# Railway automatically provides these when you add PostgreSQL and Redis services
DATABASE_URL=postgresql://user:pass@host:port/db    # Auto-provided by Railway PostgreSQL
REDIS_URL=redis://host:port                         # Auto-provided by Railway Redis
```

### Security & Authentication
```bash
# CRITICAL: Generate a strong secret key for JWT tokens
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-chars

# JWT Configuration (optional, has defaults)
JWT_ALGORITHM=HS256                       # Default: HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30        # Default: 30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7           # Default: 7

# MFA Settings (optional)
MFA_ENABLED=false                         # Default: false
MFA_ISSUER=Monkey Coder                   # Default: Monkey Coder
MFA_SECRET_LENGTH=32                      # Default: 32
```

## ⚙️ System Configuration (Auto-configured)

### Railway System Variables
```bash
# Railway automatically provides these - DO NOT SET MANUALLY
PORT=8000                                 # Auto-set by Railway
HOST=0.0.0.0                             # Auto-set by Railway
RAILWAY_ENVIRONMENT=production            # Auto-set by Railway
```

### Logging & Monitoring
```bash
# Logging Configuration (optional, has defaults)
LOG_LEVEL=INFO                           # Default: INFO (options: DEBUG, INFO, WARNING, ERROR)
JSON_LOGS=true                           # Default: true (Railway prefers JSON logs)
PERFORMANCE_LOGS=true                    # Default: true

# Sentry Error Tracking (optional but recommended)
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx # Your Sentry DSN for error tracking
ENVIRONMENT=production                    # Default: development
```

## 🔧 Optional Services & Features

### Billing & Payments
```bash
# Stripe Integration (required if using billing features)
STRIPE_API_KEY=sk_test_xxxxx             # Stripe secret key
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx     # Stripe publishable key (for frontend)
```

### Sandbox Execution (Optional)
```bash
# Only needed if using sandbox service for code execution
SANDBOX_SERVICE_URL=http://localhost:8001        # Default: http://localhost:8001
SANDBOX_TOKEN_SECRET=your-sandbox-secret         # Default: default-secret
```

### MCP & GitHub Integration (Optional)
```bash
# GitHub integration for MCP servers (optional)
GITHUB_TOKEN=ghp_xxxxx                   # GitHub personal access token

# MCP Configuration (optional, has defaults)
ENABLE_MCP=true                          # Default: true
ENABLE_METRICS=true                      # Default: true
ENABLE_PRICING_MIDDLEWARE=true           # Default: true
```

## 🚀 Railway Deployment Configuration

### In Your Railway Dashboard:

1. **Service**: `monkey-coder` (ID: `ccc58ca2-1f4b-4086-beb6-2321ac7dab40`)

2. **Required Variables to Set**:
   ```bash
   # Copy these into Railway Environment Variables section
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key
   GOOGLE_API_KEY=your_google_key
   JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-chars
   ```

3. **Optional but Recommended**:
   ```bash
   SENTRY_DSN=your_sentry_dsn
   GROQ_API_KEY=your_groq_key
   LOG_LEVEL=INFO
   JSON_LOGS=true
   ```

4. **Auto-Configured by Railway** (don't set these):
   - `PORT` (automatically set to Railway's port)
   - `DATABASE_URL` (when PostgreSQL service is connected)
   - `REDIS_URL` (when Redis service is connected)
   - `RAILWAY_ENVIRONMENT`

## ⚠️ Important Notes

### JWT Secret Key Generation
Generate a strong JWT secret key:
```bash
# Use one of these methods to generate a secure key:
openssl rand -hex 32
python -c "import secrets; print(secrets.token_hex(32))"
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### Database & Redis Services
Make sure your Railway project has:
- ✅ **PostgreSQL** service added and connected
- ✅ **Redis** service added and connected
- ✅ Both services should auto-inject their URLs into your environment

### Variable Priority
1. **Critical**: AI API keys, JWT secret, database connections
2. **Important**: Sentry DSN for error tracking
3. **Optional**: Additional AI providers, MCP features, billing integration

## 🔍 Testing Variables

After deployment, verify variables are working:

```bash
# Test health endpoint (should show active components)
curl https://monkey-coder.up.railway.app/health

# Test providers endpoint (requires API key)
curl -H "Authorization: Bearer your-api-key" \
     https://monkey-coder.up.railway.app/v1/providers
```

## 🆘 Troubleshooting

### Common Issues:
1. **500 errors**: Check JWT_SECRET_KEY is set
2. **Provider errors**: Verify AI API keys are correct
3. **Database errors**: Ensure PostgreSQL service is connected
4. **Cache errors**: Ensure Redis service is connected

### Check Railway Logs:
Go to Railway Dashboard → Your Service → Logs to see detailed error messages.

---

**✅ Minimum Required Setup**: Just set the 4 critical variables above and ensure PostgreSQL + Redis services are connected. The service will work with defaults for everything else.