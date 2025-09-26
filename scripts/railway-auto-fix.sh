#!/bin/bash

# 🚀 Railway Deployment Auto-Fix Script
# Automatically resolves common Railway deployment issues based on the cheat sheet

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ISSUES_FIXED=0
WARNINGS=0

echo -e "${BLUE}🚀 Railway Deployment Auto-Fix Script${NC}"
echo "====================================="
echo "Project: $(basename "$PROJECT_ROOT")"
echo "Working Directory: $PROJECT_ROOT"
echo ""

cd "$PROJECT_ROOT"

# Function to log actions
log_action() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    WARNINGS=$((WARNINGS + 1))
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to fix build system conflicts (ISSUE 1)
fix_build_conflicts() {
    echo -e "\n${YELLOW}1. Fixing Build System Conflicts...${NC}"
    
    COMPETING_FILES=()
    
    # Check for competing build files (excluding services directory)
    if [ -f "Dockerfile" ] && [ ! -d "services" ] || [ -f "Dockerfile" ] && [ "$(dirname $(find . -maxdepth 1 -name "Dockerfile"))" = "." ]; then
        COMPETING_FILES+=("Dockerfile")
    fi
    if [ -f "railway.toml" ]; then
        COMPETING_FILES+=("railway.toml")
    fi
    if [ -f "railway.json" ]; then
        COMPETING_FILES+=("railway.json")
    fi
    if [ -f "nixpacks.toml" ]; then
        COMPETING_FILES+=("nixpacks.toml")
    fi
    
    if [ ${#COMPETING_FILES[@]} -gt 0 ]; then
        echo "Found competing build files: ${COMPETING_FILES[*]}"
        
        # Backup competing files before removal
        BACKUP_DIR="./railway-backup-$(date +%Y%m%d-%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        for file in "${COMPETING_FILES[@]}"; do
            if [ -f "$file" ]; then
                cp "$file" "$BACKUP_DIR/"
                rm "$file"
                log_action "Removed $file (backed up to $BACKUP_DIR)"
                ISSUES_FIXED=$((ISSUES_FIXED + 1))
            fi
        done
    else
        log_action "No competing build files found"
    fi
    
    # Ensure railpack.json exists
    if [ ! -f "railpack.json" ]; then
        log_error "railpack.json not found!"
        echo "Creating basic railpack.json template..."
        cat > railpack.json << 'EOF'
{
  "$schema": "https://schema.railpack.com",
  "version": "1",
  "metadata": {
    "name": "monkey-coder",
    "description": "AI-powered code generation and analysis platform"
  },
  "build": {
    "provider": "python",
    "packages": {
      "python": "3.12.11",
      "node": "20"
    },
    "steps": {
      "install": {
        "commands": [
          "python -m venv /app/.venv",
          "/app/.venv/bin/pip install --upgrade pip setuptools wheel",
          "/app/.venv/bin/pip install -r requirements.txt"
        ]
      }
    }
  },
  "deploy": {
    "startCommand": "/app/.venv/bin/python run_server.py",
    "healthCheckPath": "/health",
    "healthCheckTimeout": 300
  }
}
EOF
        log_action "Created basic railpack.json template"
        ISSUES_FIXED=$((ISSUES_FIXED + 1))
    else
        # Validate JSON syntax
        if jq '.' railpack.json > /dev/null 2>&1; then
            log_action "railpack.json syntax is valid"
        else
            log_error "railpack.json has invalid JSON syntax!"
            echo "Please fix the JSON syntax manually or recreate the file"
        fi
    fi
}

# Function to fix PORT binding issues (ISSUE 2)  
fix_port_binding() {
    echo -e "\n${YELLOW}2. Fixing PORT Binding Issues...${NC}"
    
    # Check run_server.py for proper PORT usage
    if [ -f "run_server.py" ]; then
        if grep -q "host.*=.*['\"]0\.0\.0\.0['\"]" run_server.py; then
            log_action "run_server.py correctly binds to 0.0.0.0"
        else
            log_warning "run_server.py may not be binding to 0.0.0.0"
        fi
        
        if grep -q "PORT" run_server.py; then
            log_action "run_server.py uses PORT environment variable"
        else
            log_warning "run_server.py should use PORT environment variable"
        fi
    fi
    
    # Check main FastAPI app
    MAIN_PY="packages/core/monkey_coder/app/main.py"
    if [ -f "$MAIN_PY" ]; then
        if grep -q "0\.0\.0\.0" "$MAIN_PY"; then
            log_action "FastAPI app correctly configured for 0.0.0.0 binding"
        else
            log_warning "FastAPI app should bind to 0.0.0.0"
        fi
    fi
}

# Function to fix health check configuration (ISSUE 5)
fix_health_check() {
    echo -e "\n${YELLOW}3. Fixing Health Check Configuration...${NC}"
    
    # Check railpack.json health configuration
    if [ -f "railpack.json" ]; then
        if jq '.deploy.healthCheckPath' railpack.json | grep -q '"/health"'; then
            log_action "Health check path configured in railpack.json"
        else
            log_warning "Adding health check path to railpack.json"
            # Use jq to add healthCheckPath if missing
            tmp_file=$(mktemp)
            jq '.deploy.healthCheckPath = "/health"' railpack.json > "$tmp_file" && mv "$tmp_file" railpack.json
            ISSUES_FIXED=$((ISSUES_FIXED + 1))
        fi
        
        if jq '.deploy.healthCheckTimeout' railpack.json | grep -q 'null'; then
            log_warning "Adding health check timeout to railpack.json"
            tmp_file=$(mktemp)
            jq '.deploy.healthCheckTimeout = 300' railpack.json > "$tmp_file" && mv "$tmp_file" railpack.json
            ISSUES_FIXED=$((ISSUES_FIXED + 1))
        fi
    fi
    
    # Check if health endpoint is implemented
    MAIN_PY="packages/core/monkey_coder/app/main.py"
    if [ -f "$MAIN_PY" ]; then
        if grep -q "/health" "$MAIN_PY"; then
            log_action "Health endpoint implemented in main.py"
        else
            log_error "Health endpoint not found in main.py"
            echo "Please add a health endpoint that returns HTTP 200"
        fi
    fi
}

# Function to validate monorepo structure (ISSUE 6)
check_monorepo_structure() {
    echo -e "\n${YELLOW}4. Checking Monorepo Structure...${NC}"
    
    if [ -d "packages" ] || [ -d "services" ]; then
        log_action "Monorepo structure detected"
        
        # Check if railpack.json is properly configured for monorepo
        if [ -f "railpack.json" ]; then
            if jq '.services' railpack.json > /dev/null 2>&1; then
                log_action "Services configuration found in railpack.json"
            else
                log_warning "Consider using services configuration for multiple services"
            fi
        fi
    else
        log_action "Single service structure (no monorepo complexity)"
    fi
}

# Function to fix reference variables (ISSUE 4)
fix_reference_variables() {
    echo -e "\n${YELLOW}5. Checking Reference Variables...${NC}"
    
    # Check for invalid Railway variable references
    CONFIG_FILES=("railpack.json" ".env.example" "railway_vars_cli.sh")
    
    for file in "${CONFIG_FILES[@]}"; do
        if [ -f "$file" ]; then
            if grep -q '{{.*\.PORT}}' "$file"; then
                log_warning "File $file contains invalid PORT reference"
                echo "   Use RAILWAY_PUBLIC_DOMAIN instead of PORT references"
            else
                log_action "No invalid PORT references in $file"
            fi
        fi
    done
}

# Function to create Railway deployment readiness script
create_readiness_script() {
    echo -e "\n${YELLOW}6. Creating Deployment Readiness Script...${NC}"
    
    cat > check-railway-readiness.sh << 'EOF'
#!/bin/bash

# Railway Deployment Readiness Check
# Quick pre-deployment validation

echo "🔍 Railway Deployment Readiness Check"
echo "===================================="

READY=true

# Check railpack.json exists and is valid
if [ ! -f "railpack.json" ]; then
    echo "❌ railpack.json not found"
    READY=false
elif ! jq '.' railpack.json > /dev/null 2>&1; then
    echo "❌ railpack.json has invalid JSON"
    READY=false
else
    echo "✅ railpack.json exists and is valid"
fi

# Check for competing build files
COMPETING=0
for file in Dockerfile railway.toml railway.json nixpacks.toml; do
    if [ -f "$file" ] && [ "$file" != "services/*/Dockerfile" ]; then
        echo "❌ Found competing build file: $file"
        COMPETING=$((COMPETING + 1))
        READY=false
    fi
done

if [ $COMPETING -eq 0 ]; then
    echo "✅ No competing build files found"
fi

# Check health endpoint
if [ -f "railpack.json" ] && jq '.deploy.healthCheckPath' railpack.json | grep -q '"/health"'; then
    echo "✅ Health check configured"
else
    echo "⚠️  Health check not configured"
fi

# Final verdict
echo ""
if [ "$READY" = true ]; then
    echo "✅ READY FOR RAILWAY DEPLOYMENT!"
    exit 0
else
    echo "❌ NOT READY - Please fix issues above"
    exit 1
fi
EOF
    
    chmod +x check-railway-readiness.sh
    log_action "Created check-railway-readiness.sh script"
}

# Function to update git hooks for Railway validation
update_git_hooks() {
    echo -e "\n${YELLOW}7. Updating Git Hooks...${NC}"
    
    if [ -f ".githooks/pre-commit" ]; then
        if grep -q "railway" ".githooks/pre-commit"; then
            log_action "Git hooks already include Railway validation"
        else
            log_warning "Consider adding Railway validation to git hooks"
        fi
    else
        log_action "No git hooks to update"
    fi
}

# Main execution
main() {
    echo "Starting Railway deployment fixes..."
    
    fix_build_conflicts
    fix_port_binding 
    fix_health_check
    check_monorepo_structure
    fix_reference_variables
    create_readiness_script
    update_git_hooks
    
    # Summary
    echo -e "\n${BLUE}📋 Fix Summary${NC}"
    echo "=============="
    echo "Issues Fixed: $ISSUES_FIXED"
    echo "Warnings: $WARNINGS"
    
    if [ $ISSUES_FIXED -gt 0 ]; then
        echo -e "\n${GREEN}✅ Applied $ISSUES_FIXED fixes for Railway deployment${NC}"
    fi
    
    if [ $WARNINGS -gt 0 ]; then
        echo -e "\n${YELLOW}⚠️  $WARNINGS warnings need attention${NC}"
    fi
    
    echo -e "\n${BLUE}🚀 Next Steps:${NC}"
    echo "1. Run: ./check-railway-readiness.sh"  
    echo "2. Test locally: railway run python run_server.py"
    echo "3. Deploy: railway up"
    
    echo -e "\n${GREEN}✅ Railway deployment auto-fix completed!${NC}"
}

# Run main function
main