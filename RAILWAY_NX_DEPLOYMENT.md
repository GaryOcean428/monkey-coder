# Railway Deployment Guide for Nx Monorepo

This monorepo contains three services deployable to Railway.app. Each service has its own `railpack.json` configuration file following the official [railpack.com specification](https://railpack.com/config/file/).

## Services

### 1. Frontend (Root `railpack.json`)
- **Path:** Root directory
- **Type:** Node.js 20 / Next.js 15
- **Build:** Yarn 4.9.2 workspace build
- **Deploy:** Static export served via `serve`
- **Health Check:** `/` (120s timeout)
- **Config:** `railpack.json`

### 2. Backend (`services/backend/railpack.json`)
- **Path:** `services/backend/`
- **Type:** Python 3.12 / FastAPI
- **Build:** uv package manager
- **Deploy:** Uvicorn with 2 workers
- **Health Check:** `/api/health` (305s timeout)
- **Config:** `services/backend/railpack.json`

### 3. ML Service (`services/ml/railpack.json`)
- **Path:** `services/ml/`
- **Type:** Python 3.12 / PyTorch
- **Build:** uv package manager with HuggingFace cache
- **Deploy:** Uvicorn with 1 worker (GPU support)
- **Health Check:** `/api/health` (600s timeout)
- **Config:** `services/ml/railpack.json`

## Railway Deployment

### Multi-Service Deployment (Recommended for Nx)

Deploy each service separately on Railway:

1. **Frontend Service**
   - Root Path: `/` (repository root)
   - Build Command: Uses `railpack.json` at root
   - Railway will auto-detect and use the root railpack.json

2. **Backend Service**
   - Root Path: `/services/backend`
   - Build Command: Uses `services/backend/railpack.json`
   - Set Railway service root path to `services/backend`

3. **ML Service**
   - Root Path: `/services/ml`
   - Build Command: Uses `services/ml/railpack.json`
   - Set Railway service root path to `services/ml`

### Service Communication

Services communicate via Railway's private networking:

- Backend → ML: Uses `ML_SERVICE_URL` environment variable
- Frontend → Backend: Uses public domain or private domain for SSR

Environment variable references (set in Railway dashboard):
- `${{SERVICE_NAME.RAILWAY_PRIVATE_DOMAIN}}` for internal communication
- `${{SERVICE_NAME.RAILWAY_PUBLIC_DOMAIN}}` for external access

## Railpack.json Compliance

All railpack.json files follow the official specification from https://railpack.com/config/file/:

### Structure
```json
{
  "$schema": "https://schema.railpack.com",
  "version": "1",
  "metadata": { ... },
  "build": { ... },
  "steps": { ... },
  "deploy": { ... }
}
```

### Key Features
- ✅ `$schema` for validation
- ✅ `version` field set to "1"
- ✅ `metadata` with name and description
- ✅ `build.provider` (node or python)
- ✅ `build.packages` for runtime versions
- ✅ `steps` with install and build stages
- ✅ `steps.*.inputs` for layer dependencies
- ✅ `deploy.startCommand` using $PORT
- ✅ `deploy.healthCheckPath` for health monitoring
- ✅ `deploy.env` for environment variables
- ✅ All services bind to `0.0.0.0` and use `$PORT`

## Nx Best Practices

### Workspace Structure
```
monkey-coder/
├── railpack.json              # Frontend service config
├── packages/
│   └── web/                   # Next.js frontend
├── services/
│   ├── backend/
│   │   └── railpack.json      # Backend service config
│   └── ml/
│       └── railpack.json      # ML service config
└── package.json               # Yarn workspace root
```

### Benefits of This Approach
1. **Clear Separation**: Each service has its own railpack.json
2. **Independent Deployment**: Services can be deployed separately
3. **Nx Compatible**: Follows Nx monorepo patterns
4. **Railway Compliant**: Uses official railpack.json specification
5. **Scalable**: Easy to add new services

### Railway Service Configuration

When creating services in Railway dashboard:

1. **Set Root Path**: Point to the service directory
   - Frontend: `/` (root)
   - Backend: `services/backend`
   - ML: `services/ml`

2. **Environment Variables**: Set in Railway dashboard
   - `PORT` is automatically injected by Railway
   - Service references use `${{service.RAILWAY_PRIVATE_DOMAIN}}`

3. **Build Detection**: Railway will auto-detect railpack.json in the service root

## Validation

Validate all railpack.json files:
```bash
jq '.' railpack.json
jq '.' services/backend/railpack.json
jq '.' services/ml/railpack.json
```

## References

- [Railpack Official Docs](https://railpack.com/config/file/)
- [Railway Monorepo Guide](https://docs.railway.app/guides/monorepo)
- [Nx Documentation](https://nx.dev/)
- [Railway Environment Variables](https://docs.railway.app/guides/variables)
