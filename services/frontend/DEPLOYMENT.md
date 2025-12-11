# Frontend Deployment Guide

## Overview

The Monkey Coder frontend is a Next.js application configured for **static export** deployment. This means:
- The app is built as static HTML/CSS/JS files
- It cannot handle server-side API routes
- All API calls must be directed to the separate backend service

## Architecture

```
┌─────────────────┐         ┌─────────────────┐
│   Frontend      │ ──API──→ │   Backend       │
│   (Next.js)     │         │   (FastAPI)     │
│   Static Site   │         │   Python API    │
└─────────────────┘         └─────────────────┘
```

## Environment Configuration

### Local Development

When running locally, the frontend makes API calls to `http://localhost:8000`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Railway Deployment

For Railway deployment, you need to configure the backend service URL:

```bash
# Set this in Railway dashboard for the frontend service
NEXT_PUBLIC_API_URL=https://monkey-coder-backend-production.up.railway.app

# Or if using custom domain with backend on same domain:
NEXT_PUBLIC_API_URL=https://coder.fastmonkey.au
```

## Common Issues

### Error: "Unexpected token '<', '<!DOCTYPE'... is not valid JSON"

**Cause**: The frontend is trying to call API endpoints on itself instead of the backend service.

**Solution**: Ensure `NEXT_PUBLIC_API_URL` is properly set to point to the backend service URL.

### How API URLs are Resolved

The frontend uses this logic to determine the backend URL:

1. **Check `NEXT_PUBLIC_API_URL` environment variable** (highest priority)
2. **Auto-detect based on hostname**:
   - `localhost` → `http://localhost:8000`
   - `*.railway.app` → Replace frontend subdomain with backend subdomain
   - `fastmonkey.au` → Use same domain (backend handles routing)
3. **Fallback** → `http://localhost:8000`

### Files That Handle API Configuration

- `src/config/api.ts` - Main API configuration
- `src/lib/api-client.ts` - API client class
- `.env.example` - Development environment template
- `.env.production.example` - Production environment template

## Testing API Configuration

To verify the API URL is correctly configured:

```javascript
// In browser console
console.log('API Base URL:', getApiBaseUrl());
```

Or check the Network tab in DevTools to see where API requests are being sent.

## Deployment Steps

1. **Set environment variables** in Railway dashboard:
   ```
   NEXT_PUBLIC_API_URL=https://monkey-coder-backend-production.up.railway.app
   NEXT_PUBLIC_APP_URL=https://monkey-coder.up.railway.app
   ```

2. **Build the frontend**:
   ```bash
   yarn workspace @monkey-coder/frontend build
   ```

3. **Deploy**:
   - Railway automatically detects `railpack.json` and builds the project
   - The static files are served using `serve`

## Troubleshooting

### API calls returning HTML instead of JSON

1. Check the Network tab in browser DevTools
2. Verify the request URL is pointing to the backend service
3. Check if `NEXT_PUBLIC_API_URL` is set correctly
4. Ensure the backend service is running and accessible

### CORS Issues

If you see CORS errors:
1. Ensure the backend CORS configuration includes the frontend domain
2. Check the backend's `CORS_ORIGINS` environment variable

### Railway-Specific Issues

- Ensure the frontend and backend are deployed as **separate services**
- Each service should have its own `railpack.json`
- Use Railway's service reference for the backend URL
- Check Railway logs for both services to diagnose issues
