# Multi-stage build for Monkey Coder
# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY packages/web/package.json packages/web/package-lock.json* ./
RUN npm ci
COPY packages/web/ ./
RUN npm run build

# Stage 2: Python runtime
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app directory and user
RUN groupadd -r appuser && useradd -r -g appuser appuser
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies and install
COPY packages/core/ ./
RUN pip install -e .

# Copy frontend build from first stage
COPY --from=frontend-builder /app/out ./packages/web/out/

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose dynamic port from environment
ARG PORT
ENV PORT=${PORT:-8000}
EXPOSE ${PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Start the application
CMD ["python", "-m", "monkey_coder.app.main"]
