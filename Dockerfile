# Stage 1: Build Next.js Frontend
FROM node:18-alpine AS web-builder

# Install system dependencies for Alpine
RUN apk add --no-cache libc6-compat

# Enable Corepack to use the correct Yarn version
RUN corepack enable

WORKDIR /app

# Copy root-level yarn configuration for workspace
COPY yarn.lock ./
COPY .yarnrc.yml ./
COPY package.json ./

# Copy web package.json
COPY packages/web/package.json ./packages/web/

# Install dependencies with Yarn (project's preferred package manager)
# First update lockfile to resolve conflicts, then install dependencies
RUN yarn install --mode=update-lockfile && yarn install

# Copy web source files
COPY packages/web/ ./packages/web/

# Clean any existing build artifacts to ensure fresh build
RUN rm -rf .next out build dist

# Enhanced debugging for Railway build troubleshooting
RUN echo "=== Web package structure ===" && \
    ls -la packages/web/ && \
    echo "=== Source directory structure ===" && \
    ls -la packages/web/src/ && \
    echo "=== Lib directory check ===" && \
    ls -la packages/web/src/lib/ && \
    echo "=== Utils file verification ===" && \
    ls -la packages/web/src/lib/utils.ts && \
    echo "=== Package.json verification ===" && \
    cat packages/web/package.json | grep -A 5 -B 5 "clsx\|tailwind-merge" && \
    echo "=== Node modules verification ===" && \
    ls -la node_modules/clsx node_modules/tailwind-merge 2>/dev/null || echo "Missing critical dependencies"

# Set NODE_ENV for production build
ENV NODE_ENV=production

# Build Next.js with proper static export (fresh build)
RUN cd packages/web && yarn build

# Verify build output exists
RUN ls -la packages/web/out/ || (echo "Build failed: no output directory" && exit 1)

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
