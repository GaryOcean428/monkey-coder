#!/bin/bash

# 🚀 Complete Railway Deployment Integration Script
# Integrates all Railway deployment tools with MCP framework
# Provides comprehensive deployment readiness checking and fixing

set -e

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$PROJECT_ROOT/railway_deployment_${TIMESTAMP}.log"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging function
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

log "${BLUE}🚀 Railway Deployment Integration Suite${NC}"
log "======================================="
log "Project: $(basename "$PROJECT_ROOT")"
log "Log file: $LOG_FILE"
log "Timestamp: $(date)"
log ""

cd "$PROJECT_ROOT"

# Function to check if tools exist
check_tools() {
    log "${YELLOW}1. Checking available Railway deployment tools...${NC}"
    
    TOOLS_AVAILABLE=0
    
    # Check MCP Railway deployment manager
    if [ -f "scripts/mcp-railway-deployment-manager.py" ]; then
        log "   ✅ MCP Railway Deployment Manager: Available"
        TOOLS_AVAILABLE=$((TOOLS_AVAILABLE + 1))
    else
        log "   ❌ MCP Railway Deployment Manager: Missing"
    fi
    
    # Check Railway auto-fix script
    if [ -f "scripts/railway-auto-fix.sh" ]; then
        log "   ✅ Railway Auto-Fix Script: Available"
        TOOLS_AVAILABLE=$((TOOLS_AVAILABLE + 1))
    else
        log "   ❌ Railway Auto-Fix Script: Missing"
    fi
    
    # Check standard validation script
    if [ -f "scripts/railway-cheatsheet-validation.sh" ]; then
        log "   ✅ Railway Cheatsheet Validation: Available"
        TOOLS_AVAILABLE=$((TOOLS_AVAILABLE + 1))
    else
        log "   ❌ Railway Cheatsheet Validation: Missing"
    fi
    
    # Check MCP integration
    if [ -f "packages/core/monkey_coder/mcp/railway_deployment_tool.py" ]; then
        log "   ✅ MCP Railway Integration: Available"
        TOOLS_AVAILABLE=$((TOOLS_AVAILABLE + 1))
    else
        log "   ❌ MCP Railway Integration: Missing"
    fi
    
    log "   📊 Tools Available: $TOOLS_AVAILABLE/4"
    log ""
}

# Function to run MCP-enhanced validation
run_mcp_validation() {
    log "${YELLOW}2. Running MCP-Enhanced Railway Validation...${NC}"
    
    if [ -f "scripts/mcp-railway-deployment-manager.py" ]; then
        if python scripts/mcp-railway-deployment-manager.py >> "$LOG_FILE" 2>&1; then
            log "   ✅ MCP validation completed successfully"
            return 0
        else
            log "   ❌ MCP validation found issues (see log for details)"
            return 1
        fi
    else
        log "   ⚠️  MCP validation not available - using standard validation"
        return 2
    fi
}

# Function to run standard validation
run_standard_validation() {
    log "${YELLOW}3. Running Standard Railway Validation...${NC}"
    
    if [ -f "scripts/railway-cheatsheet-validation.sh" ]; then
        if ./scripts/railway-cheatsheet-validation.sh >> "$LOG_FILE" 2>&1; then
            log "   ✅ Standard validation completed successfully"
            return 0
        else
            log "   ❌ Standard validation found issues"
            return 1
        fi
    else
        log "   ❌ Standard validation script not available"
        return 1
    fi
}

# Function to apply auto-fixes
apply_auto_fixes() {
    log "${YELLOW}4. Applying Railway Auto-Fixes...${NC}"
    
    if [ -f "scripts/railway-auto-fix.sh" ]; then
        if ./scripts/railway-auto-fix.sh >> "$LOG_FILE" 2>&1; then
            log "   ✅ Auto-fixes applied successfully"
            return 0
        else
            log "   ❌ Auto-fixes failed (check log for details)"
            return 1
        fi
    else
        log "   ⚠️  Auto-fix script not available"
        return 1
    fi
}

# Function to create deployment summary
create_deployment_summary() {
    log "${YELLOW}5. Creating Deployment Summary...${NC}"
    
    SUMMARY_FILE="$PROJECT_ROOT/RAILWAY_DEPLOYMENT_SUMMARY.md"
    
    cat > "$SUMMARY_FILE" << EOF
# Railway Deployment Summary

Generated: $(date)
Project: $(basename "$PROJECT_ROOT")

## Tools Available

EOF
    
    if [ -f "scripts/mcp-railway-deployment-manager.py" ]; then
        echo "- ✅ MCP Railway Deployment Manager" >> "$SUMMARY_FILE"
    else
        echo "- ❌ MCP Railway Deployment Manager" >> "$SUMMARY_FILE"
    fi
    
    if [ -f "scripts/railway-auto-fix.sh" ]; then
        echo "- ✅ Railway Auto-Fix Script" >> "$SUMMARY_FILE"
    else
        echo "- ❌ Railway Auto-Fix Script" >> "$SUMMARY_FILE"
    fi
    
    if [ -f "packages/core/monkey_coder/mcp/railway_deployment_tool.py" ]; then
        echo "- ✅ MCP Railway Integration" >> "$SUMMARY_FILE"
    else
        echo "- ❌ MCP Railway Integration" >> "$SUMMARY_FILE"
    fi
    
    cat >> "$SUMMARY_FILE" << EOF

## Railway Deployment Checklist

Based on the Railway Deployment Master Cheat Sheet:

### Build System (Issue 1)
- [ ] Only railpack.json exists (no competing build files)
- [ ] railpack.json has valid JSON syntax
- [ ] Required fields are present (version, metadata, build, deploy)

### PORT Binding (Issue 2)  
- [ ] Application uses process.env.PORT (not hardcoded ports)
- [ ] Application binds to 0.0.0.0 (not localhost/127.0.0.1)
- [ ] Start command doesn't hardcode ports

### Health Checks (Issue 5)
- [ ] Health endpoint implemented (/health returning 200)
- [ ] healthCheckPath configured in railpack.json
- [ ] Health check timeout set appropriately (300s recommended)

### Reference Variables (Issue 4)
- [ ] Use RAILWAY_PUBLIC_DOMAIN not PORT references
- [ ] Use RAILWAY_PRIVATE_DOMAIN for internal communication
- [ ] No invalid variable references in configuration

### Monorepo Structure (Issue 6)
- [ ] Services properly configured if monorepo
- [ ] No conflicting service configurations
- [ ] Clear separation of service concerns

## Quick Commands

\`\`\`bash
# Run comprehensive validation
./scripts/mcp-railway-deployment-manager.py

# Apply automatic fixes
./scripts/railway-auto-fix.sh

# Check deployment readiness
./check-railway-readiness.sh

# Deploy to Railway
railway up
\`\`\`

## Links

- [Railway Deployment Cheat Sheet](./CLAUDE.md#railway-deployment-master-cheat-sheet)
- [Railway Documentation](https://docs.railway.app/)
- [railpack.json Schema](https://schema.railpack.com/)
EOF
    
    log "   ✅ Deployment summary created: $SUMMARY_FILE"
}

# Function to show next steps
show_next_steps() {
    log "${CYAN}🎯 Next Steps:${NC}"
    
    if [ -f "check-railway-readiness.sh" ]; then
        log "   1. Run final readiness check: ./check-railway-readiness.sh"
    fi
    
    log "   2. Test locally: railway run python run_server.py"
    log "   3. Deploy to Railway: railway up"
    log "   4. Monitor deployment health"
    log "   5. Review deployment summary: RAILWAY_DEPLOYMENT_SUMMARY.md"
    log ""
    log "${GREEN}✅ Railway deployment integration completed!${NC}"
    log "   📋 Full log available at: $LOG_FILE"
}

# Main execution flow
main() {
    # Check available tools
    check_tools
    
    # Run MCP validation if available, otherwise standard validation
    MCP_RESULT=1
    if run_mcp_validation; then
        MCP_RESULT=0
    elif [ $? -eq 2 ]; then
        # MCP not available, try standard validation
        if run_standard_validation; then
            MCP_RESULT=0
        fi
    fi
    
    # If validation found issues, try auto-fixes
    if [ $MCP_RESULT -ne 0 ]; then
        log "${YELLOW}⚠️  Issues detected - attempting auto-fixes...${NC}"
        if apply_auto_fixes; then
            log "${GREEN}✅ Auto-fixes applied - re-running validation...${NC}"
            # Re-run validation after fixes
            if run_mcp_validation || [ $? -eq 2 ] && run_standard_validation; then
                MCP_RESULT=0
                log "${GREEN}✅ Validation passed after auto-fixes${NC}"
            else
                log "${RED}❌ Issues remain after auto-fixes${NC}"
            fi
        fi
    fi
    
    # Create deployment summary
    create_deployment_summary
    
    # Show next steps
    show_next_steps
    
    # Final status
    if [ $MCP_RESULT -eq 0 ]; then
        log ""
        log "${GREEN}🎉 RAILWAY DEPLOYMENT READY!${NC}"
        exit 0
    else
        log ""
        log "${RED}🛑 DEPLOYMENT BLOCKED - Issues need resolution${NC}"
        exit 1
    fi
}

# Execute main function
main "$@"