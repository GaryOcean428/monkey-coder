# Monkey Coder - Agent Development Guide

This guide provides comprehensive setup, build, test, and deployment instructions for the Monkey Coder AI development platform.

## 🚀 Quick Start

```bash
# 1. Clone and enter the repository
git clone https://github.com/GaryOcean428/monkey-coder.git
cd monkey-coder

# 2. Setup package manager (Yarn 4.9.2 with Corepack)
corepack enable
corepack prepare yarn@4.9.2 --activate

# 3. Install dependencies
yarn install

# 4. Setup environment variables
cp .env.example .env
# Edit .env with your API keys and configuration

# 5. Build all packages
yarn build

# 6. Run tests
yarn test

# 7. Start development server
yarn dev
```bash

## 📋 Table of Contents

- [System Requirements](#-system-requirements)
- [Environment Setup](#-environment-setup)
- [Package Structure](#-package-structure)
- [Build & Development](#-build--development)
- [Testing](#-testing)
- [Railway Deployment](#-railway-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

## 🔧 System Requirements

### Required
- **Node.js:** ≥20.0.0 (use Node 20 LTS recommended)
- **Python:** 3.12 (Railway compatible version)
- **Yarn:** 4.9.2 (managed via Corepack)
- **Git:** Latest stable version

### Optional
- **Docker:** For local services (PostgreSQL, Redis)
- **Railway CLI:** For deployment management

### Development Tools
- **VS Code:** Recommended with extensions:
  - Python
  - TypeScript and JavaScript
  - Prettier
  - ESLint
  - Tailwind CSS IntelliSense

## 🌍 Environment Setup

### 1. Package Manager Setup
```bash
# Enable Corepack (ships with Node 16.9+)
corepack enable

# Activate the specific Yarn version for this project
corepack prepare yarn@4.9.2 --activate

# Verify installation
yarn --version  # Should output: 4.9.2
```bash

**Critical Environment Variables:**
```bash
# Security (REQUIRED - Generate secure random values)
JWT_SECRET_KEY=your-super-secret-jwt-key-here-make-it-long-and-random
NEXTAUTH_SECRET=your-nextauth-secret-minimum-32-characters-long

# AI Provider API Keys (At least one required)
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here

# Database (Required for full functionality)
DATABASE_URL=postgresql://username:password@host:port/database

# Application URLs (adjust for your deployment)
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```bash

### 3. Database Setup (Optional for basic testing)
```bash
# Using Docker Compose for local development
docker-compose up -d postgres redis

# Or use Railway/external services for development
```bash

## 🚀 Build & Development

### Build Commands

```bash
# Build all packages
yarn build

# Build specific workspace
yarn workspace @monkey-coder/cli build
yarn workspace @monkey-coder/core build  # Python build
yarn workspace @monkey-coder/web build

# Development mode with hot reload
yarn dev
```bash

### Development Workflow

```bash
# 1. Start the development environment
yarn dev

# 2. In separate terminals:
# - Backend: packages/core runs on http://localhost:8000
# - Frontend: packages/web runs on http://localhost:3000
# - CLI: yarn workspace @monkey-coder/cli dev

# 3. Validate changes
yarn lint && yarn typecheck && yarn test
```text

## 📦 Package Structure

This is a Yarn 4.9.2 monorepo with the following packages:

```text
packages/
├── cli/           # TypeScript CLI tool
├── core/          # Python FastAPI orchestration engine
├── sdk/           # TypeScript & Python SDKs
└── web/           # Next.js 15.2.3 web interface

docs/              # Docusaurus documentation
services/          # Optional microservices
```bash

### Package Dependencies
- **CLI:** Commander.js, Chalk, Ora for user experience
- **Core:** FastAPI, Pydantic, Uvicorn for API server
- **Web:** Next.js, React 18, Tailwind CSS for frontend
- **SDK:** Dual TypeScript/Python client libraries

## 🔨 Build & Development

### 1. Install Dependencies
```bash
# Install all workspace dependencies
yarn install

# Install Python dependencies for core package
cd packages/core
pip install -e .
cd ../..
```bash

### 2. Build Commands
```bash
# Build all packages in dependency order
yarn build

# Build specific package
yarn workspace @monkey-coder/cli build
yarn workspace @monkey-coder/web build

# Development builds with watch mode
yarn dev                                    # All packages in watch mode
yarn workspace @monkey-coder/web dev        # Web frontend only
```bash

### 3. Development Workflow
```bash
# Start all services in development mode
yarn dev

# Or start services individually:
# Terminal 1: Start the Python API server
cd packages/core
python -m uvicorn monkey_coder.app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start the Next.js frontend
cd packages/web
yarn dev

# Terminal 3: Test the CLI
cd packages/cli
yarn build && yarn link
monkey --help
```bash

### 4. Code Quality
```bash
# Run linting across all packages
yarn lint

# Fix linting issues automatically
yarn lint:fix

# Type checking
yarn typecheck

# Format code with Prettier
yarn format
```bash

## 🧪 Testing

### Test Commands
```bash
# Run all tests
yarn test

# Run tests in watch mode
yarn test:watch

# Run tests with coverage
yarn test:coverage

# Run tests for specific package
yarn workspace @monkey-coder/cli test
yarn workspace @monkey-coder/web test
```text

### Test Structure

```text
packages/
├── cli/
│   └── __tests__/         # Jest tests for CLI
├── core/
│   ├── tests/             # Pytest tests for Python code
│   └── conftest.py        # Pytest configuration
├── web/
│   └── __tests__/         # Jest + React Testing Library
└── sdk/
    └── tests/             # SDK integration tests

tests/
├── integration/           # Cross-package integration tests
├── e2e/                  # End-to-end user workflows
└── performance/          # Load and performance tests
```javascript

### Writing Tests

**TypeScript/JavaScript (Jest):**
```javascript
// packages/cli/__tests__/commands.test.ts
import { describe, it, expect } from '@jest/globals';
import { CLICommand } from '../src/commands/base';

describe('CLI Commands', () => {
  it('should validate user input', () => {
    const command = new CLICommand();
    expect(command.validate('test input')).toBe(true);
  });
});
```python

**Python (Pytest):**
```python
# packages/core/tests/test_orchestrator.py
import pytest
from monkey_coder.core.orchestrator import MultiAgentOrchestrator

@pytest.mark.asyncio
async def test_orchestrator_initialization():
    orchestrator = MultiAgentOrchestrator()
    assert orchestrator.is_initialized()
```bash

## 🚂 Railway Deployment

### Prerequisites
1. Railway account: https://railway.app/
2. Railway CLI available: prefer ephemeral usage with `yarn dlx @railway/cli@latest` (avoid global npm inside repo)
3. Environment variables configured in Railway dashboard

### Deployment Process

#### 1. Railway Project Setup
```bash
# Login to Railway
railway login

# Link to existing project or create new one
railway link
# or
railway init

# Set environment variables
railway variables set JWT_SECRET_KEY="your-secure-secret-here"
railway variables set NEXTAUTH_SECRET="your-nextauth-secret-here"
railway variables set OPENAI_API_KEY="sk-your-openai-key"
# ... set all required variables from .env.example
```bash

#### 2. Database Setup
```bash
# Add PostgreSQL database
railway add postgresql

# Add Redis (optional)
railway add redis

# View connection details
railway variables
```

#### 3. Deploy
```bash
# Deploy from local directory
railway up

# Or setup GitHub integration for automatic deployments
# (Configure in Railway dashboard)
```

### Railway Configuration

The project uses `railpack.json` for Railway deployment configuration:

**Key Features:**
- ✅ Python 3.12 + Node.js 20 dual runtime
- ✅ Virtual environment isolation
- ✅ Frontend build + API server in single service
- ✅ Health checks at `/health` (primary) and `/api/health` (alias)
- ✅ Build caching for faster deployments

**Health Check Endpoints:**
- `/health` - Basic health status (railpack.json default)
- `/api/health` - Alias for A2A/MCP tooling & unified standards
- `/health/comprehensive` - Detailed component status
- `/health/readiness` - Kubernetes-style readiness probe

> Both `/health` and `/api/health` return identical payloads. Tooling may probe either; automation continues to reference `/health` for backward compatibility.

### Railway Deployment Standards (CRITICAL)

**These standards MUST be followed for all Railway deployments:**

#### 1. Build System Configuration
- ✅ **Always use railpack.json** as the primary build configuration
- ❌ **Never create competing files**: Dockerfile, railway.toml, nixpacks.toml at root level
- ⚠️ Railway Build Priority: Dockerfile > railpack.json > railway.toml > Nixpacks auto-detection
- 🔧 Remove competing configs to avoid build conflicts

#### 2. PORT Binding
- ✅ **Always use process.env.PORT** - Railway injects this automatically
- ❌ **Never hardcode ports** - causes deployment failures
- ✅ **Always bind to 0.0.0.0** - NOT localhost or 127.0.0.1
- 🔧 Example: `app.listen(process.env.PORT || 3000, '0.0.0.0')`

#### 3. Service References
- ✅ **Use RAILWAY_PUBLIC_DOMAIN** for external access
- ✅ **Use RAILWAY_PRIVATE_DOMAIN** for internal service-to-service
- ❌ **Never reference PORT** of another service (not available)
- 🔧 Example: `https://${{backend.RAILWAY_PUBLIC_DOMAIN}}`

#### 4. Health Check Configuration
- ✅ **Include health endpoint** at `/api/health` returning 200 status
- ✅ **Configure in railpack.json**: `"healthCheckPath": "/api/health"`
- ✅ **Set timeout appropriately**: `"healthCheckTimeout": 300`
- 🔧 Simple health endpoint: `app.get('/api/health', (req, res) => res.json({status: 'healthy'}))`

#### 5. Railway Validation Tools
```bash
# Comprehensive Railway validation and auto-fix
./scripts/railway-deployment-integration.sh

# Quick readiness check
./check-railway-readiness.sh

# Validate specific configurations
./scripts/validate-railway-config.sh

# MCP-enhanced debugging
python scripts/railway-mcp-debug.py
```

#### 6. Common Pitfalls to Avoid
- ❌ Using `shell=True` in subprocess calls (security risk)
- ❌ Hardcoding environment-specific values
- ❌ Missing or incorrect health check endpoints
- ❌ Binding to localhost instead of 0.0.0.0
- ❌ Creating competing build configuration files
- ❌ Referencing PORT of other services

#### 7. Pre-Deployment Checklist
```bash
# 1. Check for conflicting build configs
ls -la | grep -E "(Dockerfile|railway\.toml|nixpacks\.toml|railpack\.json)"

# 2. Validate railpack.json syntax
cat railpack.json | jq '.' > /dev/null && echo "✅ Valid JSON"

# 3. Verify PORT usage in code
grep -r "process.env.PORT\|PORT" . | grep -v node_modules

# 4. Check host binding (should be 0.0.0.0)
grep -r "0\.0\.0\.0\|localhost\|127\.0\.0\.1" . | grep -E "(listen|HOST|host)"

# 5. Verify health endpoint exists
grep -r "/health\|/api/health" . | grep -v node_modules

# 6. Test build locally
yarn build && PORT=3000 yarn start
```

### Railway Deployment Best Practices Summary

1. **Single Build System**: Only railpack.json, remove all competing configs
2. **Dynamic PORT**: Use process.env.PORT, never hardcode
3. **Correct Host**: Bind to 0.0.0.0, never localhost
4. **Health Checks**: Implement at /api/health with 200 response
5. **Service References**: Use RAILWAY_PUBLIC_DOMAIN/RAILWAY_PRIVATE_DOMAIN
6. **Validation**: Run scripts/railway-deployment-integration.sh before deploying
7. **Security**: Never use shell=True in subprocess, validate all inputs
8. **Testing**: Test locally with Railway environment: `railway run yarn dev`
9. **JSON Validation**: Always validate railpack.json syntax before commit
10. **No Manual Config**: Clear manual Build/Start commands in Railway Dashboard

### Environment Variables for Railway

**Required:**
```bash
JWT_SECRET_KEY=<64-character-random-string>
NEXTAUTH_SECRET=<32-character-random-string>
OPENAI_API_KEY=sk-<your-openai-key>
DATABASE_URL=<automatically-provided-by-railway>
```

**Optional but Recommended:**
```bash
ANTHROPIC_API_KEY=sk-ant-<your-anthropic-key>
SENTRY_DSN=<your-sentry-dsn>
CORS_ORIGINS=https://your-domain.railway.app
```

### Monitoring & Logs
```bash
# View logs
railway logs

# View service status
railway status

# Open deployed application
railway open
```

## 🔍 Troubleshooting

### Additional Common Issues

#### 1. Yarn Version Mismatch
```bash
# Error: "packageManager": "yarn@4.9.2" but current global version is 1.x
# Solution:
corepack enable
corepack prepare yarn@4.9.2 --activate
```

#### 2. Python Import Errors
```bash
# Error: ModuleNotFoundError: No module named 'monkey_coder'
# Solution:
cd packages/core
pip install -e .
```

#### 3. Frontend Build Failures
```bash
# Error: Frontend build failed
# Check Node.js version:
node --version  # Should be ≥20.0.0

# Clear cache and reinstall:
rm -rf node_modules .yarn/cache
yarn install
```

#### 4. Railway Deployment Issues
```bash
# Check deployment logs:
railway logs --deployment

# Validate configuration:
./validate_railway.sh

# Check environment variables:
railway variables
```

#### 5. Database Connection Issues
```bash
# For local development, ensure services are running:
docker-compose up -d postgres redis

# For Railway, check DATABASE_URL is set:
railway variables | grep DATABASE_URL
```

### Debug Commands
```bash
# Check project health
yarn build && yarn test

# Validate Railway configuration
./validate_railway.sh

# Test API server locally
cd packages/core
python run_server.py

# Test CLI locally
cd packages/cli
yarn build && node dist/cli.js --help

# Check frontend build
cd packages/web
yarn build && yarn start
```

### Performance Optimization

#### Frontend Build
```bash
# Enable Next.js build analysis
cd packages/web
npm_config_bundle_analyze=true yarn build
```

#### Python API
```bash
# Profile API performance
cd packages/core
python -m cProfile -o profile.stats run_server.py
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following our coding standards
4. Run tests: `yarn test`
5. Run linting: `yarn lint:fix`
6. Commit changes: `git commit -m 'feat(scope): add amazing feature'`
7. Push to branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Coding Standards

**TypeScript:**
- Use strict mode
- Follow ESLint configuration
- Write unit tests for new features
- Use meaningful variable names

**Python:**
- Follow PEP 8 (enforced by Black)
- Use type hints
- Write docstrings for public functions
- Use async/await for I/O operations

**Git Commits:**
- Use conventional commit format: `type(scope): description`
- Types: feat, fix, docs, style, refactor, test, chore
- Scopes: cli, core, web, sdk, deploy, docs

### Code Review Checklist
- [ ] Tests pass locally
- [ ] Linting passes
- [ ] Documentation updated if needed
- [ ] Breaking changes documented
- [ ] Performance impact considered
- [ ] Security implications reviewed

## 📚 Additional Resources

- **Documentation:** https://docs.monkey-coder.dev (when available)
- **API Reference:** Start server and visit `/api/docs`
- **GitHub Issues:** https://github.com/GaryOcean428/monkey-coder/issues
- **Railway Documentation:** https://docs.railway.app/
- **Yarn 4 Documentation:** https://yarnpkg.com/

## 🚂 Railway Deployment Tools

The project includes comprehensive Railway deployment tools with automated validation and fixing:

```bash
# Comprehensive Railway validation and auto-fix
./scripts/railway-deployment-integration.sh

# Quick readiness check
./check-railway-readiness.sh

# Apply auto-fixes
./scripts/railway-auto-fix.sh
```

### Railway Deployment Status

✅ **Ready for Railway deployment with:**
- Valid railpack.json configuration
- Health endpoint at /health
- Proper PORT binding (0.0.0.0)
- MCP-enhanced validation tools

## 🔧 Common Troubleshooting

### Common Issues

**Yarn Version Mismatch:**
```bash
corepack enable && corepack prepare yarn@4.9.2 --activate
```

**Python Dependencies:**
```bash
cd packages/core && pip install -r requirements-updated.txt
```

**Railway Deployment Issues:**
```bash
# Use the comprehensive validation suite
./scripts/railway-deployment-integration.sh
```

**MCP Framework Not Available:**
- Tools fall back to standalone mode
- Enhanced features unavailable but core functionality works

## 🤝 Contributing Guidelines

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following the coding standards
4. Run validation: `./scripts/railway-deployment-integration.sh`
5. Commit with conventional commits: `feat: add amazing feature`
6. Push to your fork and create a Pull Request

### Code Quality Standards

- **TypeScript:** Strict mode with full type coverage
- **Python:** Type hints and docstrings required
- **Testing:** Minimum 70% coverage for critical paths
- **Documentation:** All public APIs documented
- **Railway Compliance:** All changes must pass deployment validation

---

**Need Help?** Open an issue on GitHub or check the troubleshooting section above.

**Pro Tip:** Use the validate scripts before deployment:
```bash
./scripts/railway-deployment-integration.sh  # Railway deployment validation
yarn build                                   # Ensure all packages build successfully
yarn test                                    # Run the full test suite
```
