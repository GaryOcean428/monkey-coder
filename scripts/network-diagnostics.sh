#!/bin/bash
# Network Tracing Script for Monkey Coder CLI Installation
# Captures detailed network requests during installation and runtime

set -e

echo "🌐 Monkey Coder Network Diagnostics"
echo "==================================="

# Create logs directory
LOG_DIR="/tmp/monkey-network-logs"
mkdir -p "$LOG_DIR"

echo "📁 Logs will be saved to: $LOG_DIR"

# 1. Clean environment test
echo -e "\n📋 Step 1: Clean environment installation test"
echo "Creating temporary clean environment..."

TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Initialize minimal package.json
cat > package.json << 'EOF'
{
  "name": "test-monkey-install",
  "version": "1.0.0",
  "private": true
}
EOF

echo "Testing clean install with request tracing..."
NODE_DEBUG=request npm install monkey-coder-cli 2>&1 | tee "$LOG_DIR/clean-install-trace.log"

# 2. Capture all network requests during installation
echo -e "\n📋 Step 2: Detailed network request analysis"
echo "Analyzing install trace for HTTP requests..."

# Extract HTTP requests from the trace
grep -E "(GET|POST|PUT|DELETE|HEAD)" "$LOG_DIR/clean-install-trace.log" > "$LOG_DIR/http-requests.log" || echo "No HTTP requests found in trace"

# Extract registry requests
grep -i "registry" "$LOG_DIR/clean-install-trace.log" > "$LOG_DIR/registry-requests.log" || echo "No registry requests found"

# Extract any post-install activity  
grep -i "postinstall\|post-install" "$LOG_DIR/clean-install-trace.log" > "$LOG_DIR/postinstall-activity.log" || echo "No post-install activity found"

# 3. Test CLI network behavior
echo -e "\n📋 Step 3: CLI runtime network behavior"
if command -v monkey-coder >/dev/null 2>&1; then
    echo "Testing CLI network calls..."
    
    # Capture network calls during CLI operations
    echo "Testing config commands (should be local only)..."
    strace -e trace=network,connect -o "$LOG_DIR/cli-config-trace.log" monkey-coder config --help 2>&1 || echo "Config trace completed"
    
    echo "Testing health command (should make API call)..."
    strace -e trace=network,connect -o "$LOG_DIR/cli-health-trace.log" monkey-coder health 2>&1 || echo "Health trace completed"
    
else
    echo "❌ monkey-coder command not available for runtime testing"
fi

# 4. API endpoint testing
echo -e "\n📋 Step 4: Direct API endpoint testing"
BASE_URL="${MONKEY_CODER_BASE_URL:-https://monkey-coder.up.railway.app}"

echo "Testing API endpoints directly..."

# Test health endpoint with detailed curl output
echo "Testing $BASE_URL/health..."
curl -v "$BASE_URL/health" 2>&1 | tee "$LOG_DIR/health-endpoint-trace.log" || echo "Health endpoint failed"

# Test other potential endpoints
for endpoint in "/healthz" "/api/health" "/status" "/ping"; do
    echo "Testing $BASE_URL$endpoint..."
    curl -v "$BASE_URL$endpoint" 2>&1 > "$LOG_DIR/endpoint-${endpoint//\//-}-trace.log" || echo "Endpoint $endpoint failed"
done

# 5. DNS and connectivity testing
echo -e "\n📋 Step 5: DNS and connectivity diagnostics"
echo "Testing DNS resolution..."
nslookup monkey-coder.up.railway.app 2>&1 | tee "$LOG_DIR/dns-lookup.log"

echo "Testing connectivity..."
ping -c 3 monkey-coder.up.railway.app 2>&1 | tee "$LOG_DIR/ping-test.log" || echo "Ping failed"

# Test TLS connection
echo "Testing TLS connection..."
openssl s_client -connect monkey-coder.up.railway.app:443 -servername monkey-coder.up.railway.app < /dev/null 2>&1 | tee "$LOG_DIR/tls-test.log"

# 6. Registry connectivity testing
echo -e "\n📋 Step 6: NPM registry connectivity"
echo "Testing npm registry connectivity..."
curl -v https://registry.npmjs.org/ 2>&1 | tee "$LOG_DIR/registry-connectivity.log"

echo "Testing package availability..."
curl -v "https://registry.npmjs.org/monkey-coder-cli" 2>&1 | tee "$LOG_DIR/package-availability.log"

# 7. Generate network analysis report
echo -e "\n📊 Network Diagnostics Summary"
echo "==============================="

cat << EOF > "$LOG_DIR/network-analysis-report.md"
# Network Diagnostics Report

Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

## HTTP Requests During Installation
\`\`\`
$(cat "$LOG_DIR/http-requests.log" 2>/dev/null || echo "No HTTP requests captured")
\`\`\`

## Registry Requests
\`\`\`
$(cat "$LOG_DIR/registry-requests.log" 2>/dev/null || echo "No registry requests captured")
\`\`\`

## Post-Install Activity
\`\`\`
$(cat "$LOG_DIR/postinstall-activity.log" 2>/dev/null || echo "No post-install activity detected")
\`\`\`

## Health Endpoint Response
\`\`\`
$(grep -A 20 "< HTTP" "$LOG_DIR/health-endpoint-trace.log" 2>/dev/null || echo "Health endpoint not responding")
\`\`\`

## DNS Resolution
\`\`\`
$(cat "$LOG_DIR/dns-lookup.log" 2>/dev/null || echo "DNS lookup failed")
\`\`\`

## Recommendations
Based on the network trace analysis:

1. **Installation Issues**: Check http-requests.log for any 402/502 responses
2. **API Issues**: Check health-endpoint-trace.log for server responses
3. **DNS Issues**: Check dns-lookup.log for resolution problems
4. **Registry Issues**: Check registry-connectivity.log for npm access problems

## Files Generated
- clean-install-trace.log: Complete installation trace
- http-requests.log: All HTTP requests during install
- registry-requests.log: NPM registry requests
- postinstall-activity.log: Post-installation scripts
- cli-*-trace.log: CLI command network traces
- health-endpoint-trace.log: API health check details
- dns-lookup.log: DNS resolution test
- registry-connectivity.log: NPM registry connectivity
EOF

echo "✅ Network diagnostics completed"
echo "📄 Full report saved to: $LOG_DIR/network-analysis-report.md"
echo ""
echo "Key files to review:"
echo "- $LOG_DIR/clean-install-trace.log (installation network activity)"
echo "- $LOG_DIR/health-endpoint-trace.log (API health endpoint)"
echo "- $LOG_DIR/network-analysis-report.md (summary report)"

# Cleanup temp directory
rm -rf "$TEMP_DIR"