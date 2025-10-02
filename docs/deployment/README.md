# Deployment Configurations

This directory contains deployment configurations and templates for various platforms.

## Quick Links

- **[System Resource Limits](./SYSTEM_RESOURCE_LIMITS.md)** - ⚠️ CRITICAL: Configure before deploying
- **[Systemd Service Template](./systemd/monkey-coder.service)** - For Linux systems
- **[Docker Compose Configuration](./docker/docker-compose.resource-limits.yml)** - For containerized deployments
- **[Production Deployment Guide](../production-deployment-guide.md)** - Main deployment guide

## Overview

### System Resource Limits

The most common cause of production crashes is insufficient system resource limits. **Always** configure these before deploying:

| Resource | Minimum | Configuration |
|----------|---------|---------------|
| Open files | 65535 | `ulimit -n 65535` |
| Virtual memory | unlimited | `ulimit -v unlimited` |
| UV_THREADPOOL_SIZE | 64 | `export UV_THREADPOOL_SIZE=64` |

See [SYSTEM_RESOURCE_LIMITS.md](./SYSTEM_RESOURCE_LIMITS.md) for detailed guidance.

### Deployment Methods

#### 1. Railway (Recommended)

Railway provides good defaults, but ensure environment variables are set:

```bash
UV_THREADPOOL_SIZE=64
NODE_OPTIONS=--max-old-space-size=4096
```

See the main [Production Deployment Guide](../production-deployment-guide.md).

#### 2. Systemd (Linux Servers)

Use the provided service template:

```bash
sudo cp systemd/monkey-coder.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable monkey-coder
sudo systemctl start monkey-coder
```

See [monkey-coder.service](./systemd/monkey-coder.service) for details.

#### 3. Docker / Docker Compose

Use the resource limits configuration:

```bash
docker-compose -f docker-compose.yml \
  -f docs/deployment/docker/docker-compose.resource-limits.yml up
```

See [docker-compose.resource-limits.yml](./docker/docker-compose.resource-limits.yml) for details.

#### 4. Kubernetes

Apply resource limits in your deployment manifest:

```yaml
resources:
  requests:
    memory: "2Gi"
    cpu: "1000m"
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

See [SYSTEM_RESOURCE_LIMITS.md](./SYSTEM_RESOURCE_LIMITS.md) for K8s examples.

## Validation

### Automated Checks

The repository includes a GitHub Actions workflow that validates resource limits on every push:

- Workflow: `.github/workflows/preflight-limits.yml`
- Checks: open files ≥65535, virtual memory = unlimited
- Failure: Build fails with actionable error messages

### Runtime Checks

The application logs resource limits at startup:

```
[startup] System Resource Limits:
[startup]   open files      = 65536
[startup]   virtual memory  = unlimited
[startup]   threadpool size = 64
[startup] ✅ All resource limits are properly configured
```

### Manual Validation

```bash
# Check limits
ulimit -n  # Should be ≥65535
ulimit -v  # Should be unlimited
echo $UV_THREADPOOL_SIZE  # Should be 64

# Test with utilities
cd packages/cli && node -e "require('./dist/utils.js').logSystemLimits()"
cd packages/core && python3 -c "from monkey_coder.utils.system_limits import log_startup_limits; log_startup_limits()"
```

## Common Issues

### Too Many Open Files

**Symptoms:** `EMFILE`, socket errors, timeouts

**Fix:**
```bash
ulimit -n 65535  # Temporary
# For systemd: LimitNOFILE=65535
# For Docker: ulimits.nofile.soft: 65535
```

### Memory Allocation Failures

**Symptoms:** `Cannot allocate memory`, OOM despite available RAM

**Fix:**
```bash
ulimit -v unlimited  # Temporary
# For systemd: MemoryMax=infinity
# For Docker: deploy.resources.limits.memory: 4G
```

### Slow I/O Operations

**Symptoms:** Slow file/network operations

**Fix:**
```bash
export UV_THREADPOOL_SIZE=64
# For systemd: Environment="UV_THREADPOOL_SIZE=64"
# For Docker: environment: - UV_THREADPOOL_SIZE=64
```

## Support

For deployment issues:

1. Check [SYSTEM_RESOURCE_LIMITS.md](./SYSTEM_RESOURCE_LIMITS.md) troubleshooting section
2. Review application startup logs for warnings
3. Run preflight checks manually
4. Open an issue with logs and system information

## Contributing

When adding new deployment configurations:

1. Include resource limit settings
2. Add validation steps
3. Update this README
4. Test on the target platform
