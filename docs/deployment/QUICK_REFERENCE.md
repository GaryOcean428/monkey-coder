# System Resource Limits - Quick Reference Card

## ⚠️ Critical: Check Before Every Deployment

```bash
ulimit -n  # Must be ≥65535
ulimit -v  # Must be unlimited
echo $UV_THREADPOOL_SIZE  # Should be 64
```

## Platform-Specific Quick Fixes

### Linux (Shell)
```bash
ulimit -n 65535
ulimit -v unlimited
export UV_THREADPOOL_SIZE=64
```

### Systemd Service
```ini
[Service]
LimitNOFILE=65535
MemoryMax=infinity
Environment="UV_THREADPOOL_SIZE=64"
```

### Docker Compose
```yaml
services:
  app:
    ulimits:
      nofile:
        soft: 65535
        hard: 65535
    environment:
      - UV_THREADPOOL_SIZE=64
```

### Railway
```json
{
  "deploy": {
    "env": {
      "UV_THREADPOOL_SIZE": "64"
    }
  }
}
```

### Kubernetes
```yaml
env:
- name: UV_THREADPOOL_SIZE
  value: "64"
resources:
  limits:
    memory: "4Gi"
```

## Common Error Messages → Solutions

| Error | Fix |
|-------|-----|
| `EMFILE: too many open files` | `ulimit -n 65535` |
| `Cannot allocate memory` | `ulimit -v unlimited` |
| Slow file/network ops | `export UV_THREADPOOL_SIZE=64` |
| `ECONNRESET`, socket errors | Check all three above |

## Validation Commands

```bash
# Manual check
ulimit -a

# Python runtime check
python3 -c "from monkey_coder.utils.system_limits import log_startup_limits; log_startup_limits()"

# Node.js runtime check
node -e "require('./packages/cli/dist/utils.js').logSystemLimits()"

# CI/CD check
# Automatically runs in GitHub Actions on every push
```

## Expected Startup Output

✅ **Healthy:**
```
[startup] System Resource Limits:
[startup]   open files      = 65536
[startup]   virtual memory  = unlimited
[startup]   threadpool size = 64
[startup] ✅ All resource limits are properly configured
```

⚠️ **Needs Attention:**
```
[startup] ⚠️  Resource limit warnings:
[startup]   - Open files limit is low (1024). Recommended: ≥65535
[startup]   - UV_THREADPOOL_SIZE not set or too low (default 4)
```

## Emergency Troubleshooting

1. **Check startup logs** - Look for resource limit warnings
2. **Verify limits** - Run `ulimit -a`
3. **Apply fixes** - Use platform-specific commands above
4. **Restart service** - Limits only apply after restart
5. **Verify again** - Check logs for ✅ message

## More Information

- Full Guide: [SYSTEM_RESOURCE_LIMITS.md](./SYSTEM_RESOURCE_LIMITS.md)
- Deployment: [README.md](./README.md)
- Production: [production-deployment-guide.md](../production-deployment-guide.md)
