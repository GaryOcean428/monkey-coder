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
```

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
```

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
```

### 3. Database Setup (Optional for basic testing)
```bash
# Using Docker Compose for local development
docker-compose up -d postgres redis

# Or use Railway/external services for development
```

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
```

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
```

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
```

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
```

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
```

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
```

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
```

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
```

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
```

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
```

**Python (Pytest):**
```python
# packages/core/tests/test_orchestrator.py
import pytest
from monkey_coder.core.orchestrator import MultiAgentOrchestrator

@pytest.mark.asyncio
async def test_orchestrator_initialization():
    orchestrator = MultiAgentOrchestrator()
    assert orchestrator.is_initialized()
```

## 🚂 Railway Deployment

### Prerequisites
1. Railway account: https://railway.app/
2. Railway CLI installed: `npm install -g @railway/cli`
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
```

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
- ✅ Health checks at `/health`
- ✅ Build caching for faster deployments

**Health Check Endpoints:**
- `/health` - Basic health status
- `/health/comprehensive` - Detailed component status
- `/health/readiness` - Kubernetes-style readiness probe

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

### Common Issues

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
