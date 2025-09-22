#!/bin/bash
# railway_monitoring_setup.sh
# 
# Enhanced Railway deployment monitoring and alerting setup
# Includes webhook monitoring, health checks, automated rollback, and frontend asset monitoring

set -euo pipefail

echo "📊 Railway Deployment Monitoring & Alerting Setup"
echo "=================================================="

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_URL="https://coder.fastmonkey.au"
WEBHOOK_URL=${RAILWAY_WEBHOOK_URL:-""}
HEALTH_CHECK_TIMEOUT=30
STARTUP_TIMEOUT=300

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

# Function to check deployment health with detailed output
check_deployment_health() {
    local url="$1"
    local endpoint="${2:-/health}"
    
    log "Checking deployment health at: $url$endpoint"
    
    if response=$(curl -s -w "%{http_code}" --max-time $HEALTH_CHECK_TIMEOUT "$url$endpoint" 2>/dev/null); then
        local status_code="${response: -3}"
        local response_body="${response%???}"
        
        if [[ "$status_code" == "200" ]]; then
            local health_status=$(echo "$response_body" | jq -r '.status // "unknown"' 2>/dev/null)
            if [[ "$health_status" == "healthy" ]]; then
                success "✅ $endpoint is healthy"
                return 0
            else
                warning "⚠️ $endpoint status: $health_status"
                return 1
            fi
        else
            warning "⚠️ $endpoint returned status: $status_code"
            return 1
        fi
    else
        warning "⚠️ $endpoint is unreachable"
        return 1
    fi
}

# Function to check frontend assets
check_frontend_assets() {
    local url="$1"
    
    log "Checking frontend asset availability..."
    
    # Test critical frontend assets
    local critical_assets=("/" "/favicon.ico")
    local assets_ok=0
    local total_assets=${#critical_assets[@]}
    
    for asset in "${critical_assets[@]}"; do
        if curl -sf --max-time 10 "$url$asset" >/dev/null 2>&1; then
            success "✅ Asset available: $asset"
            ((assets_ok++))
        else
            warning "⚠️ Asset unavailable: $asset"
        fi
    done
    
    if [[ $assets_ok -eq $total_assets ]]; then
        success "✅ All critical frontend assets are available"
        return 0
    else
        warning "⚠️ $((total_assets - assets_ok))/$total_assets critical assets unavailable"
        return 1
    fi
}

# Function to verify API endpoints
check_api_endpoints() {
    local url="$1"
    
    log "Checking API endpoint availability..."
    
    local api_endpoints=(
        "/health"
        "/healthz"
        "/health/readiness"
        "/api/v1/railway/metrics"
        "/api/v1/railway/dashboard/data"
        "/api/v1/railway/frontend/status"
    )
    
    local endpoints_ok=0
    
    for endpoint in "${api_endpoints[@]}"; do
        if curl -sf --max-time 10 "$url$endpoint" >/dev/null 2>&1; then
            success "✅ API endpoint available: $endpoint"
            ((endpoints_ok++))
        else
            warning "⚠️ API endpoint unavailable: $endpoint"
        fi
    done
    
    if [[ $endpoints_ok -gt 0 ]]; then
        success "✅ $endpoints_ok/${#api_endpoints[@]} API endpoints are available"
        return 0
    else
        error "❌ No API endpoints are responding"
        return 1
    fi
}

# Function to send webhook notification
send_webhook_notification() {
    local status="$1"
    local message="$2"
    local component="${3:-deployment}"
    
    if [[ -n "$WEBHOOK_URL" ]]; then
        log "📡 Sending webhook notification..."
        
        local color="good"
        local emoji="✅"
        
        case "$status" in
            "unhealthy"|"failed"|"error")
                color="danger"
                emoji="🚨"
                ;;
            "degraded"|"warning")
                color="warning"
                emoji="⚠️"
                ;;
        esac
        
        local payload=$(cat <<EOF
{
    "text": "$emoji Railway $component Alert",
    "attachments": [
        {
            "color": "$color",
            "fields": [
                {
                    "title": "Component",
                    "value": "$component",
                    "short": true
                },
                {
                    "title": "Status",
                    "value": "$status",
                    "short": true
                },
                {
                    "title": "URL",
                    "value": "$DEPLOYMENT_URL",
                    "short": true
                },
                {
                    "title": "Message",
                    "value": "$message",
                    "short": false
                },
                {
                    "title": "Timestamp",
                    "value": "$(date -u +"%Y-%m-%d %H:%M:%S UTC")",
                    "short": true
                }
            ]
        }
    ]
}
EOF
        )
        
        if curl -X POST \
             -H "Content-Type: application/json" \
             -d "$payload" \
             "$WEBHOOK_URL" \
             --silent \
             --max-time 10 \
             > /dev/null; then
            success "✅ Webhook notification sent"
        else
            warning "⚠️ Failed to send webhook notification"
        fi
    else
        log "ℹ️ No webhook URL configured (set RAILWAY_WEBHOOK_URL)"
    fi
}

# Function to test Railway monitoring endpoints
test_monitoring_endpoints() {
    local url="$1"
    
    log "Testing Railway monitoring endpoints..."
    
    # Test webhook endpoint (should return 405 for GET)
    if curl -s -o /dev/null -w "%{http_code}" "$url/api/v1/railway/webhook" | grep -q "405"; then
        success "✅ Webhook endpoint is accessible"
    else
        warning "⚠️ Webhook endpoint may not be configured"
    fi
    
    # Test metrics endpoint
    if curl -sf "$url/api/v1/railway/metrics" >/dev/null 2>&1; then
        success "✅ Metrics endpoint is responsive"
    else
        warning "⚠️ Metrics endpoint unavailable"
    fi
    
    # Test dashboard endpoint
    if curl -sf "$url/api/v1/railway/dashboard/data" >/dev/null 2>&1; then
        success "✅ Dashboard endpoint is responsive"
    else
        warning "⚠️ Dashboard endpoint unavailable"
    fi
    
    # Test rollback status endpoint
    if curl -sf "$url/api/v1/railway/rollback/status" >/dev/null 2>&1; then
        success "✅ Rollback management is available"
    else
        warning "⚠️ Rollback management unavailable"
    fi
    
    # Test frontend monitoring endpoint
    if curl -sf "$url/api/v1/railway/frontend/status" >/dev/null 2>&1; then
        success "✅ Frontend monitoring is available"
    else
        warning "⚠️ Frontend monitoring unavailable"
    fi
}

# Function to create monitoring configuration
create_monitoring_config() {
    log "Creating monitoring configuration..."
    
    # Create monitoring data directory
    mkdir -p data
    
    # Create monitoring configuration file
    cat > data/monitoring_config.json << EOF
{
    "deployment_url": "$DEPLOYMENT_URL",
    "webhook_url": "$WEBHOOK_URL",
    "health_check_timeout": $HEALTH_CHECK_TIMEOUT,
    "startup_timeout": $STARTUP_TIMEOUT,
    "monitoring_enabled": true,
    "rollback_enabled": true,
    "frontend_monitoring_enabled": true,
    "alert_thresholds": {
        "consecutive_failures": 3,
        "response_time_threshold": 30,
        "crash_threshold": 3,
        "crash_window": 600
    },
    "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "created_by": "railway_monitoring_setup.sh"
}
EOF
    
    success "✅ Monitoring configuration created"
}

# Function to create deployment hooks
create_deployment_hooks() {
    log "Creating deployment validation hooks..."
    
    # Create pre-deployment validation
    cat > /tmp/railway_pre_deploy_hook.sh << 'EOF'
#!/bin/bash
# Pre-deployment validation hook

set -euo pipefail

echo "🔍 Pre-deployment validation..."

# Validate railpack.json
if ! jq empty railpack.json 2>/dev/null; then
    echo "❌ Invalid railpack.json syntax"
    exit 1
fi

# Check for required files
required_files=(
    "run_server.py"
    "packages/core/monkey_coder/app/main.py"
)

for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "❌ Required file missing: $file"
        exit 1
    fi
done

# Run path verification
if [[ -x "scripts/railway_path_verification.sh" ]]; then
    ./scripts/railway_path_verification.sh
else
    echo "⚠️ Path verification script not found"
fi

echo "✅ Pre-deployment validation passed"
EOF

    # Create post-deployment validation
    cat > /tmp/railway_post_deploy_hook.sh << 'EOF'
#!/bin/bash
# Post-deployment validation hook

set -euo pipefail

DEPLOYMENT_URL="https://coder.fastmonkey.au"
MAX_RETRIES=10
RETRY_INTERVAL=30

echo "🚀 Post-deployment validation..."

for i in $(seq 1 $MAX_RETRIES); do
    echo "Attempt $i/$MAX_RETRIES: Testing deployment..."
    
    # Test health endpoint
    if curl -f -s "$DEPLOYMENT_URL/health" | jq -r '.status' | grep -q "healthy"; then
        echo "✅ Health check passed"
        
        # Test API endpoints
        if curl -f -s "$DEPLOYMENT_URL/api/v1/railway/metrics" >/dev/null; then
            echo "✅ API endpoints responsive"
            
            # Test frontend assets
            if curl -f -s "$DEPLOYMENT_URL/" >/dev/null; then
                echo "✅ Frontend assets accessible"
                
                # Test rollback system
                if curl -f -s "$DEPLOYMENT_URL/api/v1/railway/rollback/status" >/dev/null; then
                    echo "✅ Rollback system operational"
                    echo "🎉 Deployment validation successful!"
                    
                    # Send success notification
                    if [[ -n "${RAILWAY_WEBHOOK_URL:-}" ]]; then
                        curl -X POST \
                             -H "Content-Type: application/json" \
                             -d '{"text":"🎉 Railway deployment successful! All validation checks passed."}' \
                             "$RAILWAY_WEBHOOK_URL" \
                             --silent > /dev/null
                    fi
                    
                    exit 0
                fi
            fi
        fi
    fi
    
    if [[ $i -lt $MAX_RETRIES ]]; then
        echo "⏳ Waiting ${RETRY_INTERVAL}s before retry..."
        sleep $RETRY_INTERVAL
    fi
done

echo "❌ Deployment validation failed after $MAX_RETRIES attempts"

# Send failure notification
if [[ -n "${RAILWAY_WEBHOOK_URL:-}" ]]; then
    curl -X POST \
         -H "Content-Type: application/json" \
         -d '{"text":"🚨 Railway deployment failed! Health checks did not pass within expected timeframe."}' \
         "$RAILWAY_WEBHOOK_URL" \
         --silent > /dev/null
fi

exit 1
EOF

    chmod +x /tmp/railway_pre_deploy_hook.sh
    chmod +x /tmp/railway_post_deploy_hook.sh
    
    success "✅ Deployment hooks created:"
    success "   Pre-deploy: /tmp/railway_pre_deploy_hook.sh"
    success "   Post-deploy: /tmp/railway_post_deploy_hook.sh"
}

# Function to generate status badge
generate_status_badge() {
    local status="$1"
    local badge_file="data/deployment_status.svg"
    
    local color="brightgreen"
    case "$status" in
        "unhealthy"|"failed") color="red" ;;
        "degraded"|"warning") color="orange" ;;
    esac
    
    # Create simple SVG badge
    cat > "$badge_file" << EOF
<svg xmlns="http://www.w3.org/2000/svg" width="104" height="20">
    <linearGradient id="b" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <mask id="a">
        <rect width="104" height="20" rx="3" fill="#fff"/>
    </mask>
    <g mask="url(#a)">
        <path fill="#555" d="M0 0h63v20H0z"/>
        <path fill="$color" d="M63 0h41v20H63z"/>
        <path fill="url(#b)" d="M0 0h104v20H0z"/>
    </g>
    <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
        <text x="31.5" y="15" fill="#010101" fill-opacity=".3">Railway</text>
        <text x="31.5" y="14">Railway</text>
        <text x="82.5" y="15" fill="#010101" fill-opacity=".3">$status</text>
        <text x="82.5" y="14">$status</text>
    </g>
</svg>
EOF
    
    success "✅ Status badge generated: $badge_file"
}

# Main execution function
main() {
    log "Starting Railway monitoring and alerting setup..."
    log "=================================================="
    
    overall_health="healthy"
    
    # Check deployment health
    if check_deployment_health "$DEPLOYMENT_URL"; then
        send_webhook_notification "healthy" "All health checks passed" "health"
    else
        overall_health="degraded"
        send_webhook_notification "degraded" "Health check warnings detected" "health"
    fi
    
    # Check frontend assets
    if check_frontend_assets "$DEPLOYMENT_URL"; then
        send_webhook_notification "healthy" "Frontend assets accessible" "frontend"
    else
        overall_health="degraded"
        send_webhook_notification "degraded" "Frontend asset issues detected" "frontend"
    fi
    
    # Check API endpoints
    if check_api_endpoints "$DEPLOYMENT_URL"; then
        send_webhook_notification "healthy" "API endpoints responsive" "api"
    else
        overall_health="unhealthy"
        send_webhook_notification "unhealthy" "API endpoint failures detected" "api"
    fi
    
    # Test monitoring endpoints
    test_monitoring_endpoints "$DEPLOYMENT_URL"
    
    # Create monitoring configuration
    create_monitoring_config
    
    # Create deployment hooks
    create_deployment_hooks
    
    # Generate status badge
    generate_status_badge "$overall_health"
    
    log "=================================================="
    if [[ "$overall_health" == "healthy" ]]; then
        success "✅ Railway monitoring setup completed successfully!"
        success "   All systems operational and monitoring active"
    elif [[ "$overall_health" == "degraded" ]]; then
        warning "⚠️ Railway monitoring setup completed with warnings"
        warning "   Some components may need attention"
    else
        error "❌ Railway monitoring setup completed with errors"
        error "   Critical components need immediate attention"
    fi
    
    log ""
    log "📊 Monitoring Features Enabled:"
    log "   • Deployment webhooks and metrics tracking"
    log "   • Health check monitoring dashboard"
    log "   • Automated rollback on failures"
    log "   • Frontend asset monitoring"
    log "   • Real-time alerting via webhooks"
    log ""
    log "🔗 Access monitoring dashboard at: $DEPLOYMENT_URL/api/v1/railway/dashboard"
    log "📈 View metrics at: $DEPLOYMENT_URL/api/v1/railway/metrics"
    log ""
    log "Configuration saved to: data/monitoring_config.json"
    
    exit 0
}

# Help function
show_help() {
    cat << EOF
Railway Deployment Monitoring & Alerting Setup

Usage: $0 [OPTIONS]

OPTIONS:
    -h, --help              Show this help message
    --url URL               Override deployment URL (default: https://coder.fastmonkey.au)
    --webhook-url URL       Set webhook notification URL
    --health-timeout SEC    Health check timeout in seconds (default: 30)
    --startup-timeout SEC   Startup timeout in seconds (default: 300)

ENVIRONMENT VARIABLES:
    RAILWAY_WEBHOOK_URL     Webhook URL for notifications
    RAILWAY_DEPLOYMENT_URL  Deployment URL to monitor

EXAMPLES:
    # Basic monitoring setup
    $0

    # Setup with custom webhook
    RAILWAY_WEBHOOK_URL=https://hooks.slack.com/... $0

    # Setup with custom deployment URL
    $0 --url https://my-app.railway.app

    # Help
    $0 --help

This script sets up comprehensive monitoring for Railway deployments including:
- Deployment success/failure tracking
- Health check monitoring
- Automated rollback capabilities  
- Frontend asset monitoring
- Real-time alerting

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --url)
            DEPLOYMENT_URL="$2"
            shift 2
            ;;
        --webhook-url)
            WEBHOOK_URL="$2"
            shift 2
            ;;
        --health-timeout)
            HEALTH_CHECK_TIMEOUT="$2"
            shift 2
            ;;
        --startup-timeout)
            STARTUP_TIMEOUT="$2"
            shift 2
            ;;
        *)
            error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Run main function
main "$@"

# Function to send webhook notification
send_webhook_notification() {
    local status="$1"
    local message="$2"
    
    if [[ -n "$WEBHOOK_URL" ]]; then
        echo "📡 Sending webhook notification..."
        
        local payload=$(cat <<EOF
{
    "text": "🚂 Railway Deployment Alert",
    "attachments": [
        {
            "color": "$([[ "$status" == "healthy" ]] && echo "good" || echo "warning")",
            "fields": [
                {
                    "title": "Status",
                    "value": "$status",
                    "short": true
                },
                {
                    "title": "URL",
                    "value": "$DEPLOYMENT_URL",
                    "short": true
                },
                {
                    "title": "Message",
                    "value": "$message",
                    "short": false
                },
                {
                    "title": "Timestamp",
                    "value": "$(date -u +"%Y-%m-%d %H:%M:%S UTC")",
                    "short": true
                }
            ]
        }
    ]
}
EOF
        )
        
        curl -X POST \
             -H "Content-Type: application/json" \
             -d "$payload" \
             "$WEBHOOK_URL" \
             --silent \
             > /dev/null
        
        echo "✅ Webhook notification sent"
    else
        echo "ℹ️ No webhook URL configured (set RAILWAY_WEBHOOK_URL)"
    fi
}

# Function to generate status badge
generate_status_badge() {
    local status="$1"
    local color="$([[ "$status" == "healthy" ]] && echo "brightgreen" || echo "yellow")"
    
    echo "🏷️ Generating status badge..."
    
    # Create badge URL for shields.io
    local badge_url="https://img.shields.io/badge/Railway-$status-$color?style=flat-square&logo=railway"
    
    # Create badge markdown
    local badge_markdown="[![Railway Deployment]($badge_url)]($DEPLOYMENT_URL/health)"
    
    echo "Badge URL: $badge_url"
    echo "Badge Markdown: $badge_markdown"
    
    # Save to file for README inclusion
    echo "$badge_markdown" > /tmp/railway_status_badge.md
    echo "✅ Badge saved to /tmp/railway_status_badge.md"
}

# Function to check and update README with status badge
update_readme_badge() {
    local readme_file="README.md"
    
    if [[ -f "$readme_file" ]]; then
        echo "📝 Updating README with status badge..."
        
        # Read badge markdown
        local badge_markdown
        if [[ -f "/tmp/railway_status_badge.md" ]]; then
            badge_markdown=$(cat /tmp/railway_status_badge.md)
        else
            badge_markdown="[![Railway Deployment](https://img.shields.io/badge/Railway-unknown-lightgrey?style=flat-square&logo=railway)]($DEPLOYMENT_URL/health)"
        fi
        
        # Check if badge already exists
        if grep -q "Railway Deployment" "$readme_file"; then
            echo "Updating existing badge..."
            # Replace existing badge
            sed -i.bak "s|!\[Railway Deployment\].*|$badge_markdown|g" "$readme_file"
        else
            echo "Adding new badge..."
            # Add badge after first heading
            sed -i.bak "1,/^#/ s|^#.*|&\n\n$badge_markdown|" "$readme_file"
        fi
        
        echo "✅ README updated with deployment status badge"
    else
        echo "⚠️ README.md not found"
    fi
}

# Function to create uptime monitoring script
create_uptime_monitor() {
    echo "⏰ Creating uptime monitoring script..."
    
    cat > /tmp/railway_uptime_monitor.sh << 'EOF'
#!/bin/bash
# Uptime monitoring script for Railway deployment

DEPLOYMENT_URL="https://coder.fastmonkey.au"
CHECK_INTERVAL=${CHECK_INTERVAL:-300}  # 5 minutes
LOG_FILE="/tmp/railway_uptime.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_uptime() {
    local start_time=$(date +%s)
    
    if curl -f -s "$DEPLOYMENT_URL/health" > /dev/null 2>&1; then
        local end_time=$(date +%s)
        local response_time=$((end_time - start_time))
        
        log_message "✅ UP - Response time: ${response_time}s"
        return 0
    else
        log_message "❌ DOWN - Health check failed"
        return 1
    fi
}

# Main monitoring loop
log_message "🚂 Starting Railway uptime monitoring..."
log_message "Checking: $DEPLOYMENT_URL"
log_message "Interval: ${CHECK_INTERVAL}s"

while true; do
    check_uptime
    
    # If health check fails, wait shorter interval and retry
    if [[ $? -ne 0 ]]; then
        log_message "Retrying in 60 seconds..."
        sleep 60
        check_uptime
    fi
    
    sleep "$CHECK_INTERVAL"
done
EOF

    chmod +x /tmp/railway_uptime_monitor.sh
    echo "✅ Uptime monitor created: /tmp/railway_uptime_monitor.sh"
    echo "   Run with: /tmp/railway_uptime_monitor.sh &"
}

# Function to create Railway deployment hooks
create_deployment_hooks() {
    echo "🪝 Creating Railway deployment hooks..."
    
    # Create pre-deployment validation
    cat > /tmp/railway_pre_deploy_hook.sh << 'EOF'
#!/bin/bash
# Pre-deployment validation hook

echo "🔍 Pre-deployment validation..."

# Validate railpack.json
if ! jq empty railpack.json 2>/dev/null; then
    echo "❌ Invalid railpack.json syntax"
    exit 1
fi

# Check for required files
required_files=(
    "run_server.py"
    "packages/core/monkey_coder/app/main.py"
    "packages/web/out/index.html"
)

for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "❌ Required file missing: $file"
        exit 1
    fi
done

echo "✅ Pre-deployment validation passed"
EOF

    # Create post-deployment validation
    cat > /tmp/railway_post_deploy_hook.sh << 'EOF'
#!/bin/bash
# Post-deployment validation hook

DEPLOYMENT_URL="https://coder.fastmonkey.au"
MAX_RETRIES=10
RETRY_INTERVAL=30

echo "🚀 Post-deployment validation..."

for i in $(seq 1 $MAX_RETRIES); do
    echo "Attempt $i/$MAX_RETRIES: Testing deployment..."
    
    if curl -f -s "$DEPLOYMENT_URL/health" | jq -r '.status' | grep -q "healthy"; then
        echo "✅ Deployment validation passed!"
        
        # Send success notification
        if [[ -n "$RAILWAY_WEBHOOK_URL" ]]; then
            curl -X POST \
                 -H "Content-Type: application/json" \
                 -d '{"text":"🎉 Railway deployment successful! All health checks passed."}' \
                 "$RAILWAY_WEBHOOK_URL" \
                 --silent > /dev/null
        fi
        
        exit 0
    fi
    
    if [[ $i -lt $MAX_RETRIES ]]; then
        echo "⏳ Waiting ${RETRY_INTERVAL}s before retry..."
        sleep $RETRY_INTERVAL
    fi
done

echo "❌ Deployment validation failed after $MAX_RETRIES attempts"

# Send failure notification
if [[ -n "$RAILWAY_WEBHOOK_URL" ]]; then
    curl -X POST \
         -H "Content-Type: application/json" \
         -d '{"text":"🚨 Railway deployment failed! Health checks did not pass."}' \
         "$RAILWAY_WEBHOOK_URL" \
         --silent > /dev/null
fi

exit 1
EOF

    chmod +x /tmp/railway_pre_deploy_hook.sh
    chmod +x /tmp/railway_post_deploy_hook.sh
    
    echo "✅ Deployment hooks created:"
    echo "   Pre-deploy: /tmp/railway_pre_deploy_hook.sh"
    echo "   Post-deploy: /tmp/railway_post_deploy_hook.sh"
}

# Main execution
main() {
    echo "Starting Railway monitoring setup..."
    
    # Check deployment health
    if check_deployment_health "$DEPLOYMENT_URL"; then
        local status="healthy"
        local message="All systems operational"
    else
        local status="unhealthy"
        local message="Health check failed - requires attention"
    fi
    
    # Generate status badge
    generate_status_badge "$status"
    
    # Update README if available
    if [[ -f "README.md" ]]; then
        update_readme_badge
    fi
    
    # Send webhook notification
    send_webhook_notification "$status" "$message"
    
    # Create monitoring tools
    create_uptime_monitor
    create_deployment_hooks
    
    echo ""
    echo "🎉 Railway monitoring setup complete!"
    echo ""
    echo "📋 Available tools:"
    echo "   • Status verification: ./verify_railway_deployment.sh"
    echo "   • Uptime monitoring: /tmp/railway_uptime_monitor.sh"
    echo "   • Pre-deploy hook: /tmp/railway_pre_deploy_hook.sh"
    echo "   • Post-deploy hook: /tmp/railway_post_deploy_hook.sh"
    echo ""
    echo "🔧 Railway CLI commands:"
    echo "   • Check logs: railway logs --service monkey-coder --tail"
    echo "   • Monitor status: railway status"
    echo "   • Force redeploy: railway up --force"
    echo "   • Check variables: railway variables"
    echo ""
    echo "🌐 Deployment URL: $DEPLOYMENT_URL"
    echo "📊 Health check: $DEPLOYMENT_URL/health"
    echo "📈 Metrics: $DEPLOYMENT_URL/metrics"
    echo "📚 API docs: $DEPLOYMENT_URL/api/docs"
}

# Show usage if help requested
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo "Railway Monitoring Setup Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Environment Variables:"
    echo "  RAILWAY_WEBHOOK_URL   Webhook URL for notifications"
    echo "  CHECK_INTERVAL        Uptime check interval in seconds (default: 300)"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Basic setup"
    echo "  RAILWAY_WEBHOOK_URL=https://... $0    # Setup with webhook notifications"
    exit 0
fi

# Run main function
main "$@"