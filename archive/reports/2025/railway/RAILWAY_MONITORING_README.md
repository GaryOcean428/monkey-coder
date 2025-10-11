# Railway Deployment Monitoring and Alerting System

This document describes the comprehensive Railway deployment monitoring and alerting system implemented for the monkey-coder platform.

## Overview

The Railway monitoring system provides real-time tracking of deployment health, automated rollback capabilities, frontend asset monitoring, and comprehensive alerting for deployment failures and performance issues.

## Features Implemented

### ✅ 1. Railway Deployment Tracking
- **Location**: `packages/core/monkey_coder/monitoring/railway_webhooks.py`
- **Endpoints**: `/api/v1/railway/webhook`, `/api/v1/railway/metrics`
- **Functionality**:
  - Tracks deployment success/failure rates
  - Monitors container startup times
  - Records deployment metrics and history
  - Email notifications for deployment events
  - Real-time alerting via email notifications

### ✅ 2. Health Check Monitoring Dashboard
- **Location**: `packages/core/monkey_coder/monitoring/health_dashboard.py`
- **Endpoints**: `/api/v1/railway/dashboard`, `/api/v1/railway/dashboard/data`
- **Functionality**:
  - Web-based health monitoring dashboard
  - Real-time component health tracking
  - Response time monitoring
  - Uptime percentage calculations
  - Auto-refreshing dashboard with 30-second intervals

### ✅ 3. Automated Rollback System
- **Location**: `packages/core/monkey_coder/monitoring/automated_rollback.py`
- **Endpoints**: `/api/v1/railway/rollback/*`
- **Functionality**:
  - Automatic rollback on startup failures
  - Crash loop detection and rollback
  - Manual rollback capabilities
  - Rollback history and statistics
  - Configurable failure thresholds

### ✅ 4. Frontend Asset Monitoring
- **Location**: `packages/core/monkey_coder/monitoring/frontend_assets.py`
- **Endpoints**: `/api/v1/railway/frontend/*`
- **Functionality**:
  - Frontend asset availability validation
  - Static file integrity checking
  - Asset response time monitoring
  - Dynamic asset discovery (webpack bundles)
  - Asset size and checksum verification

### ✅ 5. Path Verification in CI/CD
- **Location**: `scripts/railway_path_verification.sh`
- **Functionality**:
  - Virtual environment path validation
  - Python package installation verification
  - Application file existence checks
  - Startup command testing
  - Comprehensive diagnostic reporting

### ✅ 6. Comprehensive Monitoring Setup
- **Location**: `railway_monitoring_setup.sh`
- **Functionality**:
  - End-to-end monitoring system setup
  - Health check validation
  - API endpoint testing
  - Email configuration
  - Status badge generation

## API Endpoints

### Health Monitoring
- `GET /health` - Basic health check
- `GET /healthz` - Railway-compatible health check
- `GET /health/readiness` - Readiness probe
- `GET /health/comprehensive` - Detailed health status

### Railway Webhooks
- `POST /api/v1/railway/webhook` - Railway webhook handler
- `GET /api/v1/railway/metrics` - Deployment metrics
- `POST /api/v1/railway/health-check` - Health check callback

### Monitoring Dashboard
- `GET /api/v1/railway/dashboard` - HTML monitoring dashboard
- `GET /api/v1/railway/dashboard/data` - Dashboard data (JSON)
- `GET /api/v1/railway/dashboard/component/{name}/history` - Component history
- `POST /api/v1/railway/monitoring/start` - Start monitoring
- `POST /api/v1/railway/monitoring/stop` - Stop monitoring

### Automated Rollback
- `GET /api/v1/railway/rollback/status` - Rollback system status
- `POST /api/v1/railway/rollback/manual` - Manual rollback trigger
- `GET /api/v1/railway/rollback/history` - Rollback history
- `POST /api/v1/railway/rollback/configure` - Configure rollback settings

### Frontend Asset Monitoring
- `GET /api/v1/railway/frontend/status` - Frontend asset health
- `GET /api/v1/railway/frontend/assets` - Asset details
- `GET /api/v1/railway/frontend/verify` - Asset verification

## Configuration

### Environment Variables

```bash
# Required for email functionality
RESEND_API_KEY=your_resend_api_key
RAILWAY_TOKEN=your_railway_api_token
RAILWAY_PROJECT_ID=your_project_id
RAILWAY_SERVICE_ID=your_service_id

# Email configuration
NOTIFICATION_EMAIL_FROM=notifications@your-domain.com
ADMIN_NOTIFICATION_EMAILS=admin@your-domain.com,dev@your-domain.com
ENQUIRY_NOTIFICATION_EMAILS=support@your-domain.com
ROLLBACK_NOTIFICATION_EMAILS=devops@your-domain.com,admin@your-domain.com

# Deployment configuration
RAILWAY_DEPLOYMENT_URL=https://your-app.railway.app
FRONTEND_OUT_PATH=/app/packages/web/out

# Rollback configuration
RAILWAY_ROLLBACK_ENABLED=true
RAILWAY_STARTUP_TIMEOUT=300
RAILWAY_HEALTH_CHECK_TIMEOUT=30
RAILWAY_CRASH_THRESHOLD=3
RAILWAY_CRASH_WINDOW=600
```bash

### Monitoring Configuration

The monitoring system stores configuration in `data/monitoring_config.json`:

```json
{
    "deployment_url": "https://coder.fastmonkey.au",
    "email_notifications_configured": true,
    "health_check_timeout": 30,
    "startup_timeout": 300,
    "monitoring_enabled": true,
    "rollback_enabled": true,
    "frontend_monitoring_enabled": true,
    "alert_thresholds": {
        "consecutive_failures": 3,
        "response_time_threshold": 30,
        "crash_threshold": 3,
        "crash_window": 600
    }
}
```json

## Usage

### 1. Setup Monitoring System

```bash
# Run the comprehensive monitoring setup
./railway_monitoring_setup.sh

# With custom email notifications
RESEND_API_KEY=re_... ./railway_monitoring_setup.sh

# With custom deployment URL
./railway_monitoring_setup.sh --url https://my-app.railway.app
```bash

### 2. Path Verification

```bash
# Run path verification before deployment
./scripts/railway_path_verification.sh

# With custom paths
VENV_PATH=/custom/venv ./scripts/railway_path_verification.sh
```bash

### 3. Access Monitoring Dashboard

Visit `https://your-app.railway.app/api/v1/railway/dashboard` for the real-time monitoring dashboard.

### 4. Configure Webhooks

Set up Railway webhooks to point to your deployment's webhook endpoint:
- URL: `https://your-app.railway.app/api/v1/railway/webhook`
- Events: deployment status changes, service status changes

### 5. Manual Rollback

```bash
curl -X POST "https://your-app.railway.app/api/v1/railway/rollback/manual" \
  -H "Content-Type: application/json" \
  -d '{
    "current_deployment_id": "failed_deployment_id",
    "target_deployment_id": "stable_deployment_id",
    "reason": "manual_trigger"
  }'
```bash

## Success Criteria Achievement

- ✅ **Zero "No such file or directory" errors**: Path verification script prevents path-related deployment failures
- ✅ **Health checks pass within 30 seconds**: Configurable health check timeout with monitoring
- ✅ **Frontend assets accessible at root URL**: Frontend asset monitoring validates availability
- ✅ **API endpoints responsive at `/api/v1/health`**: Comprehensive health endpoint testing
- ✅ **Deployment success/failure tracking**: Webhook-based metrics collection
- ✅ **Container startup time monitoring**: Deployment timing analysis
- ✅ **Alert on health check failures**: Real-time webhook notifications
- ✅ **Automated rollback on startup failures**: Intelligent rollback system
- ✅ **Path verification in CI/CD**: Pre-deployment validation script

## Monitoring Dashboard Features

The web-based dashboard provides:
- Overall system health status
- Component-by-component health breakdown
- Response time metrics
- Uptime percentages
- Recent deployment history
- Auto-refresh every 30 seconds
- Mobile-responsive design

## Alerting and Notifications

The system sends email notifications for:
- Deployment failures
- Health check failures
- Crash loops detected
- Slow response times
- Frontend asset unavailability
- Successful deployments
- Rollback events

## Files Created/Modified

### New Files
- `packages/core/monkey_coder/monitoring/railway_webhooks.py`
- `packages/core/monkey_coder/monitoring/health_dashboard.py`
- `packages/core/monkey_coder/monitoring/automated_rollback.py`
- `packages/core/monkey_coder/monitoring/frontend_assets.py`
- `scripts/railway_path_verification.sh`
- `RAILWAY_MONITORING_README.md`

### Modified Files
- `packages/core/monkey_coder/app/main.py` - Added monitoring endpoints
- `railway_monitoring_setup.sh` - Enhanced with comprehensive monitoring

## Testing

```bash
# Test monitoring module imports
python -c "
import sys
sys.path.insert(0, 'packages/core')
from monkey_coder.monitoring.railway_webhooks import deployment_tracker
from monkey_coder.monitoring.health_dashboard import get_health_monitor
from monkey_coder.monitoring.automated_rollback import get_rollback_manager
from monkey_coder.monitoring.frontend_assets import get_frontend_monitor
print('✅ All monitoring modules imported successfully')
"

# Test path verification
./scripts/railway_path_verification.sh --help

# Test monitoring setup
./railway_monitoring_setup.sh --help
```bash

## Next Steps

1. **Deploy to Railway**: Apply the monitoring configuration to your Railway deployment
2. **Configure Webhooks**: Set up Railway webhooks to point to your monitoring endpoints
3. **Set Environment Variables**: Configure the required environment variables
4. **Test Alerting**: Verify webhook notifications are working
5. **Monitor and Tune**: Adjust thresholds based on your application's behavior

## Support

For issues or questions regarding the Railway monitoring system:
1. Check the monitoring dashboard at `/api/v1/railway/dashboard`
2. Review logs in the Railway console
3. Verify webhook configuration
4. Check environment variables are properly set
