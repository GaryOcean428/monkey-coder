# Production Deployment - Monkey Coder

## Current Production Setup

### 🌐 Production URLs
- **Primary Domain**: https://coder.fastmonkey.au (custom domain)
- **Railway Domain**: https://monkey-coder.up.railway.app
- **Project Name**: AetherOS
- **Service Name**: monkey-coder

### 🚀 How It Works

## Architecture Overview

```
┌─────────────────┐         ┌─────────────────────────┐         ┌──────────────┐
│                 │         │                         │         │              │
│  CLI/SDK Users  │────────▶│  coder.fastmonkey.au   │────────▶│ AI Providers │
│                 │         │  (Railway Production)   │         │              │
└─────────────────┘         └─────────────────────────┘         └──────────────┘
       │                               │                                │
       │                               │                                │
    mk-* keys                   Handles routing                   Provider keys
 (user auth tokens)           billing, caching               (stored on Railway)
                              usage tracking
```

## Key Components

### 1. User Authentication Flow
```bash
# Users authenticate with Monkey Coder API
monkey auth login --email user@example.com

# Returns an API key like: mk-dev-EeSR4-BBpJsUTZCgIUjbdN3...
# This key authenticates with Monkey Coder, NOT directly with AI providers
```

### 2. API Request Flow
```bash
# User command
monkey implement "create a REST API"

# Translates to API call
POST https://coder.fastmonkey.au/v1/execute
Authorization: Bearer mk-dev-EeSR4-BBpJsUTZCgIUjbdN3...

# Monkey Coder API then:
1. Validates user authentication (mk-* key)
2. Checks usage limits and billing
3. Selects optimal AI provider (quantum routing)
4. Makes API call using ITS OWN provider keys
5. Tracks usage for billing
6. Returns response to user
```

### 3. Provider Keys (Secured on Railway)
All AI provider keys are stored as environment variables on Railway and NEVER exposed to users:

- **OpenAI**: `OPENAI_API_KEY` ✅
- **Anthropic**: `ANTHROPIC_API_KEY` ✅
- **Google**: `GOOGLE_API_KEY` ✅
- **Groq**: `GROQ_API_KEY` ✅
- **xAI/Grok**: `XAI_API_KEY` ✅
- **Perplexity**: `PERPLEXITY_API_KEY` ✅
- **Moonshot**: `MOONSHOT_API_KEY` ✅

## Railway Infrastructure

### Database & Storage
- **PostgreSQL**: `postgres.railway.internal:5432/railway`
- **Redis Cache**: `gondola.proxy.rlwy.net:45640`
- **Volume Mount**: `/data` for persistent storage

### Security & Authentication
- **JWT Secret**: Configured for user sessions
- **MFA**: Enabled for enhanced security
- **CORS Origins**: 
  - `https://coder.fastmonkey.au`
  - `https://monkey-coder.up.railway.app`
  - `http://localhost:*` (development)

### Billing Integration
- **Stripe Public Key**: `pk_live_51R6Te4AYIAu3GrrM...`
- **Stripe Secret Key**: Stored securely on Railway
- **Usage tracking**: Per-user, per-model usage metrics

## Business Model

### For Users
- **Single API Key**: One `mk-*` key for all AI providers
- **No Provider Management**: Don't need individual AI accounts
- **Unified Billing**: Single invoice for all AI usage
- **Advanced Features**: Quantum routing, caching, failover

### For Business
- **Revenue Model**: Markup on AI provider costs
- **Usage Analytics**: Complete visibility into model usage
- **Security**: Provider keys never exposed
- **Control**: Rate limiting, usage caps, model access control

## Environment Configuration

### Production Variables (Railway)
```bash
# Core
ENVIRONMENT=production
NODE_ENV=production
RAILWAY_PUBLIC_DOMAIN=coder.fastmonkey.au
BASE_URL=https://coder.fastmonkey.au

# AI Providers (all configured ✅)
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-api03-...
GOOGLE_API_KEY=AIzaSyC...
GROQ_API_KEY=gsk_lAf1TD...
XAI_API_KEY=xai-xd9APE...
PERPLEXITY_API_KEY=pplx-fe9de3...
MOONSHOT_API_KEY=sk-q9iSI53...

# Database
DATABASE_URL=postgresql://postgres:xxx@postgres.railway.internal:5432/railway
REDIS_URL=redis://default:xxx@gondola.proxy.rlwy.net:45640

# Security
JWT_SECRET_KEY=gIkpPB4h4KH+...
MFA_ENABLED=true

# Billing
STRIPE_PUBLIC_KEY=pk_live_51R6Te4...
STRIPE_SECRET_KEY=sk_live_51R6Te4...
```

## API Endpoints

### Core Endpoints
- `POST /v1/execute` - Execute AI task with routing
- `GET /v1/models` - List available models
- `GET /v1/providers` - List available providers
- `POST /v1/auth/login` - User authentication
- `POST /v1/auth/register` - User registration
- `GET /v1/billing/usage` - Usage statistics
- `POST /v1/billing/checkout` - Stripe checkout

### Health & Monitoring
- `GET /health` - API health check
- `GET /v1/capabilities` - System capabilities
- `GET /metrics` - Prometheus metrics (port 9090)

## Deployment Configuration

### railpack.json
```json
{
  "provider": "python",
  "packages": {
    "node": "22",
    "python": "3.11"
  },
  "deploy": {
    "startCommand": "/app/.venv/bin/python run_server.py",
    "healthCheckPath": "/health",
    "healthCheckTimeout": 300
  }
}
```

## CLI/SDK Connection

### CLI Configuration
Users configure the CLI to connect to production:
```bash
# ~/.config/monkey-coder/config.json
{
  "apiKey": "mk-dev-EeSR4-BBpJsUTZCgIUjbdN3...",
  "baseUrl": "https://coder.fastmonkey.au",
  "defaultPersona": "developer"
}
```

### Environment Variable
```bash
export MONKEY_CODER_BASE_URL=https://coder.fastmonkey.au
export MONKEY_CODER_API_KEY=mk-dev-EeSR4-BBpJsUTZCgIUjbdN3...
```

## Summary

The production deployment:
1. **Runs on Railway** at `coder.fastmonkey.au`
2. **Stores all provider API keys** securely as environment variables
3. **Users authenticate** with `mk-*` keys, not provider keys
4. **Handles all AI routing** through the centralized API
5. **Tracks usage** for billing through Stripe
6. **Provides value** through quantum routing, caching, and unified access

This architecture ensures:
- ✅ **Security**: Provider keys never exposed
- ✅ **Scalability**: Centralized load management
- ✅ **Monetization**: Usage-based billing
- ✅ **Reliability**: Failover and caching
- ✅ **Innovation**: Quantum routing and optimization