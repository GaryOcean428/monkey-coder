# Monkey Coder API Documentation

## Production Deployment - Phase 2.0

**Version:** 2.0.0  
**Last Updated:** 2025-01-14  
**Status:** Production Ready

---

## Quick Start

### Base URL
- **Production:** `https://monkey-coder.up.railway.app`
- **Development:** `http://localhost:8000`

### Authentication
All API endpoints require authentication via API key in the `Authorization` header:

```bash
Authorization: Bearer your-api-key-here
```

### Rate Limiting
- **Standard:** 100 requests per minute
- **Burst:** 20 requests in quick succession
- **Headers:** Rate limit status returned in response headers

---

## Core Endpoints

### Health & Status

#### `GET /health`
Basic health check for load balancers and monitoring.

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0", 
  "timestamp": "2025-01-14T10:30:00Z",
  "components": {
    "orchestrator": "active",
    "quantum_executor": "active",
    "persona_router": "active",
    "provider_registry": "active"
  }
}
```

#### `GET /health/comprehensive`
Detailed health check with system metrics and component status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-14T10:30:00Z",
  "uptime_seconds": 3600,
  "version": "2.0.0",
  "environment": "production",
  "checks": {
    "system": {
      "status": "healthy",
      "memory_usage_percent": 45.2,
      "cpu_usage_percent": 23.1,
      "disk_usage_percent": 67.8
    },
    "database": {
      "status": "healthy",
      "url_configured": true,
      "pool_size": 10
    },
    "ai_providers": {
      "status": "healthy",
      "configured_providers": 3,
      "total_providers": 5
    }
  }
}
```

#### `GET /health/readiness`
Kubernetes-style readiness probe.

**Response:**
- `200 OK`: Application ready to receive traffic
- `503 Service Unavailable`: Still initializing

#### `GET /api/v1/production/validate`
Production readiness validation with comprehensive checks.

**Response:**
```json
{
  "ready": true,
  "warnings": [],
  "errors": [],
  "recommendations": [
    "Monitor error rates and response times after deployment",
    "Set up alerting for health check failures"
  ],
  "runtime_checks": {
    "components_initialized": true,
    "metrics_enabled": true,
    "security_headers_active": true,
    "performance_monitoring_active": true
  },
  "overall_ready": true
}
```

### Monitoring & Metrics

#### `GET /metrics`
Prometheus metrics in text format for scraping.

**Response:** Text format metrics for Prometheus

#### `GET /metrics/performance`
Detailed performance metrics for dashboards.

**Response:**
```json
{
  "performance": {
    "recent_requests": 100,
    "avg_response_time": 0.234,
    "min_response_time": 0.045,
    "max_response_time": 1.234,
    "slow_requests_count": 3,
    "error_rate_percent": 1.2
  },
  "cache": {
    "size": 145,
    "max_size": 1000,
    "hit_rate_percent": 78.5,
    "total_hits": 1234,
    "total_misses": 334
  },
  "timestamp": "2025-01-14T10:30:00Z"
}
```

#### `GET /metrics/cache`
Cache statistics for performance monitoring.

**Response:**
```json
{
  "size": 145,
  "max_size": 1000,
  "hit_rate_percent": 78.5,
  "total_hits": 1234,
  "total_misses": 334,
  "evictions": 12,
  "expired_removals": 45
}
```

---

## AI Execution Endpoints

### `POST /api/v1/execute`
Execute AI tasks with quantum routing and multi-agent orchestration.

**Request:**
```json
{
  "task": "Implement a REST API endpoint for user authentication",
  "persona": "developer",
  "provider": "openai",
  "stream": false,
  "files": [
    {
      "path": "app.py",
      "content": "# Existing application code"
    }
  ],
  "context": {
    "project_type": "flask",
    "requirements": ["security", "JWT tokens"]
  }
}
```

**Response:**
```json
{
  "task_id": "task_123456789",
  "status": "completed",
  "result": {
    "code": "# Generated authentication endpoint code",
    "explanation": "Implementation details and usage instructions",
    "files_modified": ["app.py", "auth.py"],
    "tests": "# Generated test code"
  },
  "metadata": {
    "execution_time": 2.34,
    "provider_used": "openai",
    "model": "gpt-4",
    "tokens_used": 1234,
    "quantum_branches": 3
  }
}
```

### `POST /api/v1/stream/execute`
Streaming execution with Server-Sent Events (SSE).

**Request:** Same as `/api/v1/execute` with `"stream": true`

**Response:** SSE stream with events:
```text
data: {"type": "start", "task_id": "task_123"}

data: {"type": "progress", "message": "Analyzing requirements..."}

data: {"type": "code", "content": "def authenticate_user():"}

data: {"type": "complete", "result": {...}}
```

---

## Authentication Endpoints

### `POST /api/v1/auth/login`
User login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "expires_at": "2025-01-14T11:00:00Z"
}
```

### `POST /api/v1/auth/refresh`
Refresh access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:** Same as login response with new tokens

---

## Error Handling

### Standard Error Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "persona",
      "reason": "Must be one of: developer, reviewer, architect, tester"
    }
  },
  "timestamp": "2025-01-14T10:30:00Z",
  "request_id": "req_123456789"
}
```

### HTTP Status Codes
- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

---

## Rate Limiting

### Headers
All responses include rate limiting headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 85
X-RateLimit-Reset: 1642157400
```

### Limits
- **Standard Users:** 100 requests/minute, 20 burst
- **Premium Users:** 500 requests/minute, 50 burst
- **Enterprise:** Custom limits

---

## Performance & Caching

### Response Times
- **Target:** \<2 seconds for 95% of requests
- **Monitoring:** Available at `/metrics/performance`
- **Cache:** Intelligent caching for repeated requests

### Performance Headers
All responses include performance timing:
```http
X-Process-Time: 0.234
X-Cache-Status: HIT|MISS
```

---

## Security

### HTTPS Only
All production traffic must use HTTPS. HTTP requests are redirected to HTTPS.

### Security Headers
Standard security headers included:
- `Strict-Transport-Security`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`

### API Key Security
- Store API keys securely
- Use HTTPS for all requests
- Rotate keys regularly
- Monitor for unauthorized usage

---

## Production Environment

### Infrastructure
- **Platform:** Railway
- **Runtime:** Python 3.12.11 with FastAPI
- **Database:** PostgreSQL with connection pooling
- **Monitoring:** Sentry error tracking + custom metrics
- **Caching:** High-performance in-memory cache

### Scaling
- **Horizontal:** Auto-scaling based on CPU/memory
- **Vertical:** Automatic resource allocation
- **Geographic:** Global CDN for static assets

### Monitoring
- **Health Checks:** Multiple endpoint types
- **Metrics:** Prometheus-compatible metrics
- **Alerting:** Automated alerts for issues
- **Logging:** Structured JSON logging

---

## Support & Troubleshooting

### Getting Help
- **Documentation:** [Full documentation site]
- **API Status:** `/health/comprehensive`
- **Support:** [Contact information]

### Common Issues
1. **Authentication Errors:** Check API key format and permissions
2. **Rate Limiting:** Implement exponential backoff
3. **Timeout Errors:** Increase request timeout or use streaming
4. **Performance:** Monitor cache hit rates and optimize requests

### Debug Information
Include these details when reporting issues:
- Request ID from error response
- Timestamp of the issue
- Request/response payload (without sensitive data)
- API key prefix (first 8 characters)

---

## Changelog

### Version 2.0.0 (2025-01-14)
- ✅ Production deployment ready
- ✅ Enhanced health checks and monitoring
- ✅ Performance optimization and caching
- ✅ Security hardening
- ✅ Comprehensive documentation

### Version 1.0.0 (Previous)
- Basic API functionality
- Core AI execution
- Authentication system
