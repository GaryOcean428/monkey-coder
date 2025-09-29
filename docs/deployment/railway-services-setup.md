# Railway MCP Services Setup

This directory contains comprehensive Railway deployment tools with MCP (Model Context Protocol) integration for the Monkey Coder platform.

## 🎯 Overview

The Railway MCP setup provides:
- **Automatic service provisioning** (PostgreSQL, Redis)
- **Environment variable management** with proper Railway references
- **Cross-service connectivity** and security configuration
- **Deployment validation** following Railway best practices
- **Monitoring and management tools**

## 🚀 Quick Start

### Option 1: Full Automated Setup (Recommended)

```bash
# Run the complete Railway deployment orchestrator
./scripts/railway-deployment-orchestrator.sh
```

This script will:
1. Validate your Railway CLI setup
2. Create required services (PostgreSQL, Redis)
3. Configure environment variables with proper Railway references
4. Generate security secrets
5. Create management scripts
6. Validate the complete deployment configuration

### Option 2: Python MCP Services Manager

```bash
# Run the Python-based services manager
python scripts/railway-services-setup.py
```

This provides:
- MCP framework integration
- Detailed service configuration
- JSON deployment reports
- Cross-referencing validation

## 📦 Services Created

### 1. PostgreSQL Database (`monkey-coder-postgres`)
- **Purpose**: User management, authentication, persistent data
- **Variables**: `DATABASE_URL` (automatically provided by Railway)
- **Usage**: User accounts, session storage, application data

### 2. Redis Cache (`monkey-coder-redis`)
- **Purpose**: Caching, session storage, message broker for Celery
- **Variables**: `REDIS_URL` (automatically provided by Railway)
- **Usage**: Cache layer, background task queue, real-time features

### 3. Main Application (`monkey-coder-api`)
- **Purpose**: FastAPI backend with Next.js frontend
- **Configuration**: Uses `railpack.json` for deployment
- **Features**: Health checks, proper Railway variable references

## ⚙️ Environment Variables Configured

### Railway References (Following Cheat Sheet Best Practices)
```bash
# ✅ CORRECT - Uses Railway domain references
CORS_ORIGINS=https://${{RAILWAY_PUBLIC_DOMAIN}}
NEXTAUTH_URL=https://${{RAILWAY_PUBLIC_DOMAIN}}
NEXT_PUBLIC_API_URL=https://${{RAILWAY_PUBLIC_DOMAIN}}
NEXT_PUBLIC_APP_URL=https://${{RAILWAY_PUBLIC_DOMAIN}}

# ✅ CORRECT - Railway provides these automatically
DATABASE_URL=${{DATABASE_URL}}
REDIS_URL=${{REDIS_URL}}
```

### Security Secrets (Auto-generated)
```bash
JWT_SECRET_KEY=<64-char-random-string>
NEXTAUTH_SECRET=<32-char-random-string>
SANDBOX_TOKEN_SECRET=<32-char-random-string>
```

### Application Configuration
```bash
NODE_ENV=production
PYTHON_ENV=production
LOG_LEVEL=info
HEALTH_CHECK_PATH=/health
HEALTH_CHECK_TIMEOUT=300
```

## 🔧 Management Scripts Created

### 1. `railway_api_keys_setup.sh`
Interactive script to set up all required API keys:
```bash
./railway_api_keys_setup.sh
```

Sets up:
- OpenAI API Key
- Anthropic API Key
- Google API Key
- Groq API Key
- Other optional service keys

### 2. `railway_monitor.sh`
Comprehensive monitoring and management:
```bash
# Check deployment status
./railway_monitor.sh status

# Follow deployment logs
./railway_monitor.sh logs

# List environment variables
./railway_monitor.sh vars

# Check application health
./railway_monitor.sh health https://your-domain.railway.app/health

# Deploy application
./railway_monitor.sh deploy

# Rollback deployment
./railway_monitor.sh rollback
```

## 🏥 Health Check Configuration

The setup configures proper health checking following Railway best practices:

### In `railpack.json`
```json
{
  "deploy": {
    "healthCheckPath": "/health",
    "healthCheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### Application Implementation
The `/health` endpoint should return:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-27T...",
  "services": {
    "database": "connected",
    "redis": "connected"
  }
}
```

## 🔍 Validation Checklist

The setup includes comprehensive validation following the Railway Cheat Sheet:

### ✅ Build System Conflicts (Issue 1)
- [x] Only `railpack.json` exists (no competing Dockerfile, railway.toml, etc.)
- [x] Valid JSON syntax in railpack.json
- [x] Proper build provider configuration

### ✅ PORT Binding (Issue 2)
- [x] Application uses `process.env.PORT` or `os.getenv("PORT")`
- [x] Server binds to `0.0.0.0` (not localhost)
- [x] No hardcoded ports in start commands

### ✅ Railway References (Issue 4)
- [x] Uses `${{RAILWAY_PUBLIC_DOMAIN}}` for public URLs
- [x] Uses `${{DATABASE_URL}}` and `${{REDIS_URL}}` for service connections
- [x] No invalid PORT references

### ✅ Health Check (Issue 5)
- [x] Health endpoint implemented at `/health`
- [x] Health check configured in railpack.json
- [x] Proper timeout and retry configuration

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. "Service already exists" Error
```bash
# Check existing services
railway status

# If needed, remove and recreate
railway remove <service-name>
```

#### 2. Environment Variables Not Working
```bash
# List current variables
railway variables

# Check for proper Railway references
railway variables | grep -i "railway"
```

#### 3. Health Check Failing
```bash
# Check logs
./railway_monitor.sh logs

# Test health endpoint locally
curl http://localhost:8000/health
```

#### 4. Database Connection Issues
```bash
# Verify DATABASE_URL is set
railway variables | grep DATABASE_URL

# Check database service status
railway status
```

## 📊 Monitoring and Logging

### Deployment Reports
Each setup run generates detailed reports:
- `railway_deployment_summary.json` (Python script)
- `railway_deployment_report_TIMESTAMP.json` (Bash script)
- `railway_deployment_TIMESTAMP.log` (Bash script)

### Real-time Monitoring
```bash
# Follow logs in real-time
railway logs --follow

# Check service health
railway ps

# Monitor resource usage
railway metrics
```

## 🔄 Deployment Workflow

### Complete Deployment Process

1. **Setup Services**:
   ```bash
   ./scripts/railway-deployment-orchestrator.sh
   ```

2. **Configure API Keys**:
   ```bash
   ./railway_api_keys_setup.sh
   ```

3. **Deploy Application**:
   ```bash
   railway deploy
   ```

4. **Monitor Deployment**:
   ```bash
   ./railway_monitor.sh status
   ./railway_monitor.sh health https://your-domain.railway.app/health
   ```

5. **Check Logs** (if needed):
   ```bash
   ./railway_monitor.sh logs
   ```

## 📚 Railway Best Practices Implemented

This setup implements all recommendations from the Railway Deployment Master Cheat Sheet:

### ✅ Issue 1: Build System Conflicts
- Uses only `railpack.json` for configuration
- Removes competing build files
- Validates JSON syntax

### ✅ Issue 2: PORT Binding Failures  
- Configures proper `process.env.PORT` usage
- Ensures `0.0.0.0` host binding
- No hardcoded ports

### ✅ Issue 3: Theme/CSS Loading
- Configures proper asset serving
- Sets up production build optimization

### ✅ Issue 4: Reference Variable Mistakes
- Uses `${{RAILWAY_PUBLIC_DOMAIN}}` for public URLs
- Proper service-to-service connectivity
- No invalid PORT references

### ✅ Issue 5: Health Check Configuration
- Implements `/health` endpoint
- Configures proper timeout values
- Sets up restart policies

### ✅ Issue 6: Monorepo Service Management
- Handles monorepo structure correctly
- Separate service configurations
- Proper workspace management

## 🌟 Advanced Features

### MCP Integration
The Python services manager includes MCP (Model Context Protocol) integration for:
- Enhanced orchestration patterns
- Intelligent service configuration
- Advanced monitoring capabilities

### Security Hardening
- Auto-generated secure secrets
- Proper CORS configuration
- Security headers setup
- Session management

### Production Optimization
- Build caching configuration
- Performance monitoring
- Error tracking setup
- Scalability preparation

---

## 💡 Next Steps After Setup

1. **Verify Deployment**: Check all services are running correctly
2. **Configure Monitoring**: Set up alerts and monitoring dashboards
3. **Test Functionality**: Run comprehensive application tests
4. **Scale Services**: Adjust resources based on usage patterns
5. **Set up Backup**: Configure database backup strategies

For more detailed Railway configuration, see:
- [Railway Documentation](https://docs.railway.app/)
- [Railway Best Practices](https://docs.railway.app/deploy/best-practices)
- [Railway Variables Guide](https://docs.railway.app/deploy/variables)