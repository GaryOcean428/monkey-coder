# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

consider MODELS_MANIFEST.md as canonical.

## Project Overview

Monkey Coder is an AI-powered code generation and analysis platform that transforms Qwen3-Coder models into a comprehensive development toolkit. It's structured as a yarn 4.9.2 workspace monorepo with TypeScript CLI tools, Python orchestration core, and multi-language SDKs.

## Common Development Commands

### Building and Testing

```bash
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
```

### Package-Specific Commands

```bash
# CLI package (TypeScript)
cd packages/cli
yarn build        # Build CLI
yarn dev          # Watch mode
yarn test         # Jest tests
yarn typecheck    # TypeScript checking

# Core package (Python)
cd packages/core
Python -m pytest                    # Run tests
Python -m pytest -v                 # Verbose tests
Python -m pytest --cov=monkey_coder # Coverage
black .                             # Format code
isort .                             # Sort imports
mypy monkey_coder                   # Type checking

# SDK package (TypeScript + Python)
cd packages/sdk
yarn build:ts      # Build TypeScript SDK
yarn build:Python  # Build Python SDK
yarn examples:node # Test Node.js example
```

### Documentation Commands

```bash
# Start documentation dev server
yarn docs:dev

# Build documentation
yarn docs:build

# Validate documentation links
yarn docs:validate-links
```

## Architecture Overview

### Monorepo Structure
- packages/cli/: TypeScript CLI with Commander.js, providing commands like `implement`, `analyze`, `build`, `test`, and `chat`
- packages/core/: Python FastAPI orchestration engine with multi-agent support, MCP integration, and quantum task execution
- packages/sdk/: Dual TypeScript/Python SDK for API integration
- packages/web/: Next.js web interface (optional)
- docs/: Docusaurus documentation site with interactive examples
- services/: Optional microservices (sandbox execution)

### Key Technologies
- Frontend: TypeScript, Commander.js, Chalk, Ora (CLI); Next.js, React (Web)
- Backend: Python 3.8+, FastAPI, Pydantic, asyncio
- AI Integration: OpenAI, Anthropic, Google GenAI, Groq, Qwen-Agent
- Infrastructure: Docker, Railway deployment, Sentry monitoring
- Testing: Jest (TypeScript), Pytest (Python)

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

### Environment Variables

```bash
# Required for API functionality
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Optional
SENTRY_DSN=your_sentry_dsn
MONKEY_CODER_NO_SPLASH=1  # Disable CLI splash screen
```

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
```

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
```

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
```

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
```

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

## Railway Deployment Master Cheat Sheet (Reference)
## Common Pitfalls & Correct Solutions

---

## 🔴 ISSUE 1: Build System Conflicts

### Common Error Pattern
```text
Nixpacks build failed
ERROR: failed to exec pid1: No such file or directory
```

### Root Cause
Multiple build configurations competing (Dockerfile, railway.toml, railpack.json, nixpacks.toml)

### Correct Solution
```bash
# Railway Build Priority Order (highest to lowest):
# 1. Dockerfile (if exists)
# 2. railpack.json (if exists)
# 3. railway.json/railway.toml
# 4. Nixpacks (auto-detection)

# ENFORCE RAILPACK ONLY:
rm Dockerfile railway.toml nixpacks.toml  # Remove competing configs
touch railpack.json                        # Create railpack config
```

### Correct railpack.json Template:
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
    "healthCheckPath": "/api/health",
    "healthCheckTimeout": 300
  }
}
```

---

## 🔴 ISSUE 2: PORT Binding Failures

### Common Error Pattern
```text
Application failed to respond
Health check failed at /api/health
```

### Root Cause:
Apps hardcoding ports or binding to localhost instead of 0.0.0.0

### Correct Solution:

#### Node.js/TypeScript:
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
```

#### Python:
```python
# ✅ CORRECT
import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)

# ❌ WRONG
app.run(host="127.0.0.1", port=5000)  # Wrong host and hardcoded port
```

#### railpack.json Start Commands
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

### Common Error Pattern:
- Dark mode not persisting
- Tailwind classes not applying
- CSS loading after page render (flash of unstyled content)

### Root Cause:
Theme initialization happening after React renders, missing CSS imports

### Correct Solution:

#### 1. Pre-React Theme Application:
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

#### 2. Proper CSS Import Order:
```css
/* src/index.css */
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

#### 3. Vite Config for Railway:
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

### Common Error Pattern:
```
"Install inputs must be an image or step input"
"serviceA.PORT does not resolve"
```

### Root Cause:
Misunderstanding Railway's reference variable system

### Correct Solution:

#### ❌ WRONG - Common Mistakes:
```bash
# Cannot reference PORT of another service
BACKEND_URL=${{backend.PORT}}

# Wrong inputs field in railpack.json install step
"install": {
  "inputs": [{"step": "setup"}],  # Install doesn't need inputs
  "commands": ["pip install -r requirements.txt"]
}
```

#### ✅ CORRECT - Proper References:
```bash
# Reference public domain (Railway provides)
BACKEND_URL=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}

# Reference private domain for internal communication
INTERNAL_API=http://${{backend.RAILWAY_PRIVATE_DOMAIN}}

# Railway automatically provides PORT - don't set manually
# Let Railway inject PORT, app reads from process.env.PORT
```

---

## 🔴 ISSUE 5: Health Check Configuration

### Common Error Pattern:
```
Health check failed: service unavailable
```

### Correct Solution:

#### 1. Add Health Endpoint:
```javascript
// Express.js
app.get('/api/health', (req, res) => {
  res.status(200).json({ status: 'healthy' });
});

// Python Flask
@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'}), 200
```

#### 2. Configure in railpack.json:
```json
{
  "deploy": {
    "healthCheckPath": "/api/health",
    "healthCheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

---

## 🔴 ISSUE 6: Monorepo Service Confusion

### Common Error Pattern:
```
Nixpacks unable to generate build plan
Multiple services detected
```

### Correct Solution:

#### Separate railpack.json for Each Service:
```bash
# Project structure
/
├── backend/
│   └── railpack.json  # Backend-specific config
├── frontend/
│   └── railpack.json  # Frontend-specific config
└── railpack.json      # Root config (if needed)
```

#### Root railpack.json for Monorepo:
```json
{
  "version": "1",
  "services": {
    "backend": {
      "root": "./backend",
      "build": {
        "provider": "python"
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
ls -la | grep -E "(Dockerfile|railway\.toml|nixpacks\.toml|railpack\.json)"

# 2. Validate railpack.json syntax
cat railpack.json | jq '.' > /dev/null && echo "✅ Valid JSON"

# 3. Verify PORT usage in code
grep -r "process.env.PORT\|PORT" . | grep -v node_modules

# 4. Check host binding
grep -r "0\.0\.0\.0\|localhost\|127\.0\.0\.1" . | grep -E "(listen|HOST|host)"

# 5. Verify health endpoint exists
grep -r "/health\|/api/health" . | grep -v node_modules

# 6. Test build locally
yarn build && PORT=3000 yarn start

# 7. Create git hook for validation
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
if [ -f railpack.json ]; then
  jq '.' railpack.json > /dev/null || exit 1
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

1. Always use railpack.json as the primary build configuration
2. Never hardcode ports - always use process.env.PORT
3. Always bind to 0.0.0.0 not localhost or 127.0.0.1
4. Apply theme before React renders to prevent flash of unstyled content
5. Reference domains not ports in Railway variables (${{service.RAILWAY_PUBLIC_DOMAIN}})
6. Include health check endpoint at /api/health returning 200 status
7. Remove competing build files (Dockerfile, railway.toml) when using railpack.json
8. Test locally with Railway environment: railway run yarn dev
9. Validate JSON syntax before committing railpack.json
10. Use inputs field only for layer references in railpack.json, not for basic installs
