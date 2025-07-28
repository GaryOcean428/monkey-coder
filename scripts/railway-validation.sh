#!/bin/bash
# Railway Environment Validation Script
# Validates Railway deployment configuration and environment

set -e

echo "🚂 Railway Environment Validation"
echo "================================="

LOG_DIR="/tmp/railway-validation-logs"
mkdir -p "$LOG_DIR"

# 1. Railway CLI availability
echo -e "\n📋 Step 1: Railway CLI validation"
if command -v railway >/dev/null 2>&1; then
    echo "✅ Railway CLI available"
    railway --version
    
    # Check authentication
    if railway auth 2>&1 | grep -q "Logged in"; then
        echo "✅ Railway CLI authenticated"
    else
        echo "❌ Railway CLI not authenticated"
        echo "Run 'railway login' to authenticate"
    fi
else
    echo "❌ Railway CLI not installed"
    echo "Install with: npm install -g @railway/cli"
fi

# 2. Environment variables validation
echo -e "\n📋 Step 2: Environment variables validation"
if command -v railway >/dev/null 2>&1; then
    echo "Fetching Railway environment variables..."
    railway vars 2>&1 | tee "$LOG_DIR/railway-vars.log" || echo "Failed to fetch Railway vars"
    
    # Check for required variables
    echo -e "\nChecking required environment variables..."
    for var in "OPENAI_API_KEY" "STRIPE_API_KEY" "DATABASE_URL" "SENTRY_DSN"; do
        if railway vars | grep -q "$var"; then
            echo "✅ $var: Present in Railway"
        else
            echo "❌ $var: Missing from Railway"
        fi
    done
else
    echo "⚠️  Cannot validate Railway environment variables (CLI not available)"
fi

# 3. Service status validation
echo -e "\n📋 Step 3: Railway service status"
if command -v railway >/dev/null 2>&1; then
    echo "Checking Railway service status..."
    railway status 2>&1 | tee "$LOG_DIR/railway-status.log" || echo "Failed to get Railway status"
    
    echo -e "\nFetching recent Railway logs..."
    railway logs --tail 50 2>&1 | tee "$LOG_DIR/railway-recent-logs.log" || echo "Failed to fetch Railway logs"
    
    # Look for error patterns in logs
    echo -e "\nAnalyzing logs for error patterns..."
    if grep -E "(502|503|500|ERROR|FATAL|crash)" "$LOG_DIR/railway-recent-logs.log"; then
        echo "❌ Errors found in Railway logs"
    else
        echo "✅ No critical errors in recent logs"
    fi
else
    echo "⚠️  Cannot validate Railway service status (CLI not available)"
fi

# 4. Railway configuration validation
echo -e "\n📋 Step 4: Railway configuration files"
if [ -f "railpack.json" ]; then
    echo "✅ railpack.json found"
    echo "Validating railpack.json structure..."
    
    # Check required fields
    if jq -e '.healthcheck.path' railpack.json >/dev/null 2>&1; then
        HEALTH_PATH=$(jq -r '.healthcheck.path' railpack.json)
        echo "✅ Health check path configured: $HEALTH_PATH"
    else
        echo "❌ Health check path not configured in railpack.json"
    fi
    
    if jq -e '.start.cmd' railpack.json >/dev/null 2>&1; then
        START_CMD=$(jq -r '.start.cmd' railpack.json)
        echo "✅ Start command configured: $START_CMD"
    else
        echo "❌ Start command not configured in railpack.json"
    fi
    
    # Validate JSON structure
    if jq . railpack.json >/dev/null 2>&1; then
        echo "✅ railpack.json is valid JSON"
        jq . railpack.json > "$LOG_DIR/railpack-formatted.json"
    else
        echo "❌ railpack.json has invalid JSON syntax"
    fi
else
    echo "❌ railpack.json not found"
fi

# 5. Health endpoint testing
echo -e "\n📋 Step 5: Health endpoint validation"
BASE_URL="${RAILWAY_SERVICE_URL:-https://monkey-coder.up.railway.app}"
HEALTH_PATH="/health"

echo "Testing health endpoint: $BASE_URL$HEALTH_PATH"

# Test with different methods
for method in GET HEAD; do
    echo "Testing $method $BASE_URL$HEALTH_PATH..."
    curl -X "$method" -v "$BASE_URL$HEALTH_PATH" 2>&1 | tee "$LOG_DIR/health-$method-test.log" || echo "$method test failed"
done

# Check specific Railway health endpoint format
echo "Testing Railway-specific health check..."
curl -H "Accept: application/json" -v "$BASE_URL$HEALTH_PATH" 2>&1 | tee "$LOG_DIR/health-railway-format.log" || echo "Railway health check failed"

# 6. Database connectivity (if applicable)
echo -e "\n📋 Step 6: Database connectivity validation"
if command -v railway >/dev/null 2>&1; then
    if railway vars | grep -q "DATABASE_URL"; then
        echo "✅ DATABASE_URL configured in Railway"
        
        # Try to connect to database (PostgreSQL assumed)
        if command -v psql >/dev/null 2>&1; then
            echo "Testing database connectivity..."
            DB_URL=$(railway vars | grep DATABASE_URL | cut -d'=' -f2- || echo "")
            if [ -n "$DB_URL" ]; then
                psql "$DB_URL" -c "SELECT 1;" 2>&1 | tee "$LOG_DIR/database-test.log" || echo "Database connection failed"
            fi
        else
            echo "⚠️  psql not available for database testing"
        fi
    else
        echo "⚠️  DATABASE_URL not configured"
    fi
fi

# 7. Performance and resource validation
echo -e "\n📋 Step 7: Performance validation"
if command -v railway >/dev/null 2>&1; then
    echo "Checking Railway service metrics..."
    railway logs --tail 100 | grep -E "(memory|cpu|performance)" | tail -10 > "$LOG_DIR/performance-metrics.log" || echo "No performance metrics found"
    
    if [ -s "$LOG_DIR/performance-metrics.log" ]; then
        echo "Recent performance metrics:"
        cat "$LOG_DIR/performance-metrics.log"
    else
        echo "⚠️  No performance metrics available in logs"
    fi
fi

# 8. Generate Railway validation report
echo -e "\n📊 Railway Validation Summary"
echo "============================="

cat << EOF > "$LOG_DIR/railway-validation-report.md"
# Railway Validation Report

Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

## Service Configuration
- Base URL: $BASE_URL
- Health Check Path: $HEALTH_PATH

## Environment Variables Status
$(if command -v railway >/dev/null 2>&1; then railway vars | head -20 | sed 's/^/- /'; else echo "- Railway CLI not available"; fi)

## Recent Error Patterns
\`\`\`
$(grep -E "(502|503|500|ERROR|FATAL)" "$LOG_DIR/railway-recent-logs.log" 2>/dev/null | tail -10 || echo "No recent errors found")
\`\`\`

## Health Endpoint Response
\`\`\`
$(grep -A 10 "< HTTP" "$LOG_DIR/health-GET-test.log" 2>/dev/null | head -20 || echo "Health endpoint not responding")
\`\`\`

## Recommended Actions
1. **If 502/503 errors**: Check railway-recent-logs.log for service crashes
2. **If environment issues**: Verify all required variables are set with 'railway vars'
3. **If health check fails**: Check railpack.json configuration and service startup
4. **If database issues**: Verify DATABASE_URL and connection permissions

## Files Generated
- railway-vars.log: Environment variables
- railway-status.log: Service status
- railway-recent-logs.log: Recent service logs
- health-*-test.log: Health endpoint tests
- performance-metrics.log: Performance data
EOF

echo "✅ Railway validation completed"
echo "📄 Full report saved to: $LOG_DIR/railway-validation-report.md"
echo ""
echo "Key commands for troubleshooting:"
echo "- railway logs -s monkey-coder --tail 300"
echo "- railway vars"
echo "- railway status"
echo "- curl -i $BASE_URL$HEALTH_PATH"