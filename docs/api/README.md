# Monkey Coder Backend API

## Overview

The Monkey Coder backend provides a comprehensive FastAPI-based service for AI-powered code generation, analysis, and orchestration. This API is designed for both internal use by the Monkey Coder CLI and web interface, as well as external integration by third-party applications.

## Base URL

- **Production**: `https://monkey-coder-backend.railway.app`
- **Development**: `http://localhost:8000`

## Authentication

All API endpoints require authentication via JWT tokens. Obtain tokens through the authentication endpoints.

### Authentication Endpoints

```http
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
```

## Core API Endpoints

### Code Generation & Analysis

```http
POST /api/v1/execute
POST /api/v1/execute/stream
GET  /api/v1/tasks/{task_id}
```

### User Management

```http
GET  /api/v1/users/me
PUT  /api/v1/users/me
GET  /api/v1/users/usage
```

### Billing & Usage

```http
GET  /api/v1/billing/usage
GET  /api/v1/billing/plans
POST /api/v1/billing/subscribe
```

### Health & Monitoring

```http
GET  /health
GET  /api/v1/health/detailed
```

## External Integration Guide

### 1. Authentication Setup

```python
import requests

# Login to get JWT token
response = requests.post('https://monkey-coder-backend.railway.app/api/v1/auth/login', {
    'email': 'your-email@example.com',
    'password': 'your-password'
})
token = response.json()['access_token']

# Use token in subsequent requests
headers = {'Authorization': f'Bearer {token}'}
```

### 2. Code Generation

```python
# Generate code with AI
response = requests.post(
    'https://monkey-coder-backend.railway.app/api/v1/execute',
    headers=headers,
    json={
        'task_type': 'implement',
        'prompt': 'Create a React component for user authentication',
        'files': [],
        'context': {
            'persona': 'developer',
            'framework': 'react'
        }
    }
)
result = response.json()
```

### 3. Streaming Responses

```python
import sseclient

# Stream real-time responses
response = requests.post(
    'https://monkey-coder-backend.railway.app/api/v1/execute/stream',
    headers=headers,
    json={...},
    stream=True
)

client = sseclient.SSEClient(response)
for event in client.events():
    print(f"Progress: {event.data}")
```

## Rate Limits

- **Free Plan**: 100 requests/hour
- **Pro Plan**: 1000 requests/hour  
- **Enterprise**: Custom limits

## Error Handling

All errors follow standard HTTP status codes with detailed JSON responses:

```json
{
  "error": "validation_error",
  "message": "Invalid request parameters",
  "details": {...}
}
```

## SDK Integration

For easier integration, use the official SDKs:

```bash
# Python SDK
pip install monkey-coder-sdk

# Node.js SDK  
npm install monkey-coder-sdk
```

## Support

- **Documentation**: https://docs.monkey-coder.dev
- **API Reference**: https://api.monkey-coder.dev/docs
- **Support**: support@monkey-coder.dev
