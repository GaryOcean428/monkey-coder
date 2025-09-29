# Railway Services Separation Guide

## Overview

The Monkey Coder platform has been separated into two distinct Railway services for better scalability, maintainability, and development workflow:

1. **Backend Service** (`monkey-coder-backend`) - FastAPI application
2. **Frontend Service** (`monkey-coder-frontend`) - Next.js web interface

## Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │
│   (Next.js)     │◄──►│   (FastAPI)     │
│   Port: 3000    │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘
```

## Service Configurations

### Backend Service (`railpack-backend.json`)

- **Purpose**: AI orchestration, API endpoints, core business logic
- **Technology**: Python FastAPI
- **Port**: 8000
- **Health Check**: `/health`
- **Resources**: 2Gi memory, 1000m CPU

### Frontend Service (`railpack.json`)

- **Purpose**: Web interface, authentication portal, user dashboard
- **Technology**: Next.js React application
- **Port**: 3000
- **Health Check**: `/api/health`
- **Resources**: 1Gi memory, 500m CPU

## Deployment Process

### 1. Deploy Backend Service

```bash
# Deploy backend service
railway up --config railpack-backend.json
```

### 2. Deploy Frontend Service

```bash
# Deploy frontend service (references backend via environment variable)
railway up --config railpack.json
```

### 3. Configure Service Discovery

The frontend automatically connects to the backend using the `BACKEND_URL` environment variable, which references the Railway internal domain of the backend service.

## Environment Variables

### Backend Service

```env
PORT=8000
ENVIRONMENT=production
LOG_LEVEL=info
SUPABASE_URL=${SUPABASE_URL}
POSTGRES_URL=${POSTGRES_URL}
# ... other secrets
```

### Frontend Service

```env
NODE_ENV=production
PORT=3000
BACKEND_URL=${monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}
NEXT_PUBLIC_API_URL=${monkey-coder-backend.RAILWAY_PUBLIC_DOMAIN}
```

## Benefits of Separation

1. **Independent Scaling**: Scale backend and frontend resources independently
2. **Development Workflow**: Separate deployments for API and UI changes
3. **External Integration**: Backend service can be used by external applications
4. **Resource Optimization**: Different resource allocation for different workloads
5. **Fault Isolation**: Issues in one service don't affect the other

## External API Access

The separated backend service provides a clean API for external integrations:

- **API Base URL**: `https://monkey-coder-backend.railway.app`
- **Documentation**: Available at `/docs` endpoint
- **Authentication**: JWT-based authentication system
- **Rate Limiting**: Configured per plan tier

## Monitoring & Health Checks

Both services include comprehensive health monitoring:

- **Backend**: `/health` and `/api/v1/health/detailed`
- **Frontend**: `/api/health`
- **Restart Policy**: Automatic restart on failure (max 3 retries)

## Railway Deployment Configuration

### Frontend Service (Next.js Static Export)

The frontend service is configured for static export to ensure compatibility with Railway's deployment model:

- **Build Command**: Uses `yarn workspace @monkey-coder/web export` instead of `yarn build`
- **Environment Variables**: 
  - `NEXT_OUTPUT_EXPORT=true` - Enables Next.js static export mode
  - `NEXT_TELEMETRY_DISABLED=1` - Disables Next.js telemetry
- **Next.js Configuration**: `packages/web/next.config.js` conditionally enables static export
- **Output Directory**: Static files are generated in `packages/web/out/`

### Troubleshooting

**Build Hanging Issues:**
- Ensure `yarn export` is used instead of `yarn build` for static export
- Verify `NEXT_OUTPUT_EXPORT=true` is set in build environment
- Check that `next.config.js` exists and has proper export configuration

**Static Asset Issues:**
- Verify `images.unoptimized: true` in Next.js config for static export compatibility
- Ensure `trailingSlash: true` for proper routing in static export mode

## Migration Notes

- Existing deployments will continue to work
- New deployments should use the separated architecture
- Environment variables need to be configured for service discovery
- Database connections remain centralized through Supabase
- Frontend now uses static export for improved Railway compatibility
