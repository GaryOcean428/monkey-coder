# Step 6: Containerized Sandbox & Tool Access

This implementation provides a secure, containerized sandbox environment for code execution and browser automation using E2B and BrowserBase integrations.

## Features Implemented

### ✅ 1. E2B/BrowserBase Sandbox Integration

**E2B Code Execution:**
- Secure Python code execution in isolated environments
- Jupyter notebook-style execution with result capture
- Common package pre-installation (numpy, pandas, etc.)
- Resource monitoring and cleanup
- Timeout and error handling

**BrowserBase Browser Automation:**
- Playwright-based browser automation
- Screenshot capture and page interaction
- Link extraction and text content parsing
- Element waiting and clicking
- Session management with cleanup

### ✅ 2. Secure Volume Mounts & Network Limits

**Security Measures:**
- Non-root user execution (sandbox:1001)
- Resource limits: 512MB RAM, 50% CPU, 1GB disk
- Network allowlisting for external APIs only
- Process and file descriptor limits
- Secure token-based authentication

**Volume Management:**
- `/sandbox/volumes/workspace` (1GB) - Execution workspace
- `/sandbox/volumes/temp` (512MB) - Temporary files  
- `/sandbox/volumes/logs` (256MB) - Execution logs
- Proper permissions and cleanup

### ✅ 3. Dockerfiles

**Core Dockerfile (`Dockerfile`):**
- Slim Python 3.11 base image
- Dynamic PORT environment variable support
- Health checks and non-root execution
- Production-ready with security hardening

**Sandbox Dockerfile (`services/sandbox/Dockerfile`):**
- Multi-process management with Supervisor
- E2B and BrowserBase SDK integration
- Chromium browser with Xvfb for headless operation
- Security constraints and resource limits

### ✅ 4. Railway/Railpack Template

**Configuration (`railpack.json`):**
- Multi-service deployment (core + sandbox)
- Environment variable management
- Resource allocation and scaling
- Health checks and monitoring
- Volume mounts for persistent storage
- Security headers and network policies

**Key Features:**
- Respects "no railway.toml if railpack.json" rule
- Proper service networking and discovery
- PostgreSQL and Redis database integration
- External API allowlisting

## Architecture

```
┌─────────────────┐    ┌─────────────────┐
│  Core Service   │───▶│ Sandbox Service │
│   Port: 8000    │    │   Port: 8001    │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │  E2B + Browser  │
│     Redis       │    │   Integration   │
└─────────────────┘    └─────────────────┘
```

## API Endpoints

### Core Service (Port 8000)
- `GET /health` - Service health check
- `POST /v1/execute` - Main task execution endpoint
- `GET /v1/billing/usage` - Usage and billing metrics
- `GET /v1/providers` - Available AI providers
- `GET /v1/models` - Available AI models

### Sandbox Service (Port 8001)
- `GET /sandbox/health` - Sandbox health check
- `POST /sandbox/execute` - Execute sandbox tasks
- `GET /sandbox/metrics` - Performance metrics
- `POST /sandbox/cleanup` - Resource cleanup

## Security Implementation

### Authentication & Authorization
```python
# Token-based authentication
from services.sandbox.sandbox.security import generate_sandbox_token

token = generate_sandbox_token("execution-id", expires_in=3600)
headers = {"Authorization": f"Bearer {token}"}
```

### Resource Monitoring
```python
# Resource limits enforcement
from services.sandbox.sandbox.security import enforce_resource_limits

await enforce_resource_limits()  # Raises HTTPException if exceeded
```

### URL/Code Validation
```python
# Security validation
security_manager = SecurityManager()
if not security_manager.validate_url(url):
    raise HTTPException(status_code=400, detail="Invalid URL")
if not security_manager.validate_code(code):
    raise HTTPException(status_code=400, detail="Dangerous code detected")
```

## Usage Examples

### Code Execution
```python
from packages.core.monkey_coder.sandbox_client import SandboxClient

client = SandboxClient()
result = await client.execute_code(
    code="import numpy as np\nprint(np.array([1, 2, 3]))",
    execution_id="unique-id",
    timeout=30
)
```

### Browser Automation
```python
result = await client.execute_browser_action(
    url="https://example.com",
    action="screenshot",
    execution_id="unique-id",
    timeout=30
)
```

## Deployment

### Local Development
```bash
# Copy environment template
cp .env.example .env

# Start with Docker Compose
docker-compose up -d

# Or with monitoring
docker-compose --profile monitoring up -d
```

### Railway Deployment
```bash
# Deploy using railpack.json
railway up

# Or deploy specific service
railway up --service core
railway up --service sandbox
```

### Environment Variables
```bash
# Required
OPENAI_API_KEY=sk-...
SANDBOX_TOKEN_SECRET=secure-random-secret

# Optional (for sandbox features)
E2B_API_KEY=e2b_...
BROWSERBASE_API_KEY=bb_...
BROWSERBASE_PROJECT_ID=proj_...
```

## Monitoring & Observability

### Prometheus Metrics
- `sandbox_executions_total` - Total executions by type/status
- `sandbox_execution_duration_seconds` - Execution duration histogram
- `sandbox_memory_usage_bytes` - Current memory usage
- `sandbox_cpu_usage_percent` - Current CPU usage
- `sandbox_active_sessions` - Active sessions by type

### Health Checks
- Service availability monitoring
- Resource usage tracking
- Dependency health verification
- Execution timeout detection

### Logging
- Structured JSON logging with execution tracing
- Security event logging
- Error tracking and alerting
- Performance monitoring

## File Structure

```
├── Dockerfile                           # Core service container
├── docker-compose.yml                   # Local development setup
├── railpack.json                        # Railway deployment config
├── .env.example                         # Environment template
├── services/sandbox/
│   ├── Dockerfile                       # Sandbox service container
│   ├── requirements.txt                 # Python dependencies
│   ├── supervisord.conf                 # Process management
│   └── sandbox/
│       ├── main.py                      # FastAPI application
│       ├── e2b_integration.py           # E2B sandbox manager
│       ├── browserbase_integration.py   # BrowserBase manager
│       ├── security.py                  # Security controls
│       └── monitoring.py                # Metrics collection
├── packages/core/monkey_coder/
│   └── sandbox_client.py                # Core-to-sandbox client
└── docs/
    └── SANDBOX_ARCHITECTURE.md          # Detailed documentation
```

## Security Considerations

### Container Security
- Non-privileged containers
- Read-only root filesystem where possible
- Capability dropping (no-new-privileges)
- Resource limits enforcement
- Network isolation and allowlisting

### Data Protection
- No persistent sensitive data storage
- Secure token-based authentication
- Input validation and sanitization
- Execution timeout enforcement
- Automatic resource cleanup

### Network Security
- Allowlisted external domains only
- Internal service communication over Docker network
- TLS termination at load balancer
- Rate limiting and DDoS protection

## Testing

### Unit Tests
```bash
# Test sandbox components
pytest services/sandbox/tests/

# Test core integration
pytest packages/core/tests/
```

### Integration Tests
```bash
# Full system test
docker-compose exec core python -m pytest tests/integration/

# Sandbox service test
curl -X POST http://localhost:8001/sandbox/execute \
  -H "Authorization: Bearer $(generate-token)" \
  -H "Content-Type: application/json" \
  -d '{"sandbox_type":"code","action":"execute","code":"print(\"Hello World\")"}'
```

## Troubleshooting

### Common Issues
1. **E2B API Key**: Ensure valid API key is configured
2. **BrowserBase Setup**: Verify project ID and credentials
3. **Resource Limits**: Check memory/CPU usage in logs
4. **Network Access**: Verify allowlisted domains
5. **Docker Issues**: Check container logs and resource allocation

### Debug Commands
```bash
# Check service logs
docker-compose logs -f sandbox

# Monitor resources
docker stats

# Health check
curl http://localhost:8000/health
curl http://localhost:8001/sandbox/health

# Execute into container
docker-compose exec sandbox /bin/bash
```

## Next Steps

This implementation provides a solid foundation for secure containerized sandboxing. Future enhancements could include:

1. **WebAssembly (WASM) Support** - Language-agnostic execution
2. **GPU Acceleration** - For ML/AI workloads
3. **Kubernetes Deployment** - For production scalability  
4. **Custom Container Images** - User-defined environments
5. **Advanced Security Policies** - Fine-grained access controls

The sandbox system is now ready for integration with the broader Monkey Coder ecosystem and can be extended to support additional execution environments and automation tools.
