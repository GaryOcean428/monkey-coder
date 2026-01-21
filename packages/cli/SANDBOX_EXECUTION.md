# Docker-based Sandboxed Shell Execution

## Overview

This feature implements Docker-based sandboxed shell execution for safe command running in agent mode. It provides three execution modes with varying levels of isolation and security.

## Architecture

### Components

1. **SandboxExecutor** (`packages/cli/src/sandbox/index.ts`)
   - Unified interface for all sandbox modes
   - Handles mode selection and fallback logic
   - Integrates with existing DockerSandbox

2. **DockerSandbox** (`packages/cli/src/sandbox/docker-executor.ts`)
   - Docker container-based isolation
   - Resource limits (CPU, memory)
   - Network isolation
   - Security hardening (no capabilities, no-new-privileges)

3. **Shell Execute Tool** (`packages/cli/src/tools/index.ts`)
   - Updated to use SandboxExecutor
   - Passes sandbox mode from agent configuration
   - Records commands for checkpoint tracking

4. **Agent Command** (`packages/cli/src/commands/agent.ts`)
   - CLI options: `--sandbox <mode>` and `--docker`
   - Configuration passed to AgentRunner

5. **AgentRunner** (`packages/cli/src/agent-runner.ts`)
   - Accepts sandbox configuration
   - Passes mode to tool calls
   - Displays sandbox mode in console

## Sandbox Modes

### 1. Spawn Mode (Default)
**Safety Level: Medium**

```bash
monkey agent --sandbox spawn --task "Your task"
# OR
monkey agent --task "Your task"  # spawn is default
```

**Features:**
- Uses Node.js `spawn()` with array arguments
- Prevents shell injection attacks
- No shell parsing of command strings
- Timeout enforcement
- Working directory isolation

**Use Cases:**
- Production agent mode (recommended)
- Untrusted command execution
- General purpose automation

**Limitations:**
- Same filesystem access as parent process
- Same network access as parent process
- Same user permissions

### 2. Docker Mode
**Safety Level: High**

```bash
monkey agent --docker --task "Your task"
# OR
monkey agent --sandbox docker --task "Your task"
```

**Features:**
- Full container isolation
- Resource limits:
  - Memory: 256MB (configurable)
  - CPU: 50% (configurable)
  - PID limit: 50 processes
- Network isolation (default: disabled)
- Security hardening:
  - All capabilities dropped
  - no-new-privileges
  - Read-only root filesystem (optional)
- Filesystem bind mounts with read/write control
- Automatic fallback to spawn if Docker unavailable

**Use Cases:**
- Maximum security requirements
- Untrusted code execution
- Resource-constrained environments
- Multi-tenant systems

**Requirements:**
- Docker daemon running
- User has Docker access
- Sufficient Docker resources

**Limitations:**
- Slower than spawn mode (container overhead)
- Requires Docker installation
- May have filesystem access restrictions

### 3. None Mode (Unsafe)
**Safety Level: None**

```bash
monkey agent --sandbox none --task "Your task"
```

**Features:**
- Direct command execution
- No sandboxing
- Full system access

**Use Cases:**
- Development/testing only
- Debugging
- Local experimentation

**⚠️ WARNING:** Do not use in production or with untrusted input!

## Configuration

### CLI Options

```bash
# Basic usage with default spawn mode
monkey agent --task "Run tests"

# Use Docker sandboxing
monkey agent --docker --task "Run tests"

# Explicit sandbox mode
monkey agent --sandbox docker --task "Build project"
monkey agent --sandbox spawn --task "Lint code"
monkey agent --sandbox none --task "Local test"  # Unsafe!

# Combined options
monkey agent \
  --sandbox docker \
  --task "Run untrusted script" \
  --max-iterations 10 \
  --model claude-sonnet-4
```

### Programmatic Usage

```typescript
import { getSandboxExecutor } from './sandbox/index.js';

// Create executor with options
const executor = getSandboxExecutor({
  mode: 'docker',
  timeout: 60000,        // 60 seconds
  memoryLimit: 512,      // 512 MB
  networkEnabled: false,  // Disable network
  workdir: '/workspace',
  readOnlyRoot: true,    // Read-only filesystem
});

// Execute command
const result = await executor.execute('npm', ['test']);

console.log('Exit code:', result.exitCode);
console.log('Output:', result.stdout);
console.log('Errors:', result.stderr);
console.log('Timed out:', result.timedOut);
```

### Agent Runner Integration

```typescript
import { AgentRunner } from './agent-runner.js';

const agent = new AgentRunner({
  sandboxMode: 'docker',
  requireApproval: true,
  model: 'claude-sonnet-4',
  maxIterations: 20,
});

await agent.runTask('Implement new feature');
```

## Security Considerations

### Spawn Mode Security
- ✅ Shell injection prevention (array args)
- ✅ Timeout enforcement
- ❌ No resource limits
- ❌ Full filesystem access
- ❌ Full network access
- ❌ Same user permissions

### Docker Mode Security
- ✅ Shell injection prevention
- ✅ Timeout enforcement
- ✅ Memory limits
- ✅ CPU limits
- ✅ Process limits (PID)
- ✅ Network isolation (default)
- ✅ Capability dropping (ALL)
- ✅ no-new-privileges
- ✅ Read-only root filesystem (optional)
- ✅ Controlled filesystem access (bind mounts)

### Best Practices

1. **Default to Spawn Mode**: Use spawn mode for most tasks
2. **Use Docker for Untrusted Code**: When running user-provided code
3. **Never Use None Mode in Production**: Only for development
4. **Enable Read-Only Root**: When possible for Docker mode
5. **Disable Network**: Unless specifically needed
6. **Set Appropriate Timeouts**: Prevent hung processes
7. **Require User Approval**: For dangerous operations

## Testing

### Unit Tests

```bash
cd packages/cli
yarn test sandbox.test
```

Tests cover:
- All three sandbox modes
- Timeout enforcement
- Working directory configuration
- Docker fallback behavior
- Error handling

### Manual Testing

```bash
# Run comprehensive manual tests
cd packages/cli
node scripts/test-sandbox.mjs
```

### Integration Testing

```bash
# Test with actual agent
monkey agent --docker --task "Echo hello world"
```

## Troubleshooting

### Docker Not Available

**Symptom:** "Docker not available, falling back to spawn mode"

**Solutions:**
1. Start Docker daemon: `sudo systemctl start docker`
2. Check Docker access: `docker ps`
3. Add user to docker group: `sudo usermod -aG docker $USER`
4. Accept fallback to spawn mode (still secure)

### Permission Denied Errors

**Symptom:** Exit code 126 or "Permission denied"

**Solutions:**
1. Check file permissions
2. Ensure working directory exists
3. Verify bind mount paths are accessible
4. Check Docker user permissions

### Timeout Issues

**Symptom:** Commands always timeout

**Solutions:**
1. Increase timeout: `--timeout 60000` (60 seconds)
2. Check command is not hanging
3. Verify network is available if needed
4. Check resource limits aren't too restrictive

### Memory/OOM Issues

**Symptom:** Container killed, OOMKilled = true

**Solutions:**
1. Increase memory limit in configuration
2. Optimize command memory usage
3. Check for memory leaks in scripts
4. Monitor container resource usage

## Performance

### Spawn Mode
- **Startup:** ~1-5ms
- **Overhead:** Minimal
- **Throughput:** High

### Docker Mode
- **Startup:** ~100-500ms (container creation)
- **Overhead:** Moderate (container isolation)
- **Throughput:** Medium (network/filesystem overhead)

### Recommendations
- Use spawn for simple commands (< 1 second)
- Use Docker for long-running or untrusted commands
- Consider caching/reusing Docker containers for repeated tasks (future enhancement)

## Future Enhancements

1. **Container Pooling**: Reuse containers for better performance
2. **Custom Docker Images**: Language-specific base images
3. **Volume Caching**: Persistent caches for dependencies
4. **Network Policies**: Fine-grained network control
5. **Resource Monitoring**: Real-time resource usage tracking
6. **Audit Logging**: Detailed security audit logs
7. **Rootless Docker**: Enhanced security with rootless mode
8. **Kubernetes Support**: Deploy to K8s for production scale

## Related Files

- Implementation: `packages/cli/src/sandbox/index.ts`
- Docker executor: `packages/cli/src/sandbox/docker-executor.ts`
- Tool integration: `packages/cli/src/tools/index.ts`
- CLI command: `packages/cli/src/commands/agent.ts`
- Agent runner: `packages/cli/src/agent-runner.ts`
- Tests: `packages/cli/__tests__/sandbox.test.ts`
- Manual tests: `packages/cli/scripts/test-sandbox.mjs`

## References

- Docker Security: https://docs.docker.com/engine/security/
- Node.js spawn: https://nodejs.org/api/child_process.html#child_processspawncommand-args-options
- Container Isolation: https://docs.docker.com/engine/security/userns-remap/
