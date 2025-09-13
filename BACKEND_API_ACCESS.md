# Direct Backend API Access Guide

This guide explains how to access the Monkey Coder backend API directly for integration into other projects.

## API Endpoints

The Monkey Coder backend provides several REST API endpoints:

### Authentication
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/status` - Check authentication status
- `POST /api/v1/auth/keys/dev` - Create development API key (no auth required)
- `GET /api/v1/auth/keys` - List API keys (requires auth)

### Core Functionality
- `POST /api/v1/execute` - Execute AI tasks (code generation, analysis, etc.)
- `GET /api/v1/billing/usage` - Get usage statistics
- `GET /api/v1/providers` - List available AI providers
- `GET /api/v1/models` - List available AI models
- `GET /api/v1/capabilities` - Get system capabilities

### Health & Monitoring
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

## Quick Start for API Access

### 1. Get an API Key

For development/testing, you can create a temporary API key:

```bash
curl -X POST http://localhost:8000/api/v1/auth/keys/dev
```

Response:
```json
{
  "key": "mk-YOUR_API_KEY",
  "key_id": "key_12345",
  "name": "Development Key",
  "status": "active",
  "permissions": ["*"]
}
```

### 2. Test Authentication

```bash
curl -H "Authorization: Bearer mk-YOUR_API_KEY" \
     http://localhost:8000/api/v1/auth/status
```

### 3. Execute AI Tasks

```bash
curl -X POST \
  -H "Authorization: Bearer mk-YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "unique-task-id",
    "task_type": "code_generation",
    "prompt": "Create a Python function to calculate fibonacci numbers",
    "context": {
      "user_id": "api-user",
      "session_id": "session-123",
      "environment": "api"
    },
    "persona_config": {
      "persona": "developer"
    }
  }' \
  http://localhost:8000/api/v1/execute
```

## Configuration

### Environment Variables

Configure the backend with these environment variables:

```bash
# API Configuration
PORT=8000
HOST=0.0.0.0

# AI Provider API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Database (optional)
DATABASE_URL=postgresql://user:pass@localhost/monkeycoder

# Security
JWT_SECRET_KEY=your_jwt_secret

# CORS (for web integration)
CORS_ORIGINS=http://localhost:3000,https://your-frontend.com
```

### Docker Deployment

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY packages/core/ .
EXPOSE 8000

CMD ["python", "-m", "monkey_coder.app.main"]
```

### Railway/Cloud Deployment

The backend is ready for cloud deployment. Use `railpack.json` for Railway:

```json
{
  "provider": "python",
  "packages": {
    "python": "3.13"
  },
  "deploy": {
    "startCommand": "python -m monkey_coder.app.main"
  }
}
```

## Programming Language Examples

### Python Client

```python
import requests
import json

class MonkeyCoderClient:
    def __init__(self, base_url="http://localhost:8000", api_key=None):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}" if api_key else ""
        }
    
    def execute_task(self, prompt, task_type="code_generation"):
        data = {
            "task_id": f"task-{hash(prompt)}",
            "task_type": task_type,
            "prompt": prompt,
            "context": {
                "user_id": "api-user",
                "session_id": "session-1",
                "environment": "python-client"
            },
            "persona_config": {
                "persona": "developer"
            }
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/execute",
            headers=self.headers,
            json=data
        )
        return response.json()

# Usage
client = MonkeyCoderClient(api_key="mk-YOUR_API_KEY")
result = client.execute_task("Create a REST API endpoint")
print(result)
```

### JavaScript/Node.js Client

```javascript
class MonkeyCoderClient {
    constructor(baseUrl = 'http://localhost:8000', apiKey = null) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }

    async executeTask(prompt, taskType = 'code_generation') {
        const data = {
            task_id: `task-${Date.now()}`,
            task_type: taskType,
            prompt: prompt,
            context: {
                user_id: 'api-user',
                session_id: 'session-1',
                environment: 'nodejs-client'
            },
            persona_config: {
                persona: 'developer'
            }
        };

        const response = await fetch(`${this.baseUrl}/api/v1/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.apiKey}`
            },
            body: JSON.stringify(data)
        });

        return await response.json();
    }
}

// Usage
const client = new MonkeyCoderClient('http://localhost:8000', 'mk-YOUR_API_KEY');
client.executeTask('Create a React component').then(console.log);
```

### cURL Examples

#### Generate Code
```bash
curl -X POST \
  -H "Authorization: Bearer mk-YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"task_type":"code_generation","prompt":"Create a Python class for handling API requests","persona_config":{"persona":"developer"}}' \
  http://localhost:8000/api/v1/execute
```

#### Analyze Code
```bash
curl -X POST \
  -H "Authorization: Bearer mk-YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"task_type":"code_analysis","prompt":"Review this code for security issues","files":[{"name":"app.py","content":"# your code here"}],"persona_config":{"persona":"reviewer"}}' \
  http://localhost:8000/api/v1/execute
```

## Rate Limiting and Usage

- API keys have usage tracking and rate limiting
- Development keys have generous limits for testing
- Production usage requires a subscription plan
- Usage statistics are available via `/api/v1/billing/usage`

## Security

- Always use HTTPS in production
- Store API keys securely (environment variables, not in code)
- API keys have configurable permissions
- Authentication is required for all core endpoints

## Support

For backend integration support:
- Documentation: https://coder.fastmonkey.au/docs
- GitHub Issues: https://github.com/GaryOcean428/monkey-coder/issues
- API Reference: http://localhost:8000/api/docs (when backend is running)