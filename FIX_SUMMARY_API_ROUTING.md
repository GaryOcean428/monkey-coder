# Fix Summary: API Routing Issues with Static Export

## Problem Statement

The frontend was experiencing JSON parse errors when making API calls:

```
Auth check failed: SyntaxError: Unexpected token '<', "<!DOCTYPE "... is not valid JSON
Failed to fetch models from backend: SyntaxError: Unexpected token '<', "<!DOCTYPE "... is not valid JSON
Login error: SyntaxError: Unexpected token '<', "<!DOCTYPE "... is not valid JSON
```

## Root Cause

The Next.js frontend is configured for **static export** (`output: 'export'` in `next.config.mjs`), which means:

1. It generates static HTML/CSS/JS files
2. It **cannot handle server-side API routes** (e.g., `/api/*`)
3. API calls to `/api/v1/*` were resolving to the Next.js app itself, not the backend
4. The static site was returning HTML pages instead of JSON responses

## Architecture

```
┌─────────────────────┐         ┌──────────────────────┐
│   Frontend          │ ──API──→│   Backend            │
│   (Next.js)         │         │   (FastAPI)          │
│   Static Export     │         │   Python API         │
│   Port: 3000/Railway│         │   Port: 8000/Railway │
└─────────────────────┘         └──────────────────────┘
```

**Key Issue**: The API client was using `window.location.origin` (frontend URL) instead of the backend service URL.

## Solution

### 1. Fixed API Configuration (`services/frontend/src/config/api.ts`)

**Before:**
```typescript
export function getApiBaseUrl(): string {
  if (typeof window !== 'undefined') {
    // This returns the FRONTEND URL, not the backend!
    return window.location.origin;
  }
  return process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
}
```

**After:**
```typescript
export function getApiBaseUrl(): string {
  // 1. Always check environment variable first
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  
  if (typeof window !== 'undefined') {
    const { protocol, hostname } = window.location;
    
    // 2. Railway: Replace frontend subdomain with backend subdomain
    if (hostname.includes('railway.app')) {
      const backendHost = hostname.replace(/^[^.]+/, 'monkey-coder-backend-production');
      return `${protocol}//${backendHost}`;
    }
    
    // 3. Custom domain: Use same domain (backend handles routing)
    if (hostname.includes('fastmonkey.au')) {
      return `${protocol}//${hostname}`;
    }
    
    // 4. Development: Use localhost backend
    return 'http://localhost:8000';
  }
  
  return process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
}
```

### 2. Fixed API Client (`services/frontend/src/lib/api-client.ts`)

Applied the same logic to the APIClient constructor and added better error handling:

```typescript
// Detect HTML responses and provide helpful error messages
if (text.includes('<!DOCTYPE') || text.includes('<html')) {
  throw new Error(
    `API returned HTML instead of JSON. ` +
    `Check that the backend service is running and the API URL is correct. ` +
    `(URL: ${url})`
  );
}
```

### 3. Enhanced Error Handling

Both `api.ts` and `api-client.ts` now:
- Check `Content-Type` header before parsing JSON
- Detect HTML responses and provide clear error messages
- Show the actual URL being called for easier debugging

### 4. Documentation

Created comprehensive deployment guides:
- `services/frontend/DEPLOYMENT.md` - Full deployment instructions
- Updated `.env.example` and `.env.production.example` with clear comments
- This summary document for future reference

### 5. Tests

Created comprehensive tests in `services/frontend/__tests__/config/api.test.ts`:
- Tests for all environment scenarios (localhost, Railway, custom domain)
- Tests for WebSocket URL configuration
- Tests for fallback behavior

## Environment Configuration

### Local Development

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Railway Production

Set this in Railway dashboard for the **frontend service**:

```bash
NEXT_PUBLIC_API_URL=https://monkey-coder-backend-production.up.railway.app
NEXT_PUBLIC_APP_URL=https://monkey-coder.up.railway.app
```

### Custom Domain (if backend on same domain)

```bash
NEXT_PUBLIC_API_URL=https://coder.fastmonkey.au
NEXT_PUBLIC_APP_URL=https://coder.fastmonkey.au
```

## How to Verify the Fix

### 1. Check API URL in Browser

Open the browser console on the frontend and run:

```javascript
console.log('API Base URL:', getApiBaseUrl());
```

### 2. Check Network Tab

1. Open DevTools → Network tab
2. Try to login or fetch models
3. Check the request URL - it should point to the backend service, not the frontend

### 3. Expected Behavior

**Before Fix:**
```
Request URL: https://monkey-coder.up.railway.app/api/v1/auth/login
Response: HTML page (404 or static export page)
Error: "Unexpected token '<', "<!DOCTYPE "... is not valid JSON"
```

**After Fix:**
```
Request URL: https://monkey-coder-backend-production.up.railway.app/api/v1/auth/login
Response: JSON { "access_token": "...", "user": {...} }
Success: User logged in
```

## Testing Checklist

Once deployed to Railway:

- [ ] Navigate to frontend URL
- [ ] Open browser DevTools → Console
- [ ] Check for "Auth check failed" errors (should be gone)
- [ ] Check for "Failed to fetch models" errors (should be gone)
- [ ] Try to login - should work without HTML parse errors
- [ ] Check Network tab - API calls should go to backend service URL
- [ ] Verify authentication works
- [ ] Verify models are fetched successfully

## Railway Deployment Steps

1. **Set Environment Variables** in Railway dashboard:
   - Go to Frontend service → Variables
   - Set `NEXT_PUBLIC_API_URL=https://monkey-coder-backend-production.up.railway.app`
   - Set `NEXT_PUBLIC_APP_URL=https://monkey-coder.up.railway.app`

2. **Trigger Redeploy**:
   - Railway will rebuild with new environment variables
   - Check build logs for successful build
   - Check deploy logs for successful startup

3. **Verify**:
   - Visit the frontend URL
   - Check browser console for errors
   - Test login and API calls

## Troubleshooting

### Still Getting HTML Responses?

1. **Check Environment Variables**: Verify `NEXT_PUBLIC_API_URL` is set correctly in Railway
2. **Check Backend Service**: Ensure the backend service is running and accessible
3. **Check Network Tab**: See where the request is actually going
4. **Check CORS**: Ensure backend has frontend domain in `CORS_ORIGINS`

### Backend Not Responding?

1. Check backend service logs in Railway
2. Check backend service URL is correct
3. Check backend service health endpoint: `/api/health`
4. Ensure backend service is not sleeping (Railway free tier)

### CORS Errors?

Backend needs to include frontend domain in CORS configuration:

```bash
# In backend service environment variables
CORS_ORIGINS=https://monkey-coder.up.railway.app,https://coder.fastmonkey.au
```

## Future Improvements

1. **Service Discovery**: Use Railway's service references in environment variables
2. **Health Checks**: Add frontend health checks to verify backend connectivity
3. **Retry Logic**: Add automatic retry with exponential backoff for failed API calls
4. **Monitoring**: Add monitoring for API call failures

## Related Files

- `services/frontend/src/config/api.ts` - API configuration
- `services/frontend/src/lib/api-client.ts` - API client class
- `services/frontend/src/lib/auth.ts` - Authentication functions
- `services/frontend/src/lib/models.ts` - Models fetching
- `services/frontend/next.config.mjs` - Next.js configuration
- `services/frontend/railpack.json` - Railway build configuration
- `services/frontend/DEPLOYMENT.md` - Deployment guide

## Conclusion

The fix ensures that the frontend correctly routes API calls to the backend service in all environments (local, Railway, custom domain). The key insight is that static export Next.js apps cannot handle API routes themselves and must explicitly point to the backend service URL.
