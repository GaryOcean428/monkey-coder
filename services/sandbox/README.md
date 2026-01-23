# Sandbox Service

## Overview

The Sandbox Service provides secure, isolated execution environments for code execution and browser automation using E2B and BrowserBase integrations.

## ⚠️ Optional Service

**This service is OPTIONAL for most Monkey Coder deployments.**

### When You DON'T Need This Service

- **CLI-only deployment**: The CLI has its own local Docker sandbox (`packages/cli/src/sandbox/`)
- **No browser automation**: Backend doesn't require BrowserBase integration
- **No cloud execution API**: Not offering code execution as a service
- **Cost-sensitive**: Each Railway service adds compute costs

### When You DO Need This Service

- **Browser automation**: Need BrowserBase for web scraping/testing from web clients
- **Cloud-based execution**: Offering code execution API to web/mobile users
- **No local Docker**: Backend runs in environment without Docker daemon access
- **Multi-tenant platform**: Need centralized sandbox resource management

## Architecture

### Two Independent Sandbox Systems

```
┌──────────────────────────────────────────────────────────┐
│                  Monkey Coder Platform                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  CLI Local Sandbox          Remote Sandbox Service      │
│  ─────────────────          ───────────────────────      │
│  packages/cli/src/sandbox/  services/sandbox/            │
│                                                          │
│  • Local Docker             • FastAPI service            │
│  • dockerode library        • E2B integration            │
│  • 3 modes: docker/spawn    • BrowserBase integration   │
│  • Auto-fallback            • Centralized monitoring    │
│  • No network calls         • HTTP API                  │
│                                                          │
│  Used by: CLI users         Used by: Web clients        │
│  Required: NO (optional)    Required: NO (optional)     │
└──────────────────────────────────────────────────────────┘
```

**Important**: The CLI and this service are **completely independent**. The CLI never calls this service.

## Features

### Code Execution (E2B)
- Python code execution in isolated containers
- Resource limits (CPU, memory, disk)
- Timeout enforcement
- Execution result capture

### Browser Automation (BrowserBase)
- Playwright-powered browser automation
- Chromium in isolated environment
- Screenshot and DOM capture
- Network request monitoring

### Security
- Process isolation via Docker
- Non-root user execution
- Network namespace isolation
- Resource quotas
- Authentication tokens
- CORS protection

### Monitoring
- Real-time resource usage tracking
- Execution metrics collection
- Performance monitoring
- Health check endpoints

## Local Development

### Prerequisites

```bash
# System dependencies
sudo apt-get install -y chromium xvfb supervisor

# Python dependencies
pip install -r requirements.txt
```

### Configuration

Create `.env` in this directory:

```bash
# Security
SANDBOX_TOKEN_SECRET=your-secure-secret-here

# CORS
SANDBOX_ALLOW_ORIGINS=http://localhost:3000
SANDBOX_ALLOW_ORIGIN_REGEX=^https?://([a-z0-9-]+\.)*railway\.app$

# Optional: E2B integration
E2B_API_KEY=your-e2b-api-key

# Optional: BrowserBase integration
BROWSERBASE_API_KEY=your-browserbase-api-key
BROWSERBASE_PROJECT_ID=your-browserbase-project-id

# Resource limits
SANDBOX_MAX_MEMORY_MB=512
SANDBOX_MAX_CPU_PERCENT=50.0
SANDBOX_MODE=1
```

### Running Locally

```bash
# Direct Python
python -m sandbox.main

# Or with uvicorn
uvicorn sandbox.main:app --host 0.0.0.0 --port 8001 --reload

# With Docker
docker build -t monkey-coder-sandbox .
docker run -p 8001:8001 \
  -e SANDBOX_TOKEN_SECRET=test-secret \
  monkey-coder-sandbox
```

### Testing

```bash
# Health check
curl http://localhost:8001/health

# Execute code (requires token)
curl -X POST http://localhost:8001/sandbox/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sandbox_type": "code",
    "action": "execute",
    "code": "print(\"Hello from sandbox\")",
    "timeout": 30
  }'

# Get metrics
curl http://localhost:8001/sandbox/metrics \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Railway Deployment

### Step 1: Create Service

```bash
# In Railway dashboard:
# 1. Click "New" → "Empty Service"
# 2. Name: "monkey-coder-sandbox"
# 3. Settings → Root Directory: "/services/sandbox"
```

### Step 2: Configure Environment

Set these environment variables in Railway:

```bash
SANDBOX_TOKEN_SECRET=<generate-secure-random-secret>
SANDBOX_ALLOW_ORIGINS=https://your-frontend.railway.app
E2B_API_KEY=<optional-e2b-key>
BROWSERBASE_API_KEY=<optional-browserbase-key>
BROWSERBASE_PROJECT_ID=<optional-browserbase-project>
```

### Step 3: Connect Backend (Optional)

If you want the backend to use this service, add to backend environment:

```bash
SANDBOX_SERVICE_URL=http://${{monkey-coder-sandbox.RAILWAY_PRIVATE_DOMAIN}}
SANDBOX_TOKEN_SECRET=${{monkey-coder-sandbox.SANDBOX_TOKEN_SECRET}}
```

### Step 4: Deploy

Railway will automatically:
1. Detect `railpack.json`
2. Build Docker image from `Dockerfile`
3. Start service with supervisor
4. Monitor health at `/health`

## API Endpoints

### Health Check
```
GET /health
GET /healthz
GET /sandbox/health
```

Returns service health status and resource usage.

### Execute Code/Browser Action
```
POST /sandbox/execute
Authorization: Bearer <token>
Content-Type: application/json

{
  "sandbox_type": "code|browser",
  "action": "execute",
  "code": "print('hello')",  # For code execution
  "url": "https://example.com",  # For browser actions
  "timeout": 30,
  "metadata": {}
}
```

### Get Metrics
```
GET /sandbox/metrics
Authorization: Bearer <token>
```

Returns execution statistics and resource usage.

### Cleanup Resources
```
POST /sandbox/cleanup
Authorization: Bearer <token>
```

Manually trigger cleanup of idle sandboxes.

## Security Considerations

### Process Isolation
- Runs as non-root user `sandbox` (UID 1001)
- Separate user/group with limited privileges
- Read-only root filesystem (optional)
- All capabilities dropped

### Resource Limits
- Memory: 512MB default (configurable)
- CPU: 50% of one core default
- Process limit: 50 PIDs
- Network rate limiting
- Execution timeout enforcement

### Network Security
- Network isolation enabled by default
- CORS protection for web requests
- Trusted host middleware
- Authentication token required
- HTTPS recommended in production

### Authentication
- Bearer token authentication
- Token generation via shared secret
- 30-minute token expiration
- Single-use execution IDs

## File Structure

```
services/sandbox/
├── Dockerfile              # Docker image definition
├── railpack.json          # Railway deployment config
├── requirements.txt       # Python dependencies
├── requirements.in        # Source requirements
├── supervisord.conf       # Process manager config
├── README.md             # This file
└── sandbox/
    ├── __init__.py
    ├── main.py           # FastAPI application
    ├── e2b_integration.py       # E2B sandbox manager
    ├── browserbase_integration.py  # BrowserBase manager
    ├── security.py       # Security utilities
    └── monitoring.py     # Resource monitoring
```

## Troubleshooting

### Service Won't Start

**Check logs**:
```bash
railway logs --service monkey-coder-sandbox
```

**Common issues**:
- Missing `SANDBOX_TOKEN_SECRET` environment variable
- Invalid E2B or BrowserBase API keys (if configured)
- Port binding issues (should bind to `0.0.0.0:$PORT`)

### Health Check Fails

**Verify endpoint**:
```bash
curl https://your-sandbox.railway.app/health
```

**Should return**:
```json
{
  "status": "healthy",
  "service": "sandbox",
  "version": "1.0.0",
  "timestamp": "2026-01-23T...",
  "resources": {...}
}
```

### Backend Can't Connect

**Check environment variables in backend**:
- `SANDBOX_SERVICE_URL` should point to Railway internal domain
- `SANDBOX_TOKEN_SECRET` must match sandbox service

**Test connectivity**:
```bash
# From backend service
curl http://monkey-coder-sandbox.railway.internal/health
```

### Resource Limits Exceeded

**Increase limits** via environment variables:
```bash
SANDBOX_MAX_MEMORY_MB=1024
SANDBOX_MAX_CPU_PERCENT=100
```

**Monitor usage**:
```bash
curl https://your-sandbox.railway.app/sandbox/metrics \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Cost Considerations

### Railway Pricing Impact

Each Railway service adds to your bill:
- **Compute**: ~$5-20/month depending on usage
- **Additional resources**: Memory, CPU allocated separately
- **Data transfer**: Minimal for internal service-to-service

### Cost Optimization

1. **Don't deploy if not needed**: CLI has local Docker
2. **Use Railway sleep**: Configure to sleep after inactivity
3. **Resource limits**: Set appropriate memory/CPU limits
4. **Cleanup idle resources**: Enable automatic cleanup
5. **Monitor usage**: Track via `/sandbox/metrics`

### Alternative: Local Docker

For CLI-only deployments, use the built-in local Docker sandbox:
- **Cost**: $0 (uses user's local Docker)
- **Performance**: Lower latency (no network calls)
- **Limitations**: Requires Docker installed locally

## Related Documentation

- [Sandbox Service Deployment Guide](../../docs/deployment/sandbox-service-deployment-guide.md)
- [CLI Sandbox Execution](../../packages/cli/SANDBOX_EXECUTION.md)
- [Railway Service Configuration](../../RAILWAY_SERVICE_CONFIG.md)
- [Railway Architecture](../../docs/deployment/railway-architecture.md)

## Support

For issues or questions:
- GitHub Issues: [monkey-coder/issues](https://github.com/GaryOcean428/monkey-coder/issues)
- Documentation: `docs/deployment/`
- Railway Support: [Railway Help](https://help.railway.app/)
