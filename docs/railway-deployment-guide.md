# Railway Deployment Optimization Guide

This document describes the Railway deployment optimizations implemented for the monkey-coder project.

## Overview

The Railway deployment has been optimized with:
- JSON structured logging for better log processing
- Performance monitoring for external API calls
- Enhanced health checks for Railway's infrastructure
- Proper dependency management

## JSON Logging

### Features
- **Structured Output**: All logs are in JSON format for better parsing
- **Railway Integration**: Includes service and environment fields
- **Performance Metrics**: Tracks memory usage, CPU, and request timing
- **API Monitoring**: Monitors external calls to OpenAI, Anthropic, etc.

### Configuration
Set these environment variables in Railway:

```bash
LOG_LEVEL=INFO
JSON_LOGS=true
PERFORMANCE_LOGS=true
```

### Sample Log Output
```json
{
  "timestamp": "2025-07-28T15:41:02.927446Z",
  "level": "INFO",
  "logger": "app_performance",
  "message": "Request processed",
  "module": "main",
  "function": "metrics_middleware",
  "line": 148,
  "metric_type": "http_request",
  "method": "GET",
  "path": "/health",
  "status_code": 200,
  "duration_ms": 1.31,
  "user_agent": "curl/8.5.0",
  "service": "monkey-coder",
  "environment": "production"
}
```

## Health Check Endpoint

The `/health` endpoint provides comprehensive status information:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-07-28T15:41:02.927512",
  "components": {
    "orchestrator": "active",
    "quantum_executor": "active",
    "persona_router": "active",
    "provider_registry": "active"
  }
}
```

Additional performance metrics are logged for each health check:
- Memory usage in MB
- CPU percentage
- Component status
- Qwen agent availability

## Railway Configuration

The `railpack.json` has been optimized for Railway:

```json
{
  "healthcheck": {
    "path": "/health",
    "timeout": 100
  },
  "environments": {
    "production": {
      "env": {
        "LOG_LEVEL": "INFO",
        "JSON_LOGS": "true",
        "PERFORMANCE_LOGS": "true"
      }
    }
  }
}
```

## Performance Monitoring

### API Call Monitoring
External API calls are automatically monitored with the `@monitor_api_calls` decorator:

```python
@monitor_api_calls("openai_connection_test")
async def _test_connection(self) -> None:
    # API call implementation
```

This tracks:
- Function name and duration
- Success/failure status
- Error details if applicable
- Argument counts for debugging

### HTTP Request Metrics
Every HTTP request is tracked with:
- Request method and path
- Response status code
- Processing duration in milliseconds
- User agent information
- Memory and CPU usage

## Dependency Resolution

### Fixed Issues
1. **safetensors version conflict**: Updated from `==0.4.8` to `>=0.4.3`
2. **transformers/tokenizers compatibility**: Used compatible version ranges
3. **qwen-agent missing dependency**: Added `python-dotenv` requirement
4. **qwen-agent import error**: Fixed import to use `Agent as QwenAgent`

### Required Dependencies
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
qwen-agent>=0.0.10
python-dotenv>=1.0.0
sentry-sdk[fastapi]>=1.40.0
psutil>=5.9.0
prometheus-client>=0.19.0
```

## Deployment Process

1. **Install dependencies**: Railway automatically installs from requirements.txt
2. **Start command**: `python -m monkey_coder.app.main`
3. **Health check**: Railway monitors `/health` endpoint
4. **Logging**: JSON logs are automatically collected by Railway
5. **Monitoring**: Performance metrics available in Railway dashboard

## Environment Variables

Required for production:
```bash
# API Keys (set in Railway dashboard)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
QWEN_API_KEY=your_qwen_key

# Logging Configuration
LOG_LEVEL=INFO
JSON_LOGS=true
PERFORMANCE_LOGS=true

# Railway Environment
RAILWAY_ENVIRONMENT=production
PORT=8000
```

## Troubleshooting

### Common Issues

1. **Qwen Agent Warning**: Ensure `python-dotenv` is installed
2. **JSON Logging Not Working**: Check `JSON_LOGS=true` environment variable
3. **Performance Metrics Missing**: Verify `PERFORMANCE_LOGS=true` is set
4. **Health Check Failing**: Check `/health` endpoint directly

### Log Analysis

Use Railway's log filters to analyze performance:
- Filter by `metric_type` for specific metric types
- Search for `duration_ms` to find slow requests
- Filter by `level: ERROR` for error analysis
- Use `service: monkey-coder` to isolate application logs

## Performance Optimization

### Memory Usage
- Typical memory usage: ~200MB
- Monitor via health check logs
- Scale up if consistently >80% of available memory

### API Response Times
- Monitor external API calls in logs
- Typical OpenAI calls: 500-2000ms
- Health checks: <5ms
- Consider caching for frequently used responses

### Request Processing
- Target <100ms for non-AI endpoints
- Health checks should be <10ms
- Use `X-Process-Time` header for client-side monitoring

## Future Improvements

1. **Database Monitoring**: Add PostgreSQL performance metrics
2. **Cache Monitoring**: Track Redis performance if added
3. **Custom Metrics**: Add business-specific metrics
4. **Alerting**: Set up Railway alerts for high error rates
5. **Log Aggregation**: Consider external log analysis tools for advanced querying