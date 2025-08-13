[← Back to Roadmap Index](./index.md)

## API Documentation Standards

### OpenAPI Specification

**Base API Structure:**

```yaml
openapi: 3.0.3
info:
  title: Monkey Coder API
  version: 1.0.4
  description: Advanced AI-powered development platform
servers:
  - url: https://api.monkey-coder.com/v1
    description: Production server
  - url: http://localhost:8000/v1
    description: Development server
```

**Authentication Schema:**

```yaml
components:
  securitySchemes:
    BearerAuth:
      type: HTTP
      scheme: bearer
      bearerFormat: JWT
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
```

**Standard Response Format:**

```json
{
  "success": true,
  "data": {},
  "metadata": {
    "timestamp": "2025-01-31T21:00:00Z",
    "request_id": "req_123456789",
    "processing_time_ms": 150,
    "model_used": "gpt-4.1",
    "tokens_consumed": 245
  },
  "errors": []
}
```

### Endpoint Specifications

**Core Endpoints:**

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---------------|
| `/v1/execute` | POST | Execute AI development tasks | ✅ |
| `/v1/capabilities` | GET | System capabilities and status | ❌ |
| `/v1/health` | GET | Health check endpoint | ❌ |
| `/v1/auth/login` | POST | User authentication | ❌ |
| `/v1/auth/refresh` | POST | Token refresh | ✅ |
| `/v1/models` | GET | Available AI models | ✅ |
| `/v1/usage` | GET | User usage statistics | ✅ |

**Request/Response Examples:**

```json
// POST /v1/execute
{
  "prompt": "Build a REST API with user authentication",
  "persona": "developer",
  "task_type": "code_generation",
  "context": {
    "language": "Python",
    "framework": "FastAPI",
    "requirements": ["JWT auth", "PostgreSQL", "Docker"]
  },
  "options": {
    "model_preference": "gpt-4.1",
    "max_tokens": 4000,
    "temperature": 0.3
  }
}
