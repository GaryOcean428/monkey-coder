# API Key Testing Guide

> **How to get API keys and test the Monkey Coder system**
> Last Updated: 2025-01-29

## 🔑 **How to Get an API Key**

### Option 1: Development API Key (Easiest for Testing)

**No authentication required** - Perfect for testing and development:

```bash
curl -X POST https://monkey-coder-production.up.railway.app/v1/auth/keys/dev \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "key": "mk-AbCdEf123456...",
  "key_id": "key_12345abc",
  "name": "Development Key 20250129_143022",
  "description": "Development/testing API key created via /v1/auth/keys/dev endpoint",
  "status": "active",
  "created_at": "2025-01-29T14:30:22.123456",
  "expires_at": "2025-02-28T14:30:22.123456",
  "permissions": ["*"]
}
```

⚠️ **Save the `key` value** - this is your API key for testing!

### Option 2: Authenticated API Key Creation

If you have JWT authentication set up:

```bash
curl -X POST https://monkey-coder-production.up.railway.app/v1/auth/keys \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "My Test Key",
    "description": "API key for testing CLI commands",
    "expires_days": 30
  }'
```

## 🧪 **Testing the API Key**

### 1. Test API Key Validation

```bash
curl -X GET https://monkey-coder-production.up.railway.app/v1/auth/status \
  -H "Authorization: Bearer mk-YOUR_API_KEY_HERE"
```

### 2. Test CLI Authentication

```bash
# Set your API key
export MONKEY_CODER_API_KEY="mk-YOUR_API_KEY_HERE"

# Test CLI commands
monkey auth status
monkey health
```

### 3. Test Task Execution

```bash
curl -X POST https://monkey-coder-production.up.railway.app/v1/execute \
  -H "Authorization: Bearer mk-YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "build",
    "task_type": "code_generation",
    "context": {
      "project_type": "web",
      "environment": "development"
    },
    "superclause_config": {
      "persona": "developer",
      "complexity_threshold": 0.5
    }
  }'
```

## 🚀 **Railway Environment Setup**

### Current Railway Configuration

The Railway deployment should have these environment variables set:

```bash
# Required AI Provider Keys (at least one)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
GROQ_API_KEY=gsk_...
GROK_API_KEY=...

# Security (auto-generated if not set)
JWT_SECRET_KEY=your-secret-key

# Environment
ENVIRONMENT=production
DEBUG=false

# Optional
SENTRY_DSN=your-sentry-dsn
```

### Testing Railway Deployment

1. **Check Health Endpoint:**
   ```bash
   curl https://monkey-coder-production.up.railway.app/health
   ```

2. **Check API Documentation:**
   - Visit: https://monkey-coder-production.up.railway.app/api/docs

3. **Get Development API Key:**
   ```bash
   curl -X POST https://monkey-coder-production.up.railway.app/v1/auth/keys/dev
   ```

## 📋 **API Key Management**

### List Your API Keys

```bash
curl -X GET https://monkey-coder-production.up.railway.app/v1/auth/keys \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Revoke an API Key

```bash
curl -X DELETE https://monkey-coder-production.up.railway.app/v1/auth/keys/key_12345abc \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### View API Key Statistics (Admin Only)

```bash
curl -X GET https://monkey-coder-production.up.railway.app/v1/auth/keys/stats \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🛠️ **CLI Configuration**

### Option 1: Environment Variable

```bash
export MONKEY_CODER_API_KEY="mk-YOUR_API_KEY_HERE"
monkey auth status
```

### Option 2: CLI Configuration

```bash
monkey auth login --api-key mk-YOUR_API_KEY_HERE
```

### Option 3: Configuration File

Edit `~/.monkey-coder/config.json`:

```json
{
  "apiKey": "mk-YOUR_API_KEY_HERE",
  "baseUrl": "https://monkey-coder-production.up.railway.app"
}
```

## 🔍 **Testing Single-Word Commands**

Test the enhanced persona validation:

```bash
# These should all work now with intelligent enhancement
monkey execute "build"
monkey execute "test" 
monkey execute "debug"
monkey execute "analyze"
monkey execute "deploy"
```

## 🎯 **Testing Enhanced Features**

### Test Environment Configuration

```bash
curl -X GET https://monkey-coder-production.up.railway.app/v1/capabilities \
  -H "Authorization: Bearer mk-YOUR_API_KEY_HERE"
```

### Test Persona Validation

```bash
curl -X POST https://monkey-coder-production.up.railway.app/v1/router/debug \
  -H "Authorization: Bearer mk-YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "build",
    "task_type": "code_generation"
  }'
```

### Test Orchestration Patterns

```bash
curl -X POST https://monkey-coder-production.up.railway.app/v1/execute \
  -H "Authorization: Bearer mk-YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a comprehensive web application with testing",
    "task_type": "code_generation",
    "context": {
      "complexity": "high",
      "domains": ["frontend", "backend", "testing"]
    }
  }'
```

## ❓ **Troubleshooting**

### Common Issues

1. **"API key required" error:**
   - Make sure you're including the `Authorization: Bearer mk-...` header
   - Verify your API key starts with `mk-` and is longer than 10 characters

2. **"Invalid API key or token" error:**
   - Your API key may have expired (development keys expire after 30 days)
   - Create a new development API key using the `/v1/auth/keys/dev` endpoint

3. **"Insufficient permissions" error:**
   - Development keys have full permissions (`*`)
   - Custom keys may have limited permissions - check with `/v1/auth/keys`

4. **CLI not connecting:**
   - Check your `~/.monkey-coder/config.json` file
   - Verify the `baseUrl` points to the correct Railway URL
   - Test the API directly with curl first

### Debug Commands

```bash
# Test direct API connection
curl -v https://monkey-coder-production.up.railway.app/health

# Test API key validation
curl -v -X GET https://monkey-coder-production.up.railway.app/v1/auth/status \
  -H "Authorization: Bearer mk-YOUR_API_KEY_HERE"

# Check CLI configuration
monkey config show

# Test with verbose logging
monkey --verbose execute "test command"
```

## 🔄 **API Key Lifecycle**

### Development Keys
- **Created via:** `/v1/auth/keys/dev` (no auth required)
- **Permissions:** Full access (`*`)
- **Expiration:** 30 days
- **Use case:** Testing, development, proof of concept

### Production Keys
- **Created via:** `/v1/auth/keys` (JWT auth required)
- **Permissions:** Configurable
- **Expiration:** Configurable
- **Use case:** Production applications, CI/CD, long-term usage

### Key Security
- Keys are hashed in the system - actual keys are never stored
- Keys can be revoked immediately via the API
- Usage tracking helps monitor key activity
- Permissions can be restricted per key

## 📞 **Support**

If you're still having issues getting an API key or testing the system:

1. **Check the health endpoint:** https://monkey-coder-production.up.railway.app/health
2. **Try creating a development key:** `curl -X POST .../v1/auth/keys/dev`
3. **Check Railway logs** for any deployment issues
4. **Verify environment variables** are set correctly on Railway

The development API key endpoint should work without any authentication - this is the easiest way to get started testing the system!