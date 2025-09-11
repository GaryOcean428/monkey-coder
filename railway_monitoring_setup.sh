#!/bin/bash
# railway_monitoring_setup.sh
# 
# Set up monitoring and notification hooks for Railway deployment

set -e

echo "📊 Railway Deployment Monitoring Setup"
echo "======================================"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DEPLOYMENT_URL="https://coder.fastmonkey.au"
WEBHOOK_URL=${RAILWAY_WEBHOOK_URL:-""}

# Function to check deployment health
check_deployment_health() {
    local url="$1"
    local response
    
    echo -e "${BLUE}Checking deployment health at: $url${NC}"
    
    if response=$(curl -s -w "%{http_code}" --max-time 30 "$url/health" 2>/dev/null); then
        local status_code="${response: -3}"
        local response_body="${response%???}"
        
        if [[ "$status_code" == "200" ]]; then
            local health_status=$(echo "$response_body" | jq -r '.status // "unknown"' 2>/dev/null)
            if [[ "$health_status" == "healthy" ]]; then
                echo -e "${GREEN}✅ Deployment is healthy${NC}"
                return 0
            else
                echo -e "${YELLOW}⚠️ Deployment status: $health_status${NC}"
                return 1
            fi
        else
            echo -e "${YELLOW}⚠️ Health endpoint returned status: $status_code${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️ Health endpoint is unreachable${NC}"
        return 1
    fi
}

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