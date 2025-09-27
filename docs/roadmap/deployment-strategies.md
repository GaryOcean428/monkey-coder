[← Back to Roadmap Index](./index.md)

## Deployment Strategies

### Railway Deployment

**Production Environment:**

```bash
# Railway deployment configuration
railway login
railway link monkey-coder-production
railway deploy

# Environment variables (set via Railway dashboard)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
SENTRY_DSN=HTTPS://...
DATABASE_URL=PostgreSQL://...
REDIS_URL=Redis://...
```

**Railway Railpack Configuration:**

> **Note**: This project uses Railway's `railpack.json` system, not traditional Docker deployment. Railway handles containerization internally.

```json
{
  "$schema": "https://schema.railpack.com",
  "version": "1",
  "metadata": {
    "name": "monkey-coder",
    "description": "AI-powered code generation and analysis platform"
  },
  "build": {
    "provider": "python",
    "packages": {
      "python": "3.12.11"
    },
    "steps": {
      "install": {
        "commands": [
          "python -m venv /app/.venv",
          "/app/.venv/bin/pip install --upgrade pip setuptools wheel",
          "/app/.venv/bin/pip install -r requirements.txt"
        ]
      }
    },
    "env": {
      "NODE_ENV": "production",
      "PYTHON_ENV": "production"
    }
  },
  "deploy": {
    "startCommand": "/app/.venv/bin/python /app/run_server.py",
    "healthCheckPath": "/health",
    "healthCheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

**Key Benefits of Railpack vs Docker:**
- No Dockerfile required - Railway handles containerization
- Simpler configuration and maintenance
- Automatic dependency resolution
- Built-in health checking and restart policies
- Optimized for Railway's infrastructure

### CI/CD Pipeline

**GitHub Actions Workflow:**

```yaml
# .GitHub/workflows/deploy.yml
name: Deploy to Railway

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'yarn'

      - name: Install dependencies
        run: yarn install --frozen-lockfile

      - name: Run tests
        run: yarn test:coverage

      - name: Type checking
        run: yarn typecheck

      - name: Lint check
        run: yarn lint

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: GitHub.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Railway
        uses: railway-app/railway-action@v1
        with:
          API-token: ${{ secrets.RAILWAY_TOKEN }}
          service: monkey-coder-API
```

### Infrastructure as Code

**Railway Configuration:**

> **Note**: This project uses `railpack.json` for deployment configuration. Railway automatically handles containerization without requiring a Dockerfile.

```json
{
  "name": "monkey-coder-api",
  "source": {
    "type": "GitHub", 
    "repo": "GaryOcean428/monkey-coder",
    "branch": "main"
  },
  "build": {
    "builder": "railpack"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3,
    "healthCheckPath": "/health",
    "healthCheckTimeout": 300
  },
  "networking": {
    "serviceDomain": "monkey-coder-api.railway.app"
  },
  "scaling": {
    "minReplicas": 1,
    "maxReplicas": 10,
    "targetCPUUtilization": 70
  }
}
```

### Monitoring and Observability

**Sentry Integration:**

```python
# packages/core/monkey_coder/monitoring/sentry_config.py
import sentry_sdk
from sentry_sdk.integrations FastAPI import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

def setup_sentry(dsn: str, environment: str):
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        integrations=[
            FastApiIntegration(auto_enabling=True),
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)
        ],
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
        attach_stacktrace=True,
        send_default_pii=False
    )
```

**Health Check Implementation:**

```python
# Health monitoring with detailed component status
@app.get("/v1/health")
async def health_check():
    """Comprehensive health check with component status"""
    components = {
        "database": await check_database_connection(),
        "Redis": await check_redis_connection(),
        "ai_providers": await check_ai_provider_availability(),
        "memory_usage": get_memory_usage(),
        "cpu_usage": get_cpu_usage()
    }

    all_healthy = all(components.values())
    status_code = 200 if all_healthy else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "components": components,
            "version": "1.0.4"
        }
    )
