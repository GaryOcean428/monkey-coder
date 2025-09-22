#!/bin/bash
set -euo pipefail

echo "🚀 Starting Monkey Coder Server"
echo "================================"

# Activate virtual environment if it exists
if [ -f "/app/.venv/bin/activate" ]; then
    echo "📦 Activating virtual environment at /app/.venv"
    source /app/.venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    echo "📦 Activating local virtual environment"
    source .venv/bin/activate
fi

# Verify Python version
echo "🐍 Python version check:"
python --version

# Verify PyTorch installation
echo "🔧 Verifying PyTorch installation..."
python -c "import torch; print(f'✅ PyTorch {torch.__version__} loaded successfully')" || {
    echo "⚠️ PyTorch not installed or failed to load"
}

# Setup frontend if needed
if [ "${SERVE_FRONTEND:-true}" = "true" ]; then
    echo "🎨 Checking frontend build..."
    if [ -d "packages/web/out" ] && [ "$(ls -A packages/web/out 2>/dev/null)" ]; then
        echo "✅ Frontend assets found"
    else
        echo "🏗️ Frontend build not found, will attempt runtime build"
        python run_server.py || echo "⚠️ Frontend setup skipped"
    fi
fi

# Set default environment variables
export PORT=${PORT:-8000}
export LOG_LEVEL=${LOG_LEVEL:-info}
export WORKERS=${WORKERS:-1}

echo "📋 Server Configuration:"
echo "  • Port: ${PORT}"
echo "  • Log Level: ${LOG_LEVEL}"
echo "  • Workers: ${WORKERS}"
echo "  • Host: 0.0.0.0"

# Start the server
echo "🚀 Starting Uvicorn server..."

# Check if we're in Railway environment
if [ -n "${RAILWAY_ENVIRONMENT:-}" ]; then
    echo "🚂 Railway environment detected: ${RAILWAY_ENVIRONMENT}"
    # Use the run_server.py for Railway
    exec python run_server.py
else
    # For local development, try to use uvicorn directly
    if command -v uvicorn &> /dev/null; then
        cd packages/core 2>/dev/null || cd /app/packages/core 2>/dev/null || true
        exec uvicorn monkey_coder.app.main:app \
            --host 0.0.0.0 \
            --port ${PORT} \
            --workers ${WORKERS} \
            --loop uvloop \
            --access-log \
            --log-level ${LOG_LEVEL}
    else
        # Fallback to run_server.py
        exec python run_server.py
    fi
fi
