# Stage 1: Build Next.js Frontend
FROM node:18-alpine AS web-builder

# Install system dependencies for Alpine
RUN apk add --no-cache libc6-compat

WORKDIR /app/packages/web

# Copy web package.json
COPY packages/web/package.json ./

# Install dependencies with npm (ignoring peer dependency warnings)
RUN npm install --legacy-peer-deps --production=false

# Copy web source files
COPY packages/web/ ./

# Clean any existing build artifacts to ensure fresh build
RUN rm -rf .next out build dist

# Debug: Show directory structure for troubleshooting
RUN echo "=== Web package structure ===" && \
    ls -la && \
    echo "=== Source directory structure ===" && \
    ls -la src/ && \
    echo "=== Lib directory check ===" && \
    ls -la src/lib/ || echo "No lib directory found"

# Set NODE_ENV for production build
ENV NODE_ENV=production

# Build Next.js with proper static export (fresh build)
RUN npm run build

# Verify build output exists
RUN ls -la out/ || (echo "Build failed: no output directory" && exit 1)

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

# Copy built frontend assets from Stage 1 with correct path
COPY --from=web-builder /app/packages/web/out/ ./packages/web/out/

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
