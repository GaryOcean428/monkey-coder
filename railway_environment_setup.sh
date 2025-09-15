#!/bin/bash
set -e

# Railway Environment Setup Script for Monkey Coder
# This script addresses virtual environment path resolution issues in Railway deployment

echo "🐒 Railway Environment Setup for Monkey Coder"
echo "============================================="

# Function to detect the deployment environment
detect_environment() {
    if [ -n "$RAILWAY_ENVIRONMENT" ]; then
        echo "✅ Railway environment detected: $RAILWAY_ENVIRONMENT"
        return 0
    elif [ -n "$RAILWAY_PROJECT_NAME" ]; then
        echo "✅ Railway project detected: $RAILWAY_PROJECT_NAME"
        return 0
    elif [ -d "/app/venv" ]; then
        echo "✅ Railway virtual environment detected at /app/venv"
        return 0
    else
        echo "ℹ️ Local development environment detected"
        return 1
    fi
}

# Function to set up virtual environment paths
setup_venv_paths() {
    local venv_path="/app/venv"
    
    if [ -d "$venv_path" ]; then
        echo "🔧 Setting up Railway virtual environment paths..."
        
        # Set environment variables for virtual environment
        export VIRTUAL_ENV="$venv_path"
        export PATH="$venv_path/bin:$PATH"
        export PYTHONPATH="/app:/app/packages/core:$PYTHONPATH"
        
        echo "✅ Virtual environment configured:"
        echo "   VIRTUAL_ENV: $VIRTUAL_ENV"
        echo "   PATH: $PATH"
        echo "   PYTHONPATH: $PYTHONPATH"
        
        # Verify Python and uvicorn are accessible
        if [ -f "$venv_path/bin/python" ]; then
            echo "✅ Python found: $venv_path/bin/python"
            $venv_path/bin/python --version
        else
            echo "❌ Python not found in virtual environment"
            exit 1
        fi
        
        if [ -f "$venv_path/bin/uvicorn" ]; then
            echo "✅ Uvicorn found: $venv_path/bin/uvicorn"
            $venv_path/bin/uvicorn --version
        else
            echo "❌ Uvicorn not found in virtual environment"
            exit 1
        fi
        
        return 0
    else
        echo "⚠️ Railway virtual environment not found at $venv_path"
        echo "ℹ️ Using system Python environment"
        return 1
    fi
}

# Function to validate required environment variables
validate_environment_vars() {
    echo "🔍 Validating environment variables..."
    
    # Check for Railway-specific variables
    if [ -n "$RAILWAY_PUBLIC_DOMAIN" ]; then
        echo "✅ RAILWAY_PUBLIC_DOMAIN: $RAILWAY_PUBLIC_DOMAIN"
    fi
    
    if [ -n "$RAILWAY_PRIVATE_DOMAIN" ]; then
        echo "✅ RAILWAY_PRIVATE_DOMAIN: $RAILWAY_PRIVATE_DOMAIN"
    fi
    
    # Set default PORT if not specified
    if [ -z "$PORT" ]; then
        export PORT=8000
        echo "ℹ️ PORT not set, defaulting to 8000"
    else
        echo "✅ PORT: $PORT"
    fi
    
    # Validate critical paths exist
    if [ ! -f "/app/run_server.py" ]; then
        echo "❌ run_server.py not found at /app/run_server.py"
        exit 1
    fi
    
    echo "✅ Environment validation completed"
}

# Function to create optimized startup script
create_startup_script() {
    local script_path="/app/railway_start.sh"
    
    echo "📝 Creating optimized Railway startup script..."
    
    cat > "$script_path" << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting Monkey Coder with Railway optimization..."

# Activate virtual environment if it exists
if [ -d "/app/venv" ]; then
    echo "🔧 Activating Railway virtual environment..."
    source /app/venv/bin/activate
    export VIRTUAL_ENV="/app/venv"
    export PATH="/app/venv/bin:$PATH"
    echo "✅ Virtual environment activated"
else
    echo "ℹ️ Using system Python environment"
fi

# Set up Python path
export PYTHONPATH="/app:/app/packages/core:$PYTHONPATH"

# Change to application directory
cd /app

# Validate critical components
echo "🔍 Pre-flight validation..."

if ! python -c "import monkey_coder.app.main" 2>/dev/null; then
    echo "❌ Failed to import FastAPI app"
    exit 1
fi

echo "✅ FastAPI app import successful"

# Start the server
echo "🌟 Starting Monkey Coder server..."
if [ -f "/app/venv/bin/python" ]; then
    /app/venv/bin/python /app/run_server.py
else
    python /app/run_server.py
fi
EOF

    chmod +x "$script_path"
    echo "✅ Startup script created at $script_path"
}

# Function to test the deployment configuration
test_deployment_config() {
    echo "🧪 Testing deployment configuration..."
    
    # Test Python import
    if python -c "import sys; print('Python path:', sys.path)" 2>/dev/null; then
        echo "✅ Python path configuration successful"
    else
        echo "❌ Python path configuration failed"
        exit 1
    fi
    
    # Test package imports
    local test_packages=("fastapi" "uvicorn" "pydantic")
    for package in "${test_packages[@]}"; do
        if python -c "import $package; print('$package version:', getattr($package, '__version__', 'unknown'))" 2>/dev/null; then
            echo "✅ Package import successful: $package"
        else
            echo "❌ Package import failed: $package"
            exit 1
        fi
    done
    
    echo "✅ Deployment configuration test completed"
}

# Main execution
main() {
    echo "Starting Railway environment setup..."
    
    # Detect environment
    if detect_environment; then
        echo "🔧 Configuring for Railway deployment..."
        
        # Set up virtual environment paths
        setup_venv_paths
        
        # Validate environment variables
        validate_environment_vars
        
        # Create startup script
        create_startup_script
        
        # Test configuration
        test_deployment_config
        
        echo "✅ Railway environment setup completed successfully!"
        echo "🚀 Ready for deployment with virtual environment optimization"
        
    else
        echo "ℹ️ Local development environment - no Railway-specific setup needed"
    fi
}

# Execute main function
main "$@"