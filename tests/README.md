# Monkey Coder Smoke Test Suite

This directory contains comprehensive smoke tests for the Monkey Coder platform, designed to validate route accessibility, user flows, and cross-service integration.

## Overview

The smoke test suite covers four main areas:

1. **Backend API Tests** - FastAPI endpoint validation
2. **Frontend Route Tests** - Next.js route accessibility  
3. **CLI Tests** - Command-line interface functionality
4. **User Flow Integration Tests** - Cross-service workflows

## Test Files

### Core Test Scripts

- `smoke_test_backend.py` - Backend FastAPI endpoint tests
- `smoke_test_frontend.mjs` - Frontend Next.js route tests  
- `smoke_test_cli.mjs` - CLI command and functionality tests
- `user_flow_integration.mjs` - End-to-end user flow tests
- `run_smoke_tests.sh` - Comprehensive test runner (main entry point)

### Enhanced Existing Tests

- `../packages/web/__tests__/smoke.test.tsx` - Enhanced React component smoke tests

## Quick Start

### Run All Smoke Tests

```bash
# From the project root
./tests/run_smoke_tests.sh
```

### Run Individual Test Suites

```bash
# Backend API tests (requires backend running on localhost:8000)
cd tests && python3 smoke_test_backend.py

# Frontend route tests (requires frontend running on localhost:3000)  
cd tests && node smoke_test_frontend.mjs

# CLI tests (no services required)
cd tests && node smoke_test_cli.mjs

# Integration tests (requires both backend and frontend)
cd tests && node user_flow_integration.mjs
```

## Environment Configuration

### Environment Variables

- `BACKEND_URL` - Backend service URL (default: http://localhost:8000)
- `FRONTEND_URL` - Frontend service URL (default: http://localhost:3000)
- `BACKEND_PORT` - Backend port (default: 8000)
- `FRONTEND_PORT` - Frontend port (default: 3000)

### Example Usage

```bash
# Test against different endpoints
BACKEND_URL=https://api.monkey-coder.com FRONTEND_URL=https://monkey-coder.com ./tests/run_smoke_tests.sh

# Test with custom ports
BACKEND_PORT=8080 FRONTEND_PORT=3001 ./tests/run_smoke_tests.sh
```

## Test Categories

### Backend API Tests (`smoke_test_backend.py`)

Tests FastAPI endpoints including:

- **Health Endpoints**: `/health`, `/healthz`, `/health/comprehensive`, `/health/readiness`
- **Metrics Endpoints**: `/metrics`, `/metrics/performance`, `/metrics/cache`
- **API v1 Endpoints**: `/api/v1/cache/stats`, `/api/v1/providers`, `/api/v1/models`
- **Auth Endpoints**: Authentication flow validation (expects 401/422 for invalid requests)
- **Protected Endpoints**: Ensures proper authentication requirements

Expected Results:
- Health endpoints return 200 OK
- Public API endpoints accessible without authentication
- Protected endpoints return 401 without authentication
- Auth endpoints handle invalid requests gracefully

### Frontend Route Tests (`smoke_test_frontend.mjs`)

Tests Next.js application routes including:

- **Public Routes**: `/`, `/pricing`, `/contact`, `/terms`, `/privacy`, `/blog`, `/docs`
- **Auth Routes**: `/login`, `/signup`, `/forgot-password`
- **Protected Routes**: `/dashboard`, `/projects`, `/api-keys` (accepts 200 or 302)
- **Error Pages**: 404 handling
- **Static Assets**: `/favicon.ico`, `/robots.txt`
- **Health Endpoint**: `/api/health`

Expected Results:
- Public routes return 200 OK
- Auth routes accessible
- Protected routes redirect (302) or show content (200) based on auth state
- Error pages return appropriate status codes
- Static assets are accessible

### CLI Tests (`smoke_test_cli.mjs`)

Tests command-line interface including:

- **CLI Availability**: Yarn and CLI package accessibility
- **Core Commands**: `--help`, `--version`, `auth status`
- **Unauthenticated Commands**: Tests that commands requiring auth fail appropriately
- **Configuration**: Config command accessibility

Expected Results:
- CLI commands execute without errors
- Help and version information displayed
- Auth-required commands fail gracefully when not authenticated
- Configuration commands accessible

### User Flow Integration Tests (`user_flow_integration.mjs`)

Tests cross-service workflows including:

- **Health Sync**: Backend and frontend health endpoint coordination
- **Authentication Flow**: Complete auth workflow across services
- **Task Execution Flow**: End-to-end task processing workflow
- **API Discovery**: Service discoverability and documentation
- **Cross-Service Integration**: CORS, proxying, and service communication

Expected Results:
- Services communicate properly
- Authentication flows work end-to-end
- Protected resources properly secured
- API discovery endpoints functional
- Cross-service integration working

## Dependencies

### Python Dependencies

```bash
pip3 install httpx  # For backend API tests
```

### Node.js Dependencies

Uses Node.js built-in modules and node-fetch (should be available in the workspace).

## Test Results

### Console Output

Tests provide real-time colored console output showing:
- ✅ Passed tests with response times
- ❌ Failed tests with error details
- 📋 Summary statistics

### JSON Report

The comprehensive test runner generates `smoke_test_results.json` with:

```json
{
    "timestamp": "2024-01-15T10:30:00Z",
    "backend_url": "http://localhost:8000",
    "frontend_url": "http://localhost:3000", 
    "results": {
        "backend": true,
        "frontend": true,
        "cli": true,
        "integration": true
    },
    "summary": {
        "total_suites": 4,
        "passed_suites": 4,
        "success_rate": 100.0
    }
}
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Run Smoke Tests
  run: |
    # Start services in background
    yarn dev &
    python3 packages/core/dev_server.py &
    
    # Wait for services to be ready
    sleep 30
    
    # Run smoke tests
    ./tests/run_smoke_tests.sh
```

### Railway Deployment Validation

```bash
# Validate production deployment
BACKEND_URL=$RAILWAY_BACKEND_URL FRONTEND_URL=$RAILWAY_FRONTEND_URL ./tests/run_smoke_tests.sh
```

## Error Handling

The test suite gracefully handles:

- **Service Unavailability**: Skips tests for unavailable services with warnings
- **Network Timeouts**: 30-second timeouts with clear error messages
- **Authentication Failures**: Expected failures for protected resources
- **Build Dependencies**: Automatic building of CLI package if needed

## Performance Monitoring

Tests track and report:
- Response times for all endpoints
- Average response times per test suite
- Service availability and health

## Contributing

When adding new tests:

1. Follow existing naming conventions (`test_*` functions)
2. Include appropriate timeout handling
3. Provide clear success/failure criteria
4. Add documentation for new test categories
5. Update this README with new test descriptions

### Adding New Smoke Tests

```javascript
// Example: Add new endpoint test
async function testNewEndpoint() {
    const result = await this.test_endpoint('/api/v1/new-endpoint');
    const status = result.success ? '✅' : '❌';
    console.log(`  ${status} New endpoint - ${result.status_code} (${result.response_time:.3f}s)`);
}
```

## Troubleshooting

### Common Issues

1. **Service Not Running**: Ensure backend/frontend services are started
2. **Permission Denied**: Make sure test scripts are executable (`chmod +x`)
3. **Module Not Found**: Install required dependencies (httpx for Python)
4. **CLI Build Missing**: Run `yarn workspace monkey-coder-cli build` first

### Debug Mode

Run individual tests for detailed debugging:

```bash
# Enable verbose output
BACKEND_URL=http://localhost:8000 python3 -v smoke_test_backend.py
```

## License

These tests are part of the Monkey Coder project and follow the same MIT license.