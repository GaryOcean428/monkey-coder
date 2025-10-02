# System Resource Limits Configuration

This guide helps prevent production crashes caused by insufficient system resource limits (file descriptors, virtual memory, etc.).

## Why This Matters

Many "random" runtime crashes are caused by the OS rejecting resource requests when limits are too low. Common symptoms include:

- **Undici sporadic socket errors under load** - `ECONNRESET`, `ETIMEDOUT`
- **Headless browser/WASM "OOM" despite low app usage** - Blank pages, silent failures
- **Build passing but runtime failing** - Tests work, production crashes

## Quick Diagnosis

### Check Current Limits

```bash
# Check all limits
ulimit -a

# Check specific limits
ulimit -n  # Open files
ulimit -v  # Virtual memory
ulimit -u  # Max processes
```

### Recommended Minimum Values

| Limit | Recommended Value | Why |
|-------|------------------|-----|
| Open files (`-n`) | ≥65535 | HTTP clients (Undici), WASM modules, headless browsers |
| Virtual memory (`-v`) | unlimited | Prevents OOM in memory-intensive operations |
| Max processes (`-u`) | ≥4096 | Child process spawning |
| UV_THREADPOOL_SIZE | 64 | Node.js I/O performance (fs/crypto/dns) |

## Platform-Specific Configuration

### GitHub Actions (CI/CD)

The repository includes a preflight workflow that validates resource limits on every push/PR:

**.github/workflows/preflight-limits.yml** - Automatically checks and reports limit issues

To temporarily disable (not recommended):
```yaml
# In your workflow file
jobs:
  my-job:
    steps:
      - name: Set higher limits (if default check fails)
        run: |
          ulimit -n 65535
          ulimit -v unlimited
```

### Linux (systemd)

Use the provided service template:

```bash
# Copy the service file
sudo cp docs/deployment/systemd/monkey-coder.service /etc/systemd/system/

# Edit to match your installation paths
sudo nano /etc/systemd/system/monkey-coder.service

# Reload systemd and start
sudo systemctl daemon-reload
sudo systemctl enable monkey-coder
sudo systemctl start monkey-coder

# Verify limits
systemctl show monkey-coder -p LimitNOFILE
systemctl show monkey-coder -p MemoryMax
```

**Key settings in the service file:**
```ini
LimitNOFILE=65535
MemoryMax=infinity
Environment="UV_THREADPOOL_SIZE=64"
Environment="NODE_OPTIONS=--max-old-space-size=4096"
```

### Docker / Docker Compose

Use the provided compose file:

```bash
# Standalone
docker-compose -f docs/deployment/docker/docker-compose.resource-limits.yml up

# Merge with existing compose file
docker-compose -f docker-compose.yml \
  -f docs/deployment/docker/docker-compose.resource-limits.yml up
```

**Key settings:**
```yaml
services:
  app:
    ulimits:
      nofile:
        soft: 65535
        hard: 65535
    deploy:
      resources:
        limits:
          memory: 4G
    environment:
      - UV_THREADPOOL_SIZE=64
```

### Kubernetes

Add to your deployment manifest:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: monkey-coder
spec:
  containers:
  - name: app
    image: monkey-coder:latest
    resources:
      requests:
        memory: "2Gi"
        cpu: "1000m"
      limits:
        memory: "4Gi"
        cpu: "2000m"
    env:
    - name: UV_THREADPOOL_SIZE
      value: "64"
    securityContext:
      # Many K8s distros set this automatically, but verify:
      # sysctl fs.file-max and fs.nr_open are high enough
```

### Railway

Railway automatically provides reasonable defaults, but you can enhance them:

```json
// railpack.json
{
  "deploy": {
    "startCommand": "python run_server.py",
    "env": {
      "UV_THREADPOOL_SIZE": "64",
      "NODE_OPTIONS": "--max-old-space-size=4096"
    }
  }
}
```

Railway sets open files to 65536 by default, which meets our requirements.

### Local Development

#### Linux/macOS

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
# Increase file descriptor limit
ulimit -n 65535

# Set unlimited virtual memory
ulimit -v unlimited

# Node.js performance
export UV_THREADPOOL_SIZE=64
export NODE_OPTIONS="--max-old-space-size=4096"
```

#### Windows (WSL2)

In WSL2 terminal:

```bash
# Add to ~/.bashrc or ~/.zshrc
ulimit -n 65535
export UV_THREADPOOL_SIZE=64
```

## Runtime Monitoring

### Automatic Logging

The application logs resource limits at startup:

**Python (run_server.py):**
```
[startup] System Resource Limits:
[startup]   open files      = 65536
[startup]   virtual memory  = unlimited
[startup]   threadpool size = 64
[startup] ✅ All resource limits are properly configured
```

**TypeScript/Node.js (CLI/Web):**
```javascript
import { logSystemLimits } from './utils/system-limits';

// At application startup
logSystemLimits('[preflight]');
```

### Manual Probing

**Python:**
```python
from monkey_coder.utils.system_limits import log_startup_limits, get_system_limits_info

# Log to console
log_startup_limits()

# Get structured data
info = get_system_limits_info()
print(info)
```

**TypeScript:**
```typescript
import { logSystemLimits, getSystemLimitsInfo } from '@monkey-coder/utils';

// Log to console
logSystemLimits('[preflight]');

// Get structured data
const info = getSystemLimitsInfo();
console.log(info);
```

## Troubleshooting

### "Too many open files" Error

**Symptoms:**
- `EMFILE: too many open files`
- Socket connection failures
- Random timeouts

**Fix:**
```bash
# Temporary (current shell)
ulimit -n 65535

# Permanent (add to /etc/security/limits.conf)
* soft nofile 65535
* hard nofile 65535

# For systemd services
LimitNOFILE=65535
```

### Memory Allocation Failures

**Symptoms:**
- `Cannot allocate memory`
- Process crashes with OOM despite available RAM
- WASM/browser failures

**Fix:**
```bash
# Temporary
ulimit -v unlimited

# Systemd service
MemoryMax=infinity

# Docker
deploy:
  resources:
    limits:
      memory: 0  # unlimited
```

### Performance Issues with I/O Operations

**Symptoms:**
- Slow file operations
- DNS resolution delays
- Crypto operations taking too long

**Fix:**
```bash
# Set Node.js threadpool size
export UV_THREADPOOL_SIZE=64

# Systemd
Environment="UV_THREADPOOL_SIZE=64"

# Docker
environment:
  - UV_THREADPOOL_SIZE=64
```

## Verification

### CI/CD Preflight Check

The GitHub Actions workflow automatically validates limits:

```bash
# Manual run locally
./.github/workflows/preflight-limits.yml
```

### Production Verification

After deployment, verify limits are applied:

```bash
# For systemd
systemctl show monkey-coder -p LimitNOFILE
systemctl show monkey-coder -p MemoryMax

# For Docker
docker inspect <container_id> | jq '.[0].HostConfig.Ulimits'

# From inside container
docker exec <container_id> ulimit -a

# Check application logs
# Should see: "[startup] ✅ All resource limits are properly configured"
```

## Best Practices

1. **Always set limits explicitly** - Don't rely on system defaults
2. **Log limits at startup** - Use the provided utilities
3. **Test in CI/CD** - Use the preflight workflow
4. **Monitor in production** - Check logs for warnings
5. **Document deviations** - If you need different limits, document why

## References

- [Node.js UV_THREADPOOL_SIZE](https://nodejs.org/api/cli.html#uv_threadpool_sizesize)
- [Linux ulimit](https://ss64.com/bash/ulimit.html)
- [systemd Resource Control](https://www.freedesktop.org/software/systemd/man/systemd.resource-control.html)
- [Docker Resource Constraints](https://docs.docker.com/config/containers/resource_constraints/)

## Support

If you encounter issues with resource limits:

1. Check the startup logs for warnings
2. Run the preflight workflow locally
3. Verify platform-specific configuration
4. Open an issue with logs and system information
