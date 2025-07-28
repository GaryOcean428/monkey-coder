#!/bin/bash
# Installation Validation Script for Monkey Coder CLI
# Addresses the diagnostic requirements from the review feedback

set -e

echo "🔍 Monkey Coder CLI Installation Validation"
echo "==========================================="

# 1. Capture install logs with verbose output
echo -e "\n📋 Step 1: Testing package installation with verbose logging"
echo "Command: npm install @monkey-coder/cli --verbose"

# Create temp directory for logs
LOG_DIR="/tmp/monkey-install-logs"
mkdir -p "$LOG_DIR"

# Capture verbose install logs
echo "Capturing installation logs to $LOG_DIR/install.log..."
if NODE_DEBUG=request npm install @monkey-coder/cli --verbose 2>&1 | tee "$LOG_DIR/install.log"; then
    echo "✅ Installation successful"
else
    echo "❌ Installation failed"
    echo "📄 Install log contents:"
    cat "$LOG_DIR/install.log"
    exit 1
fi

# 2. Registry configuration validation  
echo -e "\n📋 Step 2: Validating npm registry configuration"
REGISTRY=$(npm config get registry)
echo "Current registry: $REGISTRY"
if [ "$REGISTRY" = "https://registry.npmjs.org/" ]; then
    echo "✅ Registry correctly configured"
else
    echo "❌ Registry misconfigured. Expected: https://registry.npmjs.org/"
    echo "Setting correct registry..."
    npm config set registry https://registry.npmjs.org/
fi

# 3. Package verification
echo -e "\n📋 Step 3: Verifying package availability"
if npm view @monkey-coder/cli version; then
    echo "✅ Package @monkey-coder/cli found in registry"
else
    echo "❌ Package @monkey-coder/cli not found in registry"
    echo "Checking if monkey-coder-cli exists instead..."
    if npm view monkey-coder-cli version; then
        echo "⚠️  Found monkey-coder-cli instead of @monkey-coder/cli"
        echo "This indicates a package naming issue that needs to be resolved"
    fi
fi

# 4. CLI configuration test
echo -e "\n📋 Step 4: Testing CLI configuration"
if command -v monkey-coder >/dev/null 2>&1; then
    echo "✅ monkey-coder command available"
    
    # Test configuration commands
    echo "Testing configuration setup..."
    if [ -n "$MONKEY_CODER_API_KEY" ]; then
        monkey-coder config set apiKey "$MONKEY_CODER_API_KEY" || echo "⚠️  Config set failed"
    fi
    
    if [ -n "$MONKEY_CODER_BASE_URL" ]; then
        monkey-coder config set baseUrl "$MONKEY_CODER_BASE_URL" || echo "⚠️  Base URL config failed"
    else
        echo "Setting default base URL..."
        monkey-coder config set baseUrl "https://monkey-coder.up.railway.app" || echo "⚠️  Base URL config failed"
    fi
    
    echo "✅ CLI configuration completed"
else
    echo "❌ monkey-coder command not found after installation"
fi

# 5. Health check validation
echo -e "\n📋 Step 5: Testing API health check"
BASE_URL="${MONKEY_CODER_BASE_URL:-https://monkey-coder.up.railway.app}"
echo "Testing health endpoint: $BASE_URL/health"

if curl -sf "$BASE_URL/health" -o "$LOG_DIR/health-response.json"; then
    echo "✅ Health endpoint responding"
    echo "Response:"
    cat "$LOG_DIR/health-response.json" | jq . 2>/dev/null || cat "$LOG_DIR/health-response.json"
else
    echo "❌ Health endpoint not responding (502/503 error)"
    echo "This indicates Railway service issues"
fi

# Test CLI health command if available
if command -v monkey-coder >/dev/null 2>&1; then
    echo -e "\nTesting CLI health command..."
    if monkey-coder health; then
        echo "✅ CLI health check successful"
    else
        echo "❌ CLI health check failed"
    fi
fi

# 6. Environment validation
echo -e "\n📋 Step 6: Environment validation"
echo "Required environment variables:"
for var in MONKEY_CODER_API_KEY OPENAI_API_KEY STRIPE_API_KEY; do
    if [ -n "${!var}" ]; then
        echo "✅ $var: Set (${#!var} characters)"
    else
        echo "❌ $var: Not set"
    fi
done

# 7. Generate summary report
echo -e "\n📊 Installation Validation Summary"
echo "=================================="
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "Registry: $REGISTRY"
echo "Logs saved to: $LOG_DIR"
echo ""
echo "Next steps if issues found:"
echo "1. Check $LOG_DIR/install.log for detailed installation logs"
echo "2. Verify Railway service status with: railway logs -s monkey-coder --tail 300"
echo "3. Confirm environment variables are set correctly"
echo "4. Test health endpoint manually: curl -i $BASE_URL/health"

echo -e "\n✅ Validation script completed"