# Stage 1: Build Next.js Frontend
FROM node:18-alpine AS web-builder
WORKDIR /app

# Enable Corepack for Yarn 4.9.2 support
RUN corepack enable

# Create minimal workspace structure for web package only
COPY packages/web/package.json ./package.json

# Install dependencies ignoring lockfile for simplified build
RUN yarn install

# Copy web source and build
COPY packages/web/ ./
RUN yarn build

# Stage 2: Production Python Backend
FROM python:3.11-slim AS production
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl git build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY packages/core/ ./
RUN pip install -e .

# Copy built frontend assets from Stage 1
COPY --from=web-builder /app/out ./packages/web/out/

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Dynamic port configuration
ARG PORT=8000
ENV PORT=${PORT}
EXPOSE ${PORT}

# Health check optimized for Railway
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Start the application
CMD ["python", "-m", "monkey_coder.app.main"]
