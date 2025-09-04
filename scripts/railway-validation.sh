#!/bin/bash
# Railway Environment Validation Script (updated)
# Validates Railway deployment configuration and environment using current CLI and railpack schema

set -e

echo "🚂 Railway Environment Validation"
echo "================================="

LOG_DIR="/tmp/railway-validation-logs"
mkdir -p "$LOG_DIR"

# Helper: safely run a command and tee to file
run_and_tee() {
  local outfile="$1"; shift
  ("$@" 2>&1 || true) | tee "$outfile"
}

# 1. Railway CLI availability
echo -e "\n📋 Step 1: Railway CLI validation"
if command -v railway >/dev/null 2>&1; then
  echo "✅ Railway CLI available"
  railway --version || true
else
  echo "❌ Railway CLI not installed"
  echo "Install with: npm install -g @railway/cli"
fi

# 2. Environment variables validation
echo -e "\n📋 Step 2: Environment variables validation"
if command -v railway >/dev/null 2>&1; then
  echo "Fetching Railway environment variables..."
  run_and_tee "$LOG_DIR/railway-variables.log" railway variables --service monkey-coder

  echo -e "\nChecking required environment variables..."
  for var in OPENAI_API_KEY STRIPE_API_KEY DATABASE_URL SENTRY_DSN; do
    if railway variables --service monkey-coder | grep -q "^$var="; then
      echo "✅ $var: Present in Railway"
    else
      echo "⚠️  $var: Not found"
    fi
  done
else
  echo "⚠️  Cannot validate Railway environment variables (CLI not available)"
fi

# 3. Service status and logs
echo -e "\n📋 Step 3: Railway service status & logs"
BASE_URL="${RAILWAY_SERVICE_URL:-}"
if command -v railway >/dev/null 2>&1; then
  # Try status JSON to derive domain if not set
  STATUS_JSON_PATH="$LOG_DIR/railway-status.json"
  if railway status --json >/dev/null 2>&1; then
    railway status --json > "$STATUS_JSON_PATH" || true
    # Attempt common domain field paths
    DOMAIN=$(jq -r '..|.domain? // empty' "$STATUS_JSON_PATH" | head -1)
    if [ -z "$BASE_URL" ] && [ -n "$DOMAIN" ] && [[ "$DOMAIN" != "null" ]]; then
      BASE_URL="https://$DOMAIN"
    fi
  else
    run_and_tee "$LOG_DIR/railway-status.log" railway status
  fi

  echo -e "\nFetching latest build logs..."
  run_and_tee "$LOG_DIR/railway-build-logs.log" railway logs --service monkey-coder --build

  echo -e "\nFetching latest deployment logs..."
  run_and_tee "$LOG_DIR/railway-deployment-logs.log" railway logs --service monkey-coder --deployment

  echo -e "\nAnalyzing logs for error patterns..."
  if grep -E "(\b(5[0-9]{2})\b|ERROR|FATAL|crash|Traceback)" "$LOG_DIR/railway-build-logs.log" "$LOG_DIR/railway-deployment-logs.log" 2>/dev/null; then
    echo "❌ Errors found in Railway logs (see files above)"
  else
    echo "✅ No critical errors in latest logs"
  fi
else
  echo "⚠️  Cannot validate Railway service status (CLI not available)"
fi

# 4. Railway configuration validation
echo -e "\n📋 Step 4: Railway configuration files"
if [ -f "railpack.json" ]; then
  echo "✅ railpack.json found"
  if jq . railpack.json >/dev/null 2>&1; then
    echo "✅ railpack.json is valid JSON"
    jq . railpack.json > "$LOG_DIR/railpack-formatted.json"
  else
    echo "❌ railpack.json has invalid JSON syntax"
  fi

  # Extract values from current schema
  HEALTH_PATH=$(jq -r '.deploy.healthCheckPath // empty' railpack.json 2>/dev/null || echo "")
  START_CMD=$(jq -r '.deploy.startCommand // empty' railpack.json 2>/dev/null || echo "")
  PY_VER=$(jq -r '.build.packages.python // empty' railpack.json 2>/dev/null || echo "")
  NODE_VER=$(jq -r '.build.packages.node // empty' railpack.json 2>/dev/null || echo "")

  if [ -n "$HEALTH_PATH" ]; then
    echo "✅ Health check path configured: $HEALTH_PATH"
  else
    echo "❌ Health check path not configured in railpack.json (.deploy.healthCheckPath)"
  fi
  if [ -n "$START_CMD" ]; then
    echo "✅ Start command configured: $START_CMD"
  else
    echo "❌ Start command not configured in railpack.json (.deploy.startCommand)"
  fi
  if [ -n "$PY_VER" ]; then
    echo "✅ Python version: $PY_VER"
  else
    echo "⚠️  Python version not specified under .build.packages.python"
  fi
  if [ -n "$NODE_VER" ]; then
    echo "✅ Node.js version: $NODE_VER"
  else
    echo "⚠️  Node.js version not specified under .build.packages.node"
  fi
else
  echo "❌ railpack.json not found"
fi

# 5. Health endpoint testing
echo -e "\n📋 Step 5: Health endpoint validation"
HEALTH_PATH_DEFAULT="/health"
HEALTH_PATH_EFFECTIVE="${HEALTH_PATH:-$HEALTH_PATH_DEFAULT}"

if [ -z "$BASE_URL" ]; then
  # Fallback to known domain if status JSON didn't provide one
  BASE_URL="https://monkey-coder.up.railway.app"
fi

echo "Testing health endpoint: $BASE_URL$HEALTH_PATH_EFFECTIVE"
for method in GET HEAD; do
  echo "Testing $method $BASE_URL$HEALTH_PATH_EFFECTIVE..."
  curl -s -X "$method" -i "$BASE_URL$HEALTH_PATH_EFFECTIVE" | tee "$LOG_DIR/health-$method-test.log" >/dev/null || echo "$method test failed"
done

# 6. Database connectivity (if applicable)
echo -e "\n📋 Step 6: Database connectivity validation"
if command -v railway >/dev/null 2>&1; then
  if railway variables --service monkey-coder | grep -q "^DATABASE_URL="; then
    echo "✅ DATABASE_URL configured in Railway"
    if command -v psql >/dev/null 2>&1; then
      DB_URL=$(railway variables --service monkey-coder | awk -F'=' '/^DATABASE_URL=/{print $2}' || echo "")
      if [ -n "$DB_URL" ]; then
        echo "Testing database connectivity..."
        (psql "$DB_URL" -c "SELECT 1;" 2>&1 | tee "$LOG_DIR/database-test.log") || echo "Database connection failed"
      fi
    else
      echo "⚠️  psql not available for database testing"
    fi
  else
    echo "ℹ️  DATABASE_URL not configured"
  fi
fi

# 7. Performance and resource validation (best-effort)
echo -e "\n📋 Step 7: Performance validation"
if command -v railway >/dev/null 2>&1; then
  # Use deployment logs as a proxy for recent activity
  grep -Ei "(memory|cpu|performance)" "$LOG_DIR/railway-deployment-logs.log" | tail -10 > "$LOG_DIR/performance-metrics.log" || true
  if [ -s "$LOG_DIR/performance-metrics.log" ]; then
    echo "Recent performance metrics:"
    cat "$LOG_DIR/performance-metrics.log"
  else
    echo "ℹ️  No performance metrics found in recent logs"
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
- Health Check Path: $HEALTH_PATH_EFFECTIVE
- Python: ${PY_VER:-unknown}
- Node: ${NODE_VER:-unknown}

## Environment Variables (first 20)
$(if command -v railway >/dev/null 2>&1; then railway variables --service monkey-coder | head -20 | sed 's/^/- /'; else echo "- Railway CLI not available"; fi)

## Recent Error Patterns
```
$(grep -E "(\b(5[0-9]{2})\b|ERROR|FATAL|Traceback)" "$LOG_DIR/railway-build-logs.log" "$LOG_DIR/railway-deployment-logs.log" 2>/dev/null | tail -20 || echo "No recent errors found")
```

## Health Endpoint Response (GET)
```
$(grep -A 10 -m 1 "HTTP/" "$LOG_DIR/health-GET-test.log" 2>/dev/null | head -20 || echo "Health endpoint not responding")
```

## Recommended Actions
1. If 5xx/ERROR logs appear, inspect the referenced log files under $LOG_DIR
2. If env issues: verify all required variables via 'railway variables --service monkey-coder'
3. If health check fails: verify railpack.json deploy.startCommand and application boot
4. If database issues: validate DATABASE_URL and connectivity

## Files Generated
- railway-variables.log: Environment variables
- railway-status.json or railway-status.log: Service status
- railway-build-logs.log: Latest build logs
- railway-deployment-logs.log: Latest deployment logs
- health-*-test.log: Health endpoint tests
- performance-metrics.log: Performance data
EOF

echo "✅ Railway validation completed"
echo "📄 Full report saved to: $LOG_DIR/railway-validation-report.md"
echo ""
echo "Key commands for troubleshooting:"
echo "- railway logs --service monkey-coder --build"
echo "- railway logs --service monkey-coder --deployment"
echo "- railway variables --service monkey-coder"
echo "- railway status --json | jq '.'"
echo "- curl -i $BASE_URL$HEALTH_PATH_EFFECTIVE"