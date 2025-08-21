# Multi-stage Dockerfile for Railway deployment
# Stage 1: Frontend Builder
FROM node:20-alpine AS frontend-builder

# Enable Corepack for Yarn 4.9.2
RUN corepack enable && corepack prepare yarn@4.9.2 --activate

WORKDIR /build

# Copy package files
COPY package.json yarn.lock .yarnrc.yml ./
COPY .yarn .yarn/
COPY packages/web/package.json packages/web/

# Install dependencies with immutable lockfile
RUN yarn install --immutable

# Copy frontend source and build
COPY packages/web packages/web/
RUN yarn workspace @monkey-coder/web build

# Stage 2: Python Runtime with Node
FROM python:3.13-slim

# Install Node.js 20 and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy core package and install
COPY packages/core packages/core/
RUN cd packages/core && pip install --no-cache-dir -e .

# Copy frontend build from stage 1
COPY --from=frontend-builder /build/packages/web/out packages/web/out/

# Copy server startup script
COPY run_server.py .

# Set environment variables
ENV NODE_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Expose port (Railway will override with PORT env var)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Start the unified server
CMD ["python", "run_server.py"]
