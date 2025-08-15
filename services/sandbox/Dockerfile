# Sandbox service Dockerfile with E2B/BrowserBase integration
FROM python:3.11-slim

# Set environment variables for security
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    SANDBOX_MODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Create sandbox user with limited privileges
RUN groupadd -r sandbox --gid=1001 && \
    useradd -r -g sandbox --uid=1001 --shell=/bin/bash sandbox

WORKDIR /sandbox

# Install system dependencies with security focus
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    nodejs \
    npm \
    chromium \
    xvfb \
    supervisor \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Python sandbox dependencies
COPY services/sandbox/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install E2B CLI and SDK
RUN pip install e2b-code-interpreter

# Install BrowserBase SDK
RUN pip install browserbase playwright

# Install Playwright browsers with security constraints
RUN playwright install chromium

# Copy sandbox service code
COPY services/sandbox/ ./
RUN chown -R sandbox:sandbox /sandbox

# Create secure volume mount points with proper permissions
RUN mkdir -p /sandbox/volumes/workspace \
    /sandbox/volumes/temp \
    /sandbox/volumes/logs \
    && chown -R sandbox:sandbox /sandbox/volumes \
    && chmod 750 /sandbox/volumes/*

# Network security: Create restricted network namespace
RUN mkdir -p /etc/netns/sandbox

# Copy supervisor configuration for process management
COPY services/sandbox/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Switch to sandbox user
USER sandbox

# Expose sandbox port
ARG PORT
ENV PORT=${PORT:-8001}
EXPOSE ${PORT}

# Resource limits (enforced by Docker runtime)
ENV MEMORY_LIMIT=512m \
    CPU_LIMIT=0.5 \
    NETWORK_RATE_LIMIT=10mbps

# Health check for sandbox service
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Use supervisor to manage multiple processes
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
