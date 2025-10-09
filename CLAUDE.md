# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

consider MODED_MANIFEST.md as canonical.

## Project Overview

Monkey Coder is an AI-powered code generation and analysis platform that transforms Qwen3-Coder models into a comprehensive development toolkit. It's structured as a Yarn 4.9.2 workspace monorepo with TypeScript CLI tools, Python orchestration core, and multi-language SDKs.

### Yarn Workspace Configuration
- **Package Manager**: Yarn 4.9.2 with Corepack (exact version)
- **Node Linker**: node-modules with hardlinks for performance
- **Global Cache**: Enabled for 30-50% faster installs
- **Constraints**: Enforced via yarn.config.cjs for dependency consistency
- **Security**: Zero vulnerabilities with automated auditing via `yarn npm audit --all`
- **Installation**: Always use `corepack enable && corepack prepare yarn@4.9.2 --activate`
- **Commands**: Use `yarn dlx` instead of `npx` for one-off package execution

### Python Package Management with UV
- **Package Manager**: uv 0.9.0+ for Python dependencies
- **Lock File**: packages/core/uv.lock committed for reproducible builds
- **Python Version**: Requires Python >=3.13 (Railway default)
- **PyTorch**: 2.5.0+ required for Python 3.13 compatibility
- **Installation**: See [UV Setup Guide](docs/UV_SETUP.md)
- **Usage**: `cd packages/core && uv sync` to install dependencies
- **Run Commands**: Use `uv run <command>` to execute in managed venv

## Common Development Commands

### Building and Testing

```bash
# Install dependencies (uses global cache and hardlinks)
yarn install

# Build all packages
yarn build

# Run tests across all packages
yarn test

# Run tests in watch mode
yarn test:watch

# Run test coverage
yarn test:coverage

# Lint all packages
yarn lint

# Fix linting issues
yarn lint:fix

# Type checking
yarn typecheck

# Format code
yarn format

# Check workspace constraints
yarn constraints

# Fix constraint violations
yarn constraints --fix

# Security audit
yarn npm audit --all
```bash

### Package-Specific Commands

```bash
# CLI package (TypeScript)
cd packages/cli
yarn build        # Build CLI
yarn dev          # Watch mode
yarn test         # Jest tests
yarn typecheck    # TypeScript checking

# Core package (Python with UV)
cd packages/core
uv sync                             # Install/sync dependencies
uv run pytest                       # Run tests
uv run pytest -v                    # Verbose tests
uv run pytest --cov=monkey_coder    # Coverage
uv run black .                      # Format code
uv run isort .                      # Sort imports
uv run mypy monkey_coder            # Type checking

# SDK package (TypeScript + Python)
cd packages/sdk
yarn build:ts      # Build TypeScript SDK
yarn build:Python  # Build Python SDK
yarn examples:node # Test Node.js example
```bash

### Documentation Commands

```bash
# Start documentation dev server
yarn docs:dev

# Build documentation
yarn docs:build

# Validate documentation links
yarn docs:validate-links
```bash

## Architecture Overview

### Monorepo Structure
- packages/cli/: TypeScript CLI with Commander.js, providing commands like `implement`, `analyze`, `build`, `test`, and `chat`
- packages/core/: Python FastAPI orchestration engine with multi-agent support, MCP integration, and quantum task execution
- packages/sdk/: Dual TypeScript/Python SDK for API integration
- packages/web/: Next.js 15.2.3 web interface with React 18.2.0
- docs/: Docusaurus documentation site with interactive examples
- services/: Optional microservices (sandbox execution)

### Workspace Dependencies
- All internal dependencies use `workspace:*` protocol
- Consistent versions enforced across workspaces
- Node.js >=20.0.0 required for all packages

### Key Technologies
- Frontend: TypeScript 5.8.3, Commander.js, Chalk, Ora (CLI); Next.js 15.5.4, React 18.2.0 (Web)
- Backend: Python 3.13+, FastAPI, Pydantic, asyncio, PyTorch 2.8.0
- AI Integration: OpenAI, Anthropic, Google GenAI, Groq, Qwen-Agent
- Infrastructure: Railway deployment with railpack.json, Sentry monitoring ^9.42.0
- Testing: Jest ^30.0.5 (TypeScript), Jest ^29.7.0 (Next.js), Pytest (Python)
- Package Managers: Yarn 4.9.2 (JavaScript/TypeScript), uv 0.9.0+ (Python)

### Core Components

#### CLI Architecture (packages/cli/)
- cli.ts: Main command dispatcher with authentication hooks
- API-client.ts: HTTP client for backend communication with streaming support
- config.ts: Configuration management with file persistence
- commands/: Modular command implementations (auth, usage, mcp)
- splash.ts: ASCII art splash screen (can be disabled with `--no-splash`)

#### Python Core (packages/core/)
- monkey_coder/core/orchestrator.py: Multi-agent task orchestration
- monkey_coder/core/quantum_executor.py: Advanced quantum task execution
- monkey_coder/mcp/: Model Context Protocol server management
- monkey_coder/providers/: AI provider adapters (OpenAI, Anthropic, etc.)
- monkey_coder/agents/: Specialized agent implementations
- monkey_coder/billing/: Stripe integration for usage tracking

## Configuration

### Yarn Configuration

The project uses Yarn 4.9.2 with optimized settings in `.yarnrc.yml`:
- Global cache enabled for performance
- Hardlinks for local dependencies
- Immutable installs configurable for CI
- Constraints enforced via `yarn.config.cjs`

### Environment Variables

```bash
# Required for API functionality
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Optional
SENTRY_DSN=your_sentry_dsn
MONKEY_CODER_NO_SPLASH=1  # Disable CLI splash screen
```bash

### CLI Configuration
The CLI stores configuration in `~/.monkey-coder/config.JSON`:

```json
{
  "apiKey": "your_api_key",
  "baseUrl": "http://localhost:8000",
  "defaultPersona": "developer",
  "defaultProvider": "openai",
  "showSplash": true
}
```json

## Testing Strategies

### TypeScript Testing (Jest)
- Unit tests in `__tests__/` directories
- Configuration in `jest.config.cjs` files
- Use `yarn test:watch` for development
- Coverage reports generated in `coverage/` directories

### Python Testing (Pytest)
- Test files follow `test_*.py` pattern
- Configuration in `pytest.ini`
- Async testing with `pytest-asyncio`
- Markers: `@pytest.mark.slow`, `@pytest.mark.integration`

### Running Specific Tests

```bash
# Single test file
yarn workspace monkey-coder-cli test install.test.ts
Python -m pytest tests/test_quantum.py

# Test with debugging
yarn test --verbose
Python -m pytest -v -s

# Integration tests
Python -m pytest -m integration
```bash

## Development Workflow

### Authentication Flow
Commands requiring API access (`implement`, `analyze`, `build`, `test`, `chat`) automatically check for authentication:
1. Check for `--API-key` flag
2. Check configuration file
3. Prompt for login if not authenticated

### Request Building
The CLI builds structured requests with:
- Task type validation (`code_generation`, `code_analysis`, `testing`, `custom`)
- Persona validation (`developer`, `reviewer`, `architect`, `tester`)
- File content reading and language detection
- Streaming support for real-time responses

### Error Handling
- Sentry integration for production error tracking
- Graceful error formatting with chalk colors
- Timeout handling for long-running requests
- Authentication error recovery

## Package Publishing

### Published Packages
- monkey-coder-core (PyPI): v1.0.3 - Python orchestration core
- monkey-coder-sdk (PyPI): v1.0.1 - Python SDK
- monkey-coder-cli (npm): v1.1.0 - TypeScript CLI (ready to publish)

### Release Process

```bash
# Version bump
yarn changeset

# Publish all packages
yarn release

# Individual package scripts
yarn publish-pypi    # Python packages
yarn publish-npm     # npm packages
```bash

## Troubleshooting

### Common Issues
1. Build failures: Check TypeScript compilation with `yarn typecheck`
2. Python import errors: Ensure virtual environment is activated
3. API authentication: Use `monkey auth status` to check login state
4. Streaming issues: Check network connectivity and timeout settings

### Debug Commands

```bash
# CLI debug mode
monkey --verbose implement "your prompt"

# Python debugging
Python -m monkey_coder.core.orchestrator --debug

# Check health
monkey health
```bash

### Log Locations
- CLI logs: Console output with colored formatting
- Python logs: packages/core/data/logs/
- Sentry: Centralized error tracking in production

## Commit Conventions

Follow conventional commits with these scopes:
- feat(cli): New CLI features
- fix(core): Python core bug fixes
- docs: Documentation updates
- test(sdk): SDK test additions
- chore(deps): Dependency updates

Valid commit types: build, chore, ci, docs, feat, fix, perf, refactor, revert, style, test

## CRITICAL FILE PROTECTION

### Protected Configuration Files
NEVER MODIFY the following files without explicit approval:
- packages/core/monkey_coder/models.py - Contains validated AI model configurations critical for system stability
- Any file containing model definitions, API keys, or core provider configurations

Rationale: These files contain carefully validated configurations that ensure API compatibility and system stability. Unauthorized modifications can break the entire platform.

Prohibited Actions:
- Adding new models or providers
- Modifying existing model names, parameters, or capabilities
- Changing provider configurations or API endpoints
- Updating model limits or pricing information

If changes are required: Consult project maintainers and get explicit written approval before making ANY modifications to protected files.

## Important instruction reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
NEVER MODIFY PROTECTED FILES - Especially `packages/core/monkey_coder/models.py` which is STRICTLY PROHIBITED from any changes.

## Agent OS Documentation

### Product Context
- Mission & Vision: @.agent-os/product/mission.md
- Technical Architecture: @.agent-os/product/tech-stack.md
- Development Roadmap: @docs/roadmap.md
- Decision History: @.agent-os/product/decisions.md
- System Enhancements: @.agent-os/product/system-enhancements.md

### Development Standards
- Code Style: @~/.agent-os/standards/code-style.md
- Best Practices: @~/.agent-os/standards/best-practices.md

### Project Management
- Active Specs: @.agent-os/specs/
- Spec Planning: Use `@~/.agent-os/instructions/create-spec.md`
- Tasks Execution: Use `@~/.agent-os/instructions/execute-tasks.md`

## Workflow Instructions

When asked to work on this codebase:

1. First, check @docs/roadmap.md for current priorities
2. Then, follow the appropriate instruction file:
   - For new features: @.agent-os/instructions/create-spec.md
   - For tasks execution: @~/.agent-os/instructions/execute-tasks.md
3. Always, adhere to the standards in the files listed above

## Build Tool Strategy Decision (2025-01-29)

### Comprehensive Evaluation Completed
A thorough evaluation of build tooling options (Yarn vs Nx vs Bazel/Pants) has been completed with the following outcome:

**Decision:** Continue with Yarn 4.9.2 workspace configuration with targeted enhancements

**Key Documents:**
- **Complete Analysis:** `docs/BUILD_TOOL_EVALUATION.md` (18KB technical evaluation)
- **Implementation Guide:** `docs/BUILD_IMPROVEMENTS_IMPLEMENTATION.md` (23KB with scripts)
- **Executive Summary:** `docs/BUILD_TOOL_DECISION_SUMMARY.md` (7KB quick reference)
- **Visual Comparison:** `docs/QUICK_BUILD_TOOL_COMPARISON.md` (11KB with matrices)
- **Response Document:** `docs/RESPONSE_TO_BUILD_TOOL_INQUIRY.md` (13KB addressing inquiry)
- **Product Decision:** `.agent-os/product/decisions.md` (DEC-007)

**Rationale:**
- Current 4-package structure doesn't justify Nx/Bazel complexity
- Yarn already optimized (30-50% faster installs with global cache)
- Migration costs (3-12 weeks) exceed benefits at current scale
- 10-day enhancement plan provides better ROI
- Team maintains velocity with familiar tooling
- Zero migration risk preserves Railway deployment stability

**Enhancement Plan (10 days):**
1. **Week 1:** Task orchestration with npm-run-all2, build monitoring (25% faster parallel builds)
2. **Week 2:** TypeScript project references, Python integration (50% faster incremental builds)
3. **Week 3:** Dependency visualization, circular detection, CI/CD metrics

**Reevaluation Triggers:** Package count >10, team >15 engineers, build times >10 minutes

## Recent System Enhancements (Phase 1 Completion)

### Environment Configuration Management
- Centralized Configuration: `packages/core/monkey_coder/config/env_config.py` provides type-safe environment management
- Validation & Health Checks: Comprehensive configuration validation eliminates environment-related startup failures
- Production Ready: Environment-aware configuration with secure handling of sensitive values

### Enhanced Persona Validation
- Single-Word Input Support: Users can now enter commands like "build", "test", "debug" successfully
- Edge Case Handling: `packages/core/monkey_coder/core/persona_validation.py` provides intelligent prompt enhancement
- Confidence Scoring: Enhanced validation with confidence scoring and contextual suggestions

### Advanced Orchestration Patterns
- Multi-Strategy Coordination: `packages/core/monkey_coder/core/orchestration_coordinator.py` implements 5 orchestration strategies
- Intelligent Selection: Strategy selection based on task complexity and persona context
- Reference Project Integration: Patterns from monkey1 and Gary8D projects integrated

### Production Hardening
- Comprehensive Error Handling: Robust error handling throughout the system
- Enhanced Monitoring: New `/v1/capabilities` endpoint for system status and feature documentation
- Frontend Fallback: Professional error pages when static assets are unavailable

### Key Benefits for Development
- Environment Issues Eliminated: No more dotenv injection warnings or configuration errors
- User Experience Enhanced: Single-word commands work naturally with intelligent enhancement
- Advanced Orchestration: Sophisticated coordination patterns for complex development tasks
- Production Stability: Comprehensive error handling and monitoring

## Important Notes

- Product-specific files in `.agent-os/product/` override any global standards
- User's specific instructions override (or amend) instructions found in `.agent-os/specs/...`
- Always adhere to established patterns, code style, and best practices documented above
- System Status: Phase 1 is 100% complete with comprehensive enhancements - ready for Phase 2 quantum routing development

## Railway Deployment Configuration

### railpack.json Setup

The project uses a simplified railpack.json configuration with runtime frontend building:

```json
{
  "$schema": "https://schema.railpack.com",
  "provider": "python",
  "packages": {
    "python": "3.12.11",
    "node": "20"
  },
  "deploy": {
    "startCommand": "python run_server.py"
  }
}
```json

**Note**: Frontend building is handled at runtime by `run_server.py` which automatically:
- Checks if `packages/web/out` directory exists
- Installs Yarn and dependencies if needed
- Builds the Next.js frontend using `yarn workspace @monkey-coder/web export`
- Continues with server startup even if frontend build fails (with warnings)

## Railway Deployment Master Cheat Sheet (Reference)
## Common Pitfalls & Correct Solutions

---

## 🔴 ISSUE 1: Build System Conflicts

### Common Error Pattern - Build System Conflicts

```text
Nixpacks build failed
ERROR: failed to exec pid1: No such file or directory
```

### Root Cause - Build System Conflicts
Multiple build configurations competing (Dockerfile, railway.toml, railpack.JSON, nixpacks.toml)

### Correct Solution - Build System Conflicts

```bash
# Railway Build Priority Order (highest to lowest):
# 1. Dockerfile (if exists)
# 2. railpack.JSON (if exists)
# 3. railway.JSON/railway.toml
# 4. Nixpacks (auto-detection)

# ENFORCE RAILPACK ONLY:
rm Dockerfile railway.toml nixpacks.toml  # Remove competing configs
touch railpack.JSON                        # Create railpack config
```bash

### Correct railpack.JSON Template

```json
{
  "version": "1",
  "metadata": {
    "name": "my-app"
  },
  "build": {
    "provider": "node",
    "steps": {
      "install": {
        "commands": ["yarn install --frozen-lockfile"]
      },
      "build": {
        "commands": ["yarn build"]
      }
    }
  },
  "deploy": {
    "startCommand": "yarn start",
    "healthCheckPath": "/API/health",
    "healthCheckTimeout": 300
  }
}
```json

---

## 🔴 ISSUE 2: PORT Binding Failures

### Common Error Pattern - PORT Binding

```text
Application failed to respond
Health check failed at /API/health
```

### Root Cause - PORT Binding
Apps hardcoding ports or binding to localhost instead of 0.0.0.0

### Correct Solution - PORT Binding

#### Node.js/TypeScript

```javascript
// ✅ CORRECT
const PORT = process.env.PORT || 3000;
const HOST = '0.0.0.0';  // NOT 'localhost' or '127.0.0.1'
app.listen(PORT, HOST, () => {
  console.log(`Server running on ${HOST}:${PORT}`);
});

// ❌ WRONG
app.listen(3000);  // Hardcoded port
app.listen(PORT, 'localhost');  // Wrong host
```javascript

#### Python

```python
# ✅ CORRECT
import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)

# ❌ WRONG
app.run(host="127.0.0.1", port=5000)  # Wrong host and hardcoded port
```

#### railpack.JSON Start Commands

```json
{
  "deploy": {
    // ✅ CORRECT
    "startCommand": "node server.js",  // Let app read PORT from env

    // ❌ WRONG
    "startCommand": "node server.js --port 3000"  // Hardcoded port
  }
}
```

---

## 🔴 ISSUE 3: Theme/CSS Loading Issues

### Common Error Pattern - Theme/CSS Loading
- Dark mode not persisting
- Tailwind classes not applying
- CSS loading after page render (flash of unstyled content)

### Root Cause - Theme/CSS Loading
Theme initialization happening after React renders, missing CSS imports

### Correct Solution - Theme/CSS Loading

#### 1. Pre-React Theme Application

```javascript
// src/main.tsx or index.tsx
// ✅ CORRECT - Apply theme BEFORE React renders
document.documentElement.className = localStorage.getItem('theme') || 'dark';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
```

#### 2. Proper CSS Import Order

```css
/* src/index.CSS */
/* ✅ CORRECT ORDER */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Critical theme styles */
.dark {
  color-scheme: dark;
}

/* Your custom styles AFTER Tailwind */
```

#### 3. Vite Config for Railway

```javascript
// vite.config.ts
export default defineConfig({
  base: './',  // Relative paths for Railway
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    // Ensure CSS is bundled
    cssCodeSplit: false
  }
});
```

---

## 🔴 ISSUE 4: Reference Variable Mistakes

### Common Error Pattern - Reference Variables

```text
"Install inputs must be an image or step input"
"serviceA.PORT does not resolve"
```

### Root Cause - Reference Variables
Misunderstanding Railway's reference variable system

### Correct Solution - Reference Variables

#### ❌ WRONG - Common Mistakes

```bash
# Cannot reference PORT of another service
BACKEND_URL=${{backend.PORT}}

# Wrong inputs field in railpack.JSON install step
"install": {
  "inputs": [{"step": "setup"}],  # Install doesn't need inputs
  "commands": ["pip install -r requirements.txt"]
}
```

#### ✅ CORRECT - Proper References

```bash
# Reference public domain (Railway provides)
BACKEND_URL=HTTPS://${{backend.RAILWAY_PUBLIC_DOMAIN}}

# Reference private domain for internal communication
INTERNAL_API=HTTP://${{backend.RAILWAY_PRIVATE_DOMAIN}}

# Railway automatically provides PORT - don't set manually
# Let Railway inject PORT, app reads from process.env.PORT
```

---

## 🔴 ISSUE 5: Health Check Configuration

### Common Error Pattern - Health Check Configuration

```text
Health check failed: service unavailable
```

### Correct Solution - Health Check Configuration

#### 1. Add Health Endpoint

```javascript
// Express.js
app.get('/API/health', (req, res) => {
  res.status(200).JSON({ status: 'healthy' });
});

// Python Flask
@app.route('/API/health')
def health():
    return jsonify({'status': 'healthy'}), 200
```

#### 2. Configure in railpack.JSON

```json
{
  "deploy": {
    "healthCheckPath": "/API/health",
    "healthCheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

---

## 🔴 ISSUE 6: Monorepo Service Confusion

### Common Error Pattern - Monorepo Service Confusion

```text
Nixpacks unable to generate build plan
Multiple services detected
```

### Correct Solution - Monorepo Service Confusion

#### Separate railpack.JSON for Each Service

```bash
# Project structure
/
├── backend/
│   └── railpack.JSON  # Backend-specific config
├── frontend/
│   └── railpack.JSON  # Frontend-specific config
└── railpack.JSON      # Root config (if needed)
```

#### Root railpack.JSON for Monorepo

```json
{
  "version": "1",
  "services": {
    "backend": {
      "root": "./backend",
      "build": {
        "provider": "Python"
      }
    },
    "frontend": {
      "root": "./frontend",
      "build": {
        "provider": "node"
      }
    }
  }
}
```

---

## 📋 Pre-Deployment Validation Checklist

```bash
# 1. Check for conflicting build configs
ls -la | grep -E "(Dockerfile|railway\.toml|nixpacks\.toml|railpack\.JSON)"

# 2. Validate railpack.JSON syntax
cat railpack.JSON | jq '.' > /dev/null && echo "✅ Valid JSON"

# 3. Verify PORT usage in code
grep -r "process.env.PORT\|PORT" . | grep -v node_modules

# 4. Check host binding
grep -r "0\.0\.0\.0\|localhost\|127\.0\.0\.1" . | grep -E "(listen|HOST|host)"

# 5. Verify health endpoint exists
grep -r "/health\|/API/health" . | grep -v node_modules

# 6. Test build locally
yarn build && PORT=3000 yarn start

# 7. Create git hook for validation
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
if [ -f railpack.JSON ]; then
  jq '.' railpack.JSON > /dev/null || exit 1
fi
EOF
chmod +x .git/hooks/pre-push
```

---

## 🚀 Quick Fix Commands

```bash
# Force Railpack rebuild
railway up --force

# Clear Railway build cache
railway run --service <service-name> railway cache:clear

# Debug environment variables
railway run env | grep -E "(PORT|HOST|RAILWAY)"

# Test health endpoint
railway run curl http://localhost:$PORT/api/health
```

---

## 📝 Add to Your Coding Assistant Rules

```markdown
## Railway Deployment Standards

1. Always use railpack.JSON as the primary build configuration
2. Never hardcode ports - always use process.env.PORT
3. Always bind to 0.0.0.0 not localhost or 127.0.0.1
4. Apply theme before React renders to prevent flash of unstyled content
5. Reference domains not ports in Railway variables (${{service.RAILWAY_PUBLIC_DOMAIN}})
6. Include health check endpoint at /API/health returning 200 status
7. Remove competing build files (Dockerfile, railway.toml) when using railpack.JSON
8. Test locally with Railway environment: railway run yarn dev
9. Validate JSON syntax before committing railpack.JSON
10. Use inputs field only for layer references in railpack.JSON, not for basic installs
