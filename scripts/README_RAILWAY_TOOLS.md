# MCP Railway Deployment Tools

This directory contains comprehensive Railway deployment tools that integrate with the Model Context Protocol (MCP) framework to provide automated validation, fixing, and monitoring of Railway deployments.

## Tools Overview

### 1. MCP Railway Deployment Manager (`mcp-railway-deployment-manager.py`)
**Primary Tool**: Comprehensive Railway deployment validation with MCP integration

**Features:**
- ✅ Build system conflict detection (Issue 1)
- ✅ PORT binding validation (Issue 2)
- ✅ Health check configuration (Issue 5)
- ✅ Reference variable validation (Issue 4)
- ✅ Monorepo structure validation (Issue 6)
- 🔌 MCP orchestration integration
- 📊 Detailed reporting and recommendations

**Usage:**
```bash
python scripts/mcp-railway-deployment-manager.py
python scripts/mcp-railway-deployment-manager.py --verbose
python scripts/mcp-railway-deployment-manager.py --fix
```

### 2. Railway Auto-Fix Script (`railway-auto-fix.sh`)
**Purpose**: Automatically fixes common Railway deployment issues

**Features:**
- 🔧 Removes competing build files
- ✅ Validates railpack.json structure  
- ⚙️ Configures health checks
- 🔍 Creates deployment readiness scripts
- 📝 Updates git hooks for validation

**Usage:**
```bash
./scripts/railway-auto-fix.sh
```

### 3. Railway Deployment Integration (`railway-deployment-integration.sh`)
**Purpose**: Comprehensive deployment suite orchestrating all tools

**Features:**
- 🔍 Tool availability checking
- 🚀 Automated validation pipeline
- 🔧 Auto-fix integration
- 📋 Deployment summary generation
- 📊 Comprehensive logging

**Usage:**
```bash
./scripts/railway-deployment-integration.sh
```

### 4. MCP Railway Tool (`packages/core/monkey_coder/mcp/railway_deployment_tool.py`)
**Purpose**: MCP framework integration for Railway deployment management

**Features:**
- 🔌 MCP protocol integration
- 🎯 Tool definition for MCP servers
- 🤖 Orchestration coordination
- 📡 Real-time monitoring capabilities

## Railway Deployment Cheat Sheet Implementation

All tools implement the complete Railway Deployment Master Cheat Sheet:

### Issue 1: Build System Conflicts ✅
- Detects competing build files (Dockerfile, railway.toml, nixpacks.toml)
- Validates railpack.json syntax and structure
- Automatic backup and removal of competing files

### Issue 2: PORT Binding Failures ✅  
- Validates proper PORT environment variable usage
- Checks for 0.0.0.0 binding instead of localhost
- Detects hardcoded ports in application code

### Issue 3: Theme/CSS Loading Issues ⚠️
- Not directly applicable to backend Railway deployments
- Frontend build validation included in integration

### Issue 4: Reference Variable Mistakes ✅
- Validates Railway variable references
- Checks for invalid PORT references
- Recommends RAILWAY_PUBLIC_DOMAIN usage

### Issue 5: Health Check Configuration ✅
- Validates health endpoint implementation
- Configures railpack.json health check settings
- Tests health endpoint availability

### Issue 6: Monorepo Service Confusion ✅
- Detects monorepo structure
- Validates service configuration
- Provides monorepo-specific recommendations

## MCP Integration

The tools integrate with the MCP (Model Context Protocol) framework providing:

- **Orchestration**: Advanced coordination of deployment tasks
- **Environment Management**: Comprehensive environment validation
- **Real-time Monitoring**: Deployment health and performance tracking  
- **Automated Remediation**: Self-healing deployment capabilities

## Quick Start

1. **Run comprehensive validation:**
   ```bash
   ./scripts/railway-deployment-integration.sh
   ```

2. **Fix specific issues:**
   ```bash
   python scripts/mcp-railway-deployment-manager.py --fix
   ```

3. **Apply auto-fixes:**
   ```bash
   ./scripts/railway-auto-fix.sh
   ```

4. **Check deployment readiness:**
   ```bash
   ./check-railway-readiness.sh
   ```

## Validation Workflow

```
┌─────────────────────────────────────┐
│ Railway Deployment Integration      │
├─────────────────────────────────────┤
│ 1. Check Tool Availability         │
│ 2. Run MCP-Enhanced Validation      │
│ 3. Apply Auto-Fixes (if needed)     │
│ 4. Re-validate After Fixes         │
│ 5. Generate Deployment Summary      │
│ 6. Provide Next Steps              │
└─────────────────────────────────────┘
```

## Output Files

- `RAILWAY_DEPLOYMENT_SUMMARY.md` - Comprehensive deployment summary
- `railway_deployment_YYYYMMDD_HHMMSS.log` - Detailed execution log  
- `check-railway-readiness.sh` - Quick readiness check script
- `railway-deployment-fix.sh` - Auto-generated fix script (if issues found)

## Best Practices

1. **Always run validation before deployment**
2. **Use MCP tools for enhanced capabilities when available**
3. **Review generated summaries and logs**
4. **Keep tools updated with latest Railway best practices**
5. **Integrate with CI/CD pipelines for automated validation**

## Troubleshooting

### MCP Framework Not Available
If MCP tools show "running in standalone mode":
- Tools still function with core Railway validation
- Enhanced features unavailable but basic functionality works
- Consider installing MCP dependencies for full capabilities

### Validation Failures
- Review detailed logs in generated log files
- Use auto-fix tools for common issues
- Consult Railway documentation for complex problems
- Check Railway service status and quotas

### Permission Issues
Ensure all scripts are executable:
```bash
chmod +x scripts/*.sh
chmod +x *.sh
```

## Integration with CI/CD

Add Railway validation to your CI/CD pipeline:

```yaml
# Example GitHub Actions step
- name: Validate Railway Deployment
  run: |
    ./scripts/railway-deployment-integration.sh
    if [ $? -ne 0 ]; then
      echo "Railway deployment validation failed"
      exit 1
    fi
```

## Support

For issues with Railway deployment tools:
1. Check generated logs and summaries
2. Review Railway deployment documentation
3. Consult the Railway Deployment Master Cheat Sheet in `CLAUDE.md`
4. Use MCP orchestration features when available