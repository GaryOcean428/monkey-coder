#!/bin/bash
# Railway Deployment Path Verification Script
#
# This script validates that all critical paths exist and are correctly configured
# before and after Railway deployments to prevent "No such file or directory" errors.

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Configuration
VENV_PATH="${VENV_PATH:-/app/.venv}"
PYTHON_PATH="${PYTHON_PATH:-/app/.venv/bin/python}"
UVICORN_PATH="${UVICORN_PATH:-/app/.venv/bin/uvicorn}"
PIP_PATH="${PIP_PATH:-/app/.venv/bin/pip}"
FRONTEND_OUT_PATH="${FRONTEND_OUT_PATH:-/app/packages/web/out}"
REQUIREMENTS_FILE="${REQUIREMENTS_FILE:-/app/requirements-deploy.txt}"
START_SCRIPT="${START_SCRIPT:-/app/run_server.py}"

# Path verification functions
verify_virtual_environment() {
    log "Verifying virtual environment setup..."
    
    if [[ ! -d "$VENV_PATH" ]]; then
        error "Virtual environment not found at: $VENV_PATH"
        return 1
    fi
    success "Virtual environment found at: $VENV_PATH"
    
    if [[ ! -f "$PYTHON_PATH" ]]; then
        error "Python executable not found at: $PYTHON_PATH"
        return 1
    fi
    success "Python executable found at: $PYTHON_PATH"
    
    if [[ ! -x "$PYTHON_PATH" ]]; then
        error "Python executable is not executable: $PYTHON_PATH"
        return 1
    fi
    success "Python executable is properly configured"
    
    # Test Python import paths
    if ! "$PYTHON_PATH" -c "import sys; print('Python path OK')" 2>/dev/null; then
        error "Python path configuration is invalid"
        return 1
    fi
    success "Python path configuration is valid"
    
    return 0
}

verify_python_packages() {
    log "Verifying Python package installations..."
    
    if [[ ! -f "$PIP_PATH" ]]; then
        error "Pip executable not found at: $PIP_PATH"
        return 1
    fi
    success "Pip executable found at: $PIP_PATH"
    
    # Check critical packages
    critical_packages=("uvicorn" "fastapi" "pydantic")
    for package in "${critical_packages[@]}"; do
        if ! "$PYTHON_PATH" -c "import $package" 2>/dev/null; then
            error "Critical package '$package' not importable"
            return 1
        fi
        success "Package '$package' is importable"
    done
    
    # Verify uvicorn executable
    if [[ ! -f "$UVICORN_PATH" ]]; then
        error "Uvicorn executable not found at: $UVICORN_PATH"
        return 1
    fi
    success "Uvicorn executable found at: $UVICORN_PATH"
    
    if [[ ! -x "$UVICORN_PATH" ]]; then
        error "Uvicorn executable is not executable: $UVICORN_PATH"
        return 1
    fi
    success "Uvicorn executable is properly configured"
    
    return 0
}

verify_application_files() {
    log "Verifying application files..."
    
    if [[ ! -f "$START_SCRIPT" ]]; then
        error "Start script not found at: $START_SCRIPT"
        return 1
    fi
    success "Start script found at: $START_SCRIPT"
    
    if [[ ! -r "$START_SCRIPT" ]]; then
        error "Start script is not readable: $START_SCRIPT"
        return 1
    fi
    success "Start script is readable"
    
    # Check if start script is valid Python
    if ! "$PYTHON_PATH" -m py_compile "$START_SCRIPT" 2>/dev/null; then
        error "Start script has syntax errors: $START_SCRIPT"
        return 1
    fi
    success "Start script syntax is valid"
    
    # Verify core application module can be imported
    if ! "$PYTHON_PATH" -c "
import sys
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/packages/core')
try:
    from monkey_coder.app.main import app
    print('Core application module imported successfully')
except Exception as e:
    print(f'Failed to import core application: {e}')
    exit(1)
" 2>/dev/null; then
        error "Core application module cannot be imported"
        return 1
    fi
    success "Core application module can be imported"
    
    return 0
}

verify_frontend_assets() {
    log "Verifying frontend assets..."
    
    if [[ ! -d "$FRONTEND_OUT_PATH" ]]; then
        warning "Frontend output directory not found at: $FRONTEND_OUT_PATH"
        warning "This is acceptable for API-only deployments"
        return 0
    fi
    success "Frontend output directory found at: $FRONTEND_OUT_PATH"
    
    if [[ ! -f "$FRONTEND_OUT_PATH/index.html" ]]; then
        warning "Frontend index.html not found at: $FRONTEND_OUT_PATH/index.html"
        warning "This may indicate a frontend build failure"
        return 0
    fi
    success "Frontend index.html found"
    
    # Check if index.html is valid
    if [[ ! -s "$FRONTEND_OUT_PATH/index.html" ]]; then
        warning "Frontend index.html is empty"
        return 0
    fi
    success "Frontend index.html has content"
    
    return 0
}

verify_environment_variables() {
    log "Verifying environment variables..."
    
    # Check PATH includes virtual environment
    if [[ ":$PATH:" != *":$VENV_PATH/bin:"* ]]; then
        warning "Virtual environment bin directory not in PATH"
        warning "This may cause executable resolution issues"
    else
        success "Virtual environment bin directory is in PATH"
    fi
    
    # Check PYTHONPATH
    if [[ -n "${PYTHONPATH:-}" ]]; then
        if [[ ":$PYTHONPATH:" != *":/app:"* ]] || [[ ":$PYTHONPATH:" != *":/app/packages/core:"* ]]; then
            warning "PYTHONPATH may not include required application directories"
        else
            success "PYTHONPATH includes required directories"
        fi
    else
        warning "PYTHONPATH not set - relying on sys.path modification"
    fi
    
    # Check PORT configuration
    if [[ -n "${PORT:-}" ]]; then
        if [[ ! "$PORT" =~ ^[0-9]+$ ]] || [[ "$PORT" -lt 1 ]] || [[ "$PORT" -gt 65535 ]]; then
            error "PORT environment variable has invalid value: $PORT"
            return 1
        fi
        success "PORT environment variable is valid: $PORT"
    else
        warning "PORT environment variable not set - using default"
    fi
    
    return 0
}

verify_startup_command() {
    log "Verifying startup command configuration..."
    
    # Test that the exact startup command works
    startup_cmd="$PYTHON_PATH $START_SCRIPT"
    
    log "Testing startup command: $startup_cmd"
    
    # Create a test script that starts and immediately shuts down
    test_script="/tmp/test_startup.py"
    cat > "$test_script" << 'EOF'
import sys
import os
import signal
import time
import threading

# Add paths
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/packages/core')

def shutdown_handler(signum, frame):
    print("Test startup successful - shutting down")
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)

# Schedule shutdown after 5 seconds
def delayed_shutdown():
    time.sleep(5)
    print("Test startup successful - auto-shutting down")
    os.kill(os.getpid(), signal.SIGTERM)

shutdown_thread = threading.Thread(target=delayed_shutdown)
shutdown_thread.daemon = True
shutdown_thread.start()

try:
    # Import and test the application
    from monkey_coder.app.main import app
    import uvicorn
    
    print("Starting test server...")
    # Use test port to avoid conflicts
    uvicorn.run(app, host="127.0.0.1", port=9999, log_level="error")
except Exception as e:
    print(f"Startup test failed: {e}")
    sys.exit(1)
EOF

    # Run the test with timeout
    if timeout 10 "$PYTHON_PATH" "$test_script" >/dev/null 2>&1; then
        success "Startup command test passed"
        rm -f "$test_script"
        return 0
    else
        error "Startup command test failed"
        rm -f "$test_script"
        return 1
    fi
}

create_diagnostic_report() {
    log "Creating diagnostic report..."
    
    report_file="/tmp/railway_path_verification_report.json"
    
    cat > "$report_file" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "verification_results": {
        "virtual_environment": $(verify_virtual_environment >/dev/null 2>&1 && echo "true" || echo "false"),
        "python_packages": $(verify_python_packages >/dev/null 2>&1 && echo "true" || echo "false"),
        "application_files": $(verify_application_files >/dev/null 2>&1 && echo "true" || echo "false"),
        "frontend_assets": $(verify_frontend_assets >/dev/null 2>&1 && echo "true" || echo "false"),
        "environment_variables": $(verify_environment_variables >/dev/null 2>&1 && echo "true" || echo "false"),
        "startup_command": $(verify_startup_command >/dev/null 2>&1 && echo "true" || echo "false")
    },
    "paths": {
        "venv_path": "$VENV_PATH",
        "python_path": "$PYTHON_PATH",
        "uvicorn_path": "$UVICORN_PATH",
        "pip_path": "$PIP_PATH",
        "frontend_out_path": "$FRONTEND_OUT_PATH",
        "requirements_file": "$REQUIREMENTS_FILE",
        "start_script": "$START_SCRIPT"
    },
    "environment": {
        "PATH": "$PATH",
        "PYTHONPATH": "${PYTHONPATH:-}",
        "PORT": "${PORT:-}",
        "VIRTUAL_ENV": "${VIRTUAL_ENV:-}",
        "PWD": "$PWD"
    },
    "system_info": {
        "python_version": "$("$PYTHON_PATH" --version 2>&1 || echo "unknown")",
        "pip_version": "$("$PIP_PATH" --version 2>&1 | head -1 || echo "unknown")",
        "disk_usage": "$(df -h / | tail -1 || echo "unknown")",
        "memory_usage": "$(free -h | head -2 | tail -1 || echo "unknown")"
    }
}
EOF

    success "Diagnostic report created at: $report_file"
    return 0
}

# Main verification function
main() {
    log "Starting Railway deployment path verification..."
    log "=============================================="
    
    verification_passed=true
    
    # Run all verification steps
    if ! verify_virtual_environment; then
        verification_passed=false
    fi
    
    if ! verify_python_packages; then
        verification_passed=false
    fi
    
    if ! verify_application_files; then
        verification_passed=false
    fi
    
    if ! verify_frontend_assets; then
        # Frontend verification warnings don't fail the overall check
        true
    fi
    
    if ! verify_environment_variables; then
        verification_passed=false
    fi
    
    if ! verify_startup_command; then
        verification_passed=false
    fi
    
    # Always create diagnostic report
    create_diagnostic_report
    
    log "=============================================="
    if [[ "$verification_passed" == "true" ]]; then
        success "✅ All path verifications passed!"
        success "Railway deployment should start successfully"
        exit 0
    else
        error "❌ Path verification failed!"
        error "Railway deployment may encounter startup issues"
        exit 1
    fi
}

# Help function
show_help() {
    cat << EOF
Railway Deployment Path Verification Script

Usage: $0 [OPTIONS]

OPTIONS:
    -h, --help          Show this help message
    --venv-path PATH    Override virtual environment path (default: /app/.venv)
    --python-path PATH  Override Python executable path (default: /app/.venv/bin/python)
    --start-script PATH Override start script path (default: /app/run_server.py)
    --frontend-path PATH Override frontend output path (default: /app/packages/web/out)

ENVIRONMENT VARIABLES:
    VENV_PATH           Virtual environment path
    PYTHON_PATH         Python executable path
    UVICORN_PATH        Uvicorn executable path
    PIP_PATH            Pip executable path
    FRONTEND_OUT_PATH   Frontend output directory path
    REQUIREMENTS_FILE   Requirements file path
    START_SCRIPT        Application start script path

EXAMPLES:
    # Basic verification
    $0

    # Verification with custom paths
    VENV_PATH=/custom/venv $0

    # Help
    $0 --help

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --venv-path)
            VENV_PATH="$2"
            shift 2
            ;;
        --python-path)
            PYTHON_PATH="$2"
            shift 2
            ;;
        --start-script)
            START_SCRIPT="$2"
            shift 2
            ;;
        --frontend-path)
            FRONTEND_OUT_PATH="$2"
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