# Monkey Coder CLI Installation & Deployment Troubleshooting Guide

This guide addresses common installation and deployment issues,
particularly focusing on 402/502 errors and Railway deployment problems.

## Quick Diagnostic Commands

Run these commands to gather diagnostic information:

```bash
# 1. Validate installation
./scripts/validate-installation.sh

# 2. Network diagnostics
./scripts/network-diagnostics.sh

# 3. Railway environment validation
./scripts/railway-validation.sh
```

## Common Issues & Solutions

### Issue H1: Package Naming Confusion

**Symptoms:**
- `monkey-coder-cli` not found in npm registry
- Installation fails with 404 errors
- References to `monkey-coder-cli` vs `monkey-coder-cli`

**Root Cause:**
Package naming inconsistency between published package and documentation.

**Solution:**

```bash
# Check which package is actually published
npm view monkey-coder-cli
npm view monkey-coder-cli

# Install the correct package
npm install -g monkey-coder-cli

# If monkey-coder-cli doesn't exist, use:
npm install -g monkey-coder-cli
```

**Verification:**

```bash
which monkey-coder
monkey-coder --version
```

### Issue H2: Post-install Scripts Making Network Calls

**Symptoms:**
- Installation hangs or fails with network errors
- 402/502 errors during `npm install`
- CI builds failing on installation

**Root Cause:**
Post-install scripts attempting to download models or contact APIs during installation.

**Solution:**

```bash
# Install with CI flag to skip network-dependent scripts
CI=true npm install -g monkey-coder-cli

# Or disable all scripts
npm install -g monkey-coder-cli --ignore-scripts
```

**For CI/CD Pipelines:**

```yaml
# GitHub Actions
- name: Install CLI
  run: |
    export CI=true
    npm install -g monkey-coder-cli
  env:
    NODE_ENV: production
```

### Issue H3: Registry Misconfiguration

**Symptoms:**
- npm install tries wrong registry
- Azure feeds or corporate registries causing 402 errors
- Authentication failures

**Solution:**

```bash
# Reset to official npm registry
npm config set registry https://registry.npmjs.org/
echo "registry=https://registry.npmjs.org/" > ~/.npmrc

# Clear npm cache
npm cache clean --force

# Verify registry
npm config get registry
```

**Project-level fix:**

```bash
# Add .npmrc to project root
echo "registry=https://registry.npmjs.org/" > .npmrc
```

### Issue H4: Railway Service Returning 502/503

**Symptoms:**
- `curl https://monkey-coder.up.railway.app/health` returns 502
- CLI health command fails
- Service appears down

**Diagnostic Steps:**

```bash
# Check Railway service status
railway logs --service monkey-coder --deployment

# Check service health
railway status

# Verify environment variables
railway variables --service monkey-coder

# Test health endpoint
curl -v https://monkey-coder.up.railway.app/health
```

**Common Fixes:**

1. **Service Crashed:**

   ```bash
   # Restart the service
   railway up

   # Check for startup errors
   railway logs --service monkey-coder --deployment
   ```

2. **Missing Environment Variables:**

   ```bash
   # Set required variables
   railway variables set OPENAI_API_KEY=your_key_here
   railway variables set STRIPE_API_KEY=your_stripe_key
   railway variables set DATABASE_URL=your_db_url
   ```

3. **Database Connection Issues:**

```bash
# Check database connectivity
railway connect postgres
# or
psql $DATABASE_URL -c "SELECT 1;"
```

### Issue H5: Missing Environment Variables

**Symptoms:**
- 402 or 500 errors from API
- Authentication failures
- Service starts but endpoints fail

**Solution:**

```bash
# Check what's configured
railway vars

# Set missing variables
railway var set OPENAI_API_KEY="sk-..."
railway var set STRIPE_API_KEY="sk_..."
railway var set SENTRY_DSN="HTTPS://..."

# For local development
cp .env.example .env
# Edit .env with your values
```

**CLI Configuration:**

```bash
# Configure CLI to use Railway service
monkey-coder config set baseUrl "https://monkey-coder.up.railway.app"
monkey-coder config set apiKey "your-API-key"

# Test configuration
monkey-coder health
```

## Advanced Troubleshooting

### Network Request Tracing

Trace all network requests during installation:

```bash
# Full network trace
NODE_DEBUG=request npm install -g monkey-coder-cli 2>&1 | tee install-trace.log

# Analyze HTTP requests
grep -E "(GET|POST)" install-trace.log

# Check for post-install network activity
grep -i "postinstall" install-trace.log
```

### CLI Network Debugging

Debug CLI network calls:

```bash
# Trace CLI network calls
strace -e trace=network monkey-coder health

# Enable verbose logging
DEBUG=* monkey-coder health

# Check CLI configuration
monkey-coder config list
```

### Railway Service Debugging

Deep dive into Railway service issues:

```bash
# Get detailed service info
railway status --json

# Check recent deployments
railway deployments

# Monitor live logs
railway logs --service monkey-coder --deployment

# Check resource usage
railway metrics
```

### Health Endpoint Analysis

Test health endpoint comprehensively:

```bash
# Test different methods
curl -X GET https://monkey-coder.up.railway.app/health
curl -X HEAD https://monkey-coder.up.railway.app/health

# Test with headers
curl -H "Accept: application/JSON" https://monkey-coder.up.railway.app/health

# Test alternative paths
curl https://monkey-coder.up.railway.app/healthz
curl https://monkey-coder.up.railway.app/api/health
```

## Prevention & Best Practices

### For Developers

1. **Use scoped package names consistently**
2. **Guard post-install scripts with CI detection**
3. **Test installations in clean environments**
4. **Provide fallback health endpoints**

### For CI/CD

```bash
# Safe installation in CI
- name: Install CLI
  run: |
    echo "registry=HTTPS://registry.npmjs.org/" >> .npmrc
    CI=true npm install -g monkey-coder-cli

- name: Validate Installation
  run: |
    monkey-coder --version
    monkey-coder config set baseUrl "${{ secrets.API_BASE_URL }}"

- name: Health Check
  run: |
    curl -sf "${{ secrets.API_BASE_URL }}/health"
```

### For Railway Deployment

1. **Set health check timeout appropriately**

```json
{
  "deploy": {
    "healthCheckPath": "/health",
    "healthCheckTimeout": 100
  }
}
```

2. **Configure environment variables before deployment**
3. **Test locally before deploying**
4. **Monitor deployment logs**

### Issue H6: Docker Buildx Build Failures with yarn

**Symptoms:**
- Docker Buildx build fails with "Couldn't find the node_modules state file - running an install might help"
- Build fails during yarn installation phase
- Next.js build fails due to missing dependencies

**Root Cause:**
Using `yarn install --mode=update-lockfile` only updates the lockfile but doesn't actually install and link dependencies in the node_modules directory.

**Solution:**
Modify the Dockerfile to run both commands sequentially:

```dockerfile
# Instead of:
RUN yarn install --mode=update-lockfile

# Use:
RUN yarn install --mode=update-lockfile && yarn install
```

This ensures:
1. First, yarn updates the lockfile to resolve any dependency conflicts
2. Then, yarn performs the actual installation and linking of dependencies

**Verification:**

```bash
# Test the fix locally
Docker build -t test-build .

# For Railway deployment:
railway up
```

**Expected Build Time:**
- Local build: ~60-90 seconds
- Railway cloud build: ~200-220 seconds (including push time)

## Getting Help

If issues persist:

1. **Run all diagnostic scripts** and save outputs
2. **Check Railway logs** for specific error messages
3. **Verify environment variables** are set correctly
4. **Test in clean environment** to isolate issues

**Diagnostic Data to Collect:**
- Output from `./scripts/validate-installation.sh`
- Output from `./scripts/network-diagnostics.sh`
- Output from `./scripts/railway-validation.sh`
- Railway logs: `railway logs --tail 500`
- npm install logs with verbose output
- Docker build logs: `Docker build --progress=plain . 2>&1 | tee build.log`
