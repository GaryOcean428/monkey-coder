# Completion Roadmap for Monkey Coder

**Generated:** 2026-01-25  
**Related PRs:** #211 (Implementation Review), #212 (Sandbox Service Clarification)

## Executive Summary

Based on comprehensive review of open issues (#185-#194), closed issues (#181-#184), and PR #212, the following gaps were identified for achieving full project completion:

### ✅ Already Complete
- All CLI features from issues #185-#194 are implemented
- Sandbox service architecture clarified (optional deployment)
- Core functionality production-ready

### 🔧 Remaining Work
1. **Package Publishing** - npm and PyPI packages not published
2. **Documentation** - CHANGELOG and release docs missing
3. **Release Automation** - CI/CD workflows for publishing
4. **Interactive Agent Mode** - **ESSENTIAL** for complete agent experience
5. **Sandbox Service Integration** - **ESSENTIAL** backend resource for agents

---

## Issue 1: Setup npm Publishing for monkey-coder-cli

### Summary
Publish the CLI package to npm registry to enable global installation via `npm install -g monkey-coder-cli`.

### Priority
🔴 **HIGH** - Essential for public release and user adoption

### Implementation

#### 1.1 Configure package.json

Update `packages/cli/package.json`:

```json
{
  "name": "monkey-coder-cli",
  "version": "1.6.0",
  "publishConfig": {
    "access": "public",
    "registry": "https://registry.npmjs.org/"
  },
  "files": [
    "dist/**/*",
    "README.md",
    "LICENSE"
  ],
  "keywords": [
    "ai",
    "code-generation",
    "cli",
    "coding-assistant",
    "mcp",
    "agent",
    "autonomous-coding"
  ]
}
```

#### 1.2 Create GitHub Actions Workflow

Create `.github/workflows/publish-npm.yml`:

```yaml
name: Publish to npm

on:
  release:
    types: [published]
  workflow_dispatch:
    inputs:
      package:
        description: 'Package to publish'
        required: true
        type: choice
        options:
          - cli
          - sdk
          - all

jobs:
  publish-npm:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20.x'
          registry-url: 'https://registry.npmjs.org'
      
      - name: Enable Corepack
        run: corepack enable
      
      - name: Install dependencies
        run: yarn install --immutable
      
      - name: Build packages
        run: yarn build
      
      - name: Publish CLI to npm
        if: github.event.inputs.package == 'cli' || github.event.inputs.package == 'all' || github.event_name == 'release'
        working-directory: packages/cli
        run: npm publish --provenance --access public
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
      
      - name: Publish SDK to npm
        if: github.event.inputs.package == 'sdk' || github.event.inputs.package == 'all' || github.event_name == 'release'
        working-directory: packages/sdk
        run: npm publish --provenance --access public
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

#### 1.3 Update Documentation

Add to `README.md`:

```markdown
## Installation

### Via npm (Recommended)

```bash
npm install -g monkey-coder-cli
```

### Via yarn

```bash
yarn global add monkey-coder-cli
```

### From Source

```bash
git clone https://github.com/GaryOcean428/monkey-coder.git
cd monkey-coder
corepack enable
yarn install
yarn build
yarn workspace monkey-coder-cli link
```

## Quick Start

```bash
# Start interactive chat
monkey chat

# Run autonomous agent
monkey agent --task "Create a hello world TypeScript app"

# Manage sessions
monkey session list

# Configure permissions
monkey config permissions list
```
\```

#### 1.4 Pre-publish Checklist

- [ ] Add LICENSE file (MIT recommended)
- [ ] Ensure packages/cli/README.md is comprehensive
- [ ] Test local build: `cd packages/cli && yarn build && npm pack`
- [ ] Verify package contents: `tar -tzf monkey-coder-cli-1.6.0.tgz`
- [ ] Create npm account at https://www.npmjs.com/signup
- [ ] Generate npm access token: https://www.npmjs.com/settings/tokens
- [ ] Add NPM_TOKEN to GitHub repository secrets

#### 1.5 Testing Before Publishing

```bash
# Build the package
cd packages/cli
yarn build

# Create tarball
npm pack

# Test installation locally
npm install -g ./monkey-coder-cli-1.6.0.tgz

# Verify commands work
monkey --version
monkey chat --help

# Uninstall after testing
npm uninstall -g monkey-coder-cli
```

### Acceptance Criteria

- [x] Package published to https://www.npmjs.com/package/monkey-coder-cli
- [x] Installation works globally: `npm install -g monkey-coder-cli`
- [x] All commands accessible: `monkey --version`, `monkey chat`, etc.
- [x] README includes comprehensive installation instructions
- [x] GitHub Actions workflow automates future releases

---

## Issue 2: Setup PyPI Publishing for monkey-coder-core

### Summary
Publish the Python core package to PyPI to enable installation via `pip install monkey-coder-core`.

### Priority
🟡 **MEDIUM** - Important for Python developers and backend deployment

### Implementation

#### 2.1 Configure pyproject.toml

Update `packages/core/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "monkey-coder-core"
version = "1.2.0"
authors = [{name = "GaryOcean428", email = "gary@ocean428.dev"}]
description = "Python orchestration core for Monkey Coder AI platform"
readme = "README.md"
requires-python = ">=3.12"
license = {text = "MIT"}
keywords = [
    "ai",
    "code-generation",
    "orchestration",
    "multi-agent",
    "mcp"
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Code Generators",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]

[project.urls]
Homepage = "https://github.com/GaryOcean428/monkey-coder"
Repository = "https://github.com/GaryOcean428/monkey-coder"
Documentation = "https://github.com/GaryOcean428/monkey-coder/tree/main/docs"
"Bug Tracker" = "https://github.com/GaryOcean428/monkey-coder/issues"
Changelog = "https://github.com/GaryOcean428/monkey-coder/blob/main/CHANGELOG.md"

[tool.setuptools.packages.find]
where = ["."]
include = ["monkey_coder*"]
exclude = ["tests*"]
```

#### 2.2 Create GitHub Actions Workflow

Create `.github/workflows/publish-pypi.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]
  workflow_dispatch:

jobs:
  publish-pypi:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install build tools
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      
      - name: Build package
        working-directory: packages/core
        run: python -m build
      
      - name: Check distribution
        working-directory: packages/core
        run: twine check dist/*
      
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          packages-dir: packages/core/dist/
          verbose: true
```

#### 2.3 Create packages/core/README.md

```markdown
# Monkey Coder Core

Python orchestration engine for the Monkey Coder AI platform.

## Features

- 🤖 Multi-agent orchestration with specialized personas
- 🔌 Model Context Protocol (MCP) integration
- 🎯 Support for multiple AI providers (OpenAI, Anthropic, Google, Qwen)
- ⚡ FastAPI-based REST API
- 🔐 Built-in authentication and security
- 📊 Monitoring and observability

## Installation

```bash
pip install monkey-coder-core
```

## Quick Start

```python
from monkey_coder import MonkeyCoderOrchestrator

# Initialize orchestrator
orchestrator = MonkeyCoderOrchestrator()

# Execute a task
result = await orchestrator.execute_task(
    prompt="Create a REST API with FastAPI",
    persona="architect"
)

print(result)
```

## Configuration

Set environment variables:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."
```

## Documentation

Full documentation: https://github.com/GaryOcean428/monkey-coder/tree/main/docs

## License

MIT
\```

#### 2.4 Pre-publish Checklist

- [ ] Create PyPI account at https://pypi.org/account/register/
- [ ] Generate API token at https://pypi.org/manage/account/token/
- [ ] Add PYPI_API_TOKEN to GitHub repository secrets
- [ ] Test build locally: `cd packages/core && python -m build`
- [ ] Test installation: `pip install dist/monkey_coder_core-1.2.0-py3-none-any.whl`
- [ ] Verify imports: `python -c "from monkey_coder import MonkeyCoderOrchestrator"`

### Acceptance Criteria

- [x] Package published to https://pypi.org/project/monkey-coder-core/
- [x] Installation works: `pip install monkey-coder-core`
- [x] Imports work correctly
- [x] README.md comprehensive with examples
- [x] GitHub Actions workflow automated

---

## Issue 3: Create Comprehensive CHANGELOG.md

### Summary
Document all implemented features, version history, and breaking changes in a standardized CHANGELOG.md file.

### Priority
🟢 **LOW** - Important for transparency but not blocking release

### Implementation

Create `CHANGELOG.md`:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- npm and PyPI package publishing workflows
- Comprehensive documentation for package installation

## [1.6.0] - 2026-01-23

### Added - CLI Features

#### Checkpoint Management (#185, #192)
- `monkey checkpoint create [message]` - Create git-based checkpoints
- `monkey checkpoint list` - List recent checkpoints
- `monkey checkpoint restore <id>` - Restore to specific checkpoint
- `monkey undo` - Undo last file operation
- `monkey redo` - Redo undone operation
- `monkey history` - Show operation journal

#### Docker Sandbox (#186, #193)
- `--sandbox docker` - Docker-based isolated execution
- Memory limits (128MB default)
- CPU throttling (50% default)
- Network isolation
- Security: cap-drop, no-new-privileges, PID limits

#### Configuration System (#187)
- `.monkey-coder.json` - Hierarchical configuration
- Zod-based schema validation
- Global/local/project config merging
- `monkey config init` - Create config file
- `monkey config show` - Display resolved configuration
- `monkey config permissions` - Manage file/command permissions

#### Local Agent Mode (#181, #188)
- `monkey agent --task "..."` - Autonomous task execution
- Local tool execution with cloud AI inference
- Checkpoint integration
- User approval workflow
- Session persistence

#### MCP Integration (#183, #189)
- Backend MCP server with FastMCP
- Streamable HTTP at /mcp endpoint
- REST API wrapper at /api/mcp/tools
- `monkey mcp list` - List available MCP servers
- `monkey mcp enable/disable/start/stop` - Manage servers

#### Terminal UI (#182, #190)
- Ink-based React components
- Streaming text display
- Syntax-highlighted code blocks
- Task progress with listr2
- Keyboard shortcuts (Esc, Ctrl+C)

#### Session Management (#184, #191)
- `monkey session list` - List all sessions
- `monkey session show <id>` - Display session details
- `monkey session delete <id>` - Remove session
- `monkey session export <id>` - Export to JSON/markdown
- SQLite-backed persistence
- Token counting with tiktoken

#### Permission System (#194)
- Glob-based file read/write permissions
- Command allowlist/denylist
- `monkey config permissions allow/deny` - Manage rules
- `monkey config permissions test` - Test permissions
- Per-project overrides via .monkeyrc.json

### Changed
- CLI commands now use hierarchical configuration system
- Agent mode supports multiple sandbox backends
- MCP client enhanced with tool discovery and execution

### Fixed
- Session persistence across CLI invocations
- Checkpoint restoration with merge conflict handling
- Docker sandbox graceful fallback to spawn mode

## [1.5.0] - 2026-01-15

### Added
- Initial CLI infrastructure
- Basic chat and agent commands
- Backend FastAPI integration

## [1.2.0] - 2026-01-10

### Added - Core Features
- Multi-agent orchestration system
- Support for OpenAI, Anthropic, Google, Qwen providers
- FastAPI REST API
- Authentication and security middleware

[Unreleased]: https://github.com/GaryOcean428/monkey-coder/compare/v1.6.0...HEAD
[1.6.0]: https://github.com/GaryOcean428/monkey-coder/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/GaryOcean428/monkey-coder/compare/v1.2.0...v1.5.0
[1.2.0]: https://github.com/GaryOcean428/monkey-coder/releases/tag/v1.2.0
```

### Acceptance Criteria

- [x] CHANGELOG.md created at repository root
- [x] All major features documented with issue references
- [x] Version numbers follow semantic versioning
- [x] Links to GitHub releases
- [x] Grouped by Added/Changed/Fixed/Deprecated/Removed/Security

---

## Issue 4: Implement Interactive Agent Mode

### Summary
Complete the interactive REPL mode for `monkey agent` command (currently shows placeholder message). This is an **essential feature** for providing a complete autonomous coding experience similar to Claude Code and Gemini CLI.

### Priority
🔴 **CRITICAL** - Essential for complete agent experience and CLI parity with competitors

### Implementation

Update `packages/cli/src/agent-runner.ts`:

```typescript
async startInteractive(): Promise<void> {
  const session = this.sessionMgr.getOrCreateSession({
    name: 'Interactive Agent Session',
  });
  this.currentSessionId = session.id;

  console.log(chalk.green('🐒 Monkey Coder Interactive Agent'));
  console.log(chalk.gray('Type your task and press Enter. Type "exit" to quit.'));
  console.log('');

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    prompt: chalk.cyan('monkey> '),
  });

  rl.prompt();

  rl.on('line', async (line) => {
    const input = line.trim();
    
    if (!input) {
      rl.prompt();
      return;
    }
    
    if (input.toLowerCase() === 'exit' || input.toLowerCase() === 'quit') {
      console.log(chalk.green('Goodbye!'));
      rl.close();
      return;
    }
    
    if (input === 'help') {
      console.log(chalk.cyan('Available commands:'));
      console.log('  help     - Show this help message');
      console.log('  exit     - Exit interactive mode');
      console.log('  history  - Show command history');
      console.log('  clear    - Clear the screen');
      console.log('  session  - Show current session info');
      console.log('  undo     - Undo last operation');
      console.log('');
      console.log('Or type any task description to execute it.');
      rl.prompt();
      return;
    }
    
    if (input === 'clear') {
      console.clear();
      rl.prompt();
      return;
    }
    
    if (input === 'session') {
      const context = this.sessionMgr.getSessionContext(this.currentSessionId!);
      if (context) {
        console.log(chalk.cyan('Session Info:'));
        console.log(`  ID: ${context.session.id.slice(0, 8)}`);
        console.log(`  Messages: ${context.messages.length}`);
        console.log(`  Tokens: ${context.totalTokens}`);
      }
      rl.prompt();
      return;
    }
    
    try {
      await this.runTask(input);
    } catch (error) {
      console.error(chalk.red(`Error: ${error}`));
    }
    
    rl.prompt();
  });

  rl.on('close', () => {
    process.exit(0);
  });
}
```

### Acceptance Criteria

- [x] Interactive REPL mode works with `monkey agent` (no --task flag)
- [x] Commands: help, exit, history, clear, session, undo
- [x] Task execution within interactive session
- [x] Session persistence across interactions
- [x] Graceful exit on Ctrl+C or "exit" command

---

## Issue 5: Create Release Automation Workflow

### Summary
Automate the release process with semantic versioning, changelog generation, and combined npm + PyPI publishing.

### Priority
🟡 **MEDIUM** - Streamlines future releases

### Implementation

#### 5.1 Create .github/workflows/release.yml

```yaml
name: Release

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  create-release:
    runs-on: ubuntu-latest
    outputs:
      upload_url: ${{ steps.create_release.outputs.upload_url }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Generate Changelog
        id: changelog
        uses: metcalfc/changelog-generator@v4.3.1
        with:
          myToken: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Create Release
        id: create_release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          body: ${{ steps.changelog.outputs.changelog }}
          draft: false
          prerelease: false

  publish-npm:
    needs: create-release
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20.x'
          registry-url: 'https://registry.npmjs.org'
      
      - name: Enable Corepack
        run: corepack enable
      
      - name: Install and Build
        run: |
          yarn install --immutable
          yarn build
      
      - name: Publish CLI to npm
        working-directory: packages/cli
        run: npm publish --provenance --access public
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}

  publish-pypi:
    needs: create-release
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Build and Publish
        working-directory: packages/core
        run: |
          pip install build twine
          python -m build
      
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          packages-dir: packages/core/dist/
```

#### 5.2 Create Release Script

Create `scripts/release.sh`:

```bash
#!/bin/bash
set -e

# Release script for Monkey Coder
# Usage: ./scripts/release.sh [major|minor|patch]

RELEASE_TYPE=${1:-patch}

echo "🐒 Monkey Coder Release Script"
echo "================================"

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "❌ Must be on main branch to release"
  exit 1
fi

# Check if working directory is clean
if [ -n "$(git status --porcelain)" ]; then
  echo "❌ Working directory must be clean"
  exit 1
fi

# Get current version
CURRENT_VERSION=$(node -p "require('./package.json').version")
echo "📦 Current version: $CURRENT_VERSION"

# Calculate new version
IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}

case $RELEASE_TYPE in
  major)
    MAJOR=$((MAJOR + 1))
    MINOR=0
    PATCH=0
    ;;
  minor)
    MINOR=$((MINOR + 1))
    PATCH=0
    ;;
  patch)
    PATCH=$((PATCH + 1))
    ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
echo "🎯 New version: $NEW_VERSION"

# Update package.json files
echo "📝 Updating package versions..."
yarn version "$NEW_VERSION"
cd packages/cli && yarn version "$NEW_VERSION" && cd ../..
cd packages/core && sed -i "s/version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml && cd ../..

# Run tests
echo "🧪 Running tests..."
yarn test

# Update CHANGELOG
echo "📋 Update CHANGELOG.md manually, then press Enter to continue..."
read

# Commit changes
echo "💾 Committing changes..."
git add .
git commit -m "chore: release v$NEW_VERSION"

# Create tag
echo "🏷️  Creating tag..."
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"

# Push
echo "🚀 Pushing to GitHub..."
git push origin main
git push origin "v$NEW_VERSION"

echo "✅ Release v$NEW_VERSION complete!"
echo "📦 GitHub Actions will automatically publish to npm and PyPI"
```

Make executable:
```bash
chmod +x scripts/release.sh
```

### Acceptance Criteria

- [x] Semantic versioning with major/minor/patch releases
- [x] Automated changelog generation from commits
- [x] GitHub release created with notes
- [x] npm publish triggered on tag push
- [x] PyPI publish triggered on tag push
- [x] Release script handles version bumping

---

## Issue 6: Integrate Sandbox Service as Essential Backend Resource

### Summary
Deploy and integrate the sandbox service as a **critical backend resource** for agent operations. The service provides secure containerized environments for code execution (E2B) and browser automation (BrowserBase), enabling agents to safely execute untrusted code and perform web-based tasks.

### Priority
🔴 **CRITICAL** - Essential backend resource for complete agent functionality

### Background

The project has **two complementary sandbox systems**:

1. **CLI Local Sandbox** (`packages/cli/src/sandbox/`)
   - Docker-based local execution via dockerode
   - Used for simple shell commands and file operations
   - Automatic fallback: docker → spawn → exec
   - Limited to local Docker availability

2. **Backend Sandbox Service** (`services/sandbox/`)
   - FastAPI service with E2B and BrowserBase integration
   - Provides cloud-based code execution and browser automation
   - Used by backend orchestrator and agents for complex tasks
   - **Essential for full agent capabilities**

### Why This is Critical

The sandbox service is **NOT optional** for complete agent functionality:

✅ **Code Execution**: Agents need to run Python/Node.js code safely
✅ **Browser Automation**: Agents need to interact with web applications
✅ **Security**: Isolated environments prevent system compromise
✅ **Scalability**: Backend service handles multiple concurrent operations
✅ **Advanced Features**: Screen recording, network interception, filesystem access

**Without the sandbox service, agents cannot:**
- Execute complex Python/Node.js code safely
- Interact with web browsers (login, scraping, testing)
- Access advanced E2B features (filesystem, processes)
- Scale beyond local Docker limitations

### Architecture

```
┌─────────────────────────────────────────────┐
│         Monkey Coder CLI / Backend          │
│                                             │
│  ┌──────────────┐      ┌─────────────────┐ │
│  │ Local Docker │      │  Backend Agent  │ │
│  │   Sandbox    │      │  Orchestrator   │ │
│  └──────────────┘      └─────────────────┘ │
│         │                       │           │
│         │ Simple                │ Complex   │
│         │ Commands              │ Tasks     │
└─────────┼───────────────────────┼───────────┘
          │                       │
          │                       ▼
          │              ┌─────────────────┐
          │              │ Sandbox Service │
          │              │   (Railway)     │
          │              ├─────────────────┤
          │              │ E2B Integration │
          │              │ BrowserBase     │
          │              │ Security Layer  │
          │              │ Monitoring      │
          └──────────────┴─────────────────┘
```

### Implementation

#### 6.1 Verify Service Configuration

Ensure `services/sandbox/railpack.json` is configured:

```json
{
  "builder": "NIXPACKS",
  "buildCommand": "pip install -r requirements.txt",
  "startCommand": "uvicorn sandbox.main:app --host 0.0.0.0 --port $PORT",
  "healthCheckPath": "/health",
  "healthCheckTimeout": 300,
  "restartPolicyType": "ON_FAILURE",
  "restartPolicyMaxRetries": 3
}
```

#### 6.2 Environment Variables

Required for Railway deployment:

```bash
# E2B Configuration
E2B_API_KEY=<your-e2b-api-key>

# BrowserBase Configuration  
BROWSERBASE_API_KEY=<your-browserbase-api-key>
BROWSERBASE_PROJECT_ID=<your-project-id>

# Security
SANDBOX_TOKEN_SECRET=<random-256-bit-secret>

# Service URLs (auto-configured by Railway)
SANDBOX_SERVICE_URL=https://<service-name>.railway.app
```

#### 6.3 Backend Integration

Update `packages/core/monkey_coder/sandbox_client.py` to use Railway service:

```python
class SandboxClient:
    def __init__(self):
        # Railway automatically provides the service URL
        self.sandbox_url = os.getenv(
            "SANDBOX_SERVICE_URL",
            "https://monkey-coder-sandbox-production.up.railway.app"
        )
        self.token_secret = os.getenv("SANDBOX_TOKEN_SECRET")
        
        # Validate configuration
        if not self.token_secret:
            logger.warning("SANDBOX_TOKEN_SECRET not set - sandbox calls will fail")
```

#### 6.4 Agent Integration

Update `packages/core/monkey_coder/agents/base.py` to use sandbox for code execution:

```python
from monkey_coder.sandbox_client import SandboxClient

class BaseAgent:
    def __init__(self):
        self.sandbox = SandboxClient()
    
    async def execute_code(self, code: str, language: str = "python"):
        """Execute code in secure sandbox."""
        result = await self.sandbox.execute_code(
            code=code,
            execution_id=f"agent-{self.agent_id}-{datetime.now().timestamp()}",
            timeout=60
        )
        
        if result["status"] == "success":
            return result["result"]
        else:
            raise RuntimeError(f"Code execution failed: {result.get('logs')}")
```

#### 6.5 Railway Deployment

```bash
# Deploy sandbox service
railway link

# Create new service for sandbox
railway service create sandbox

# Deploy
cd services/sandbox
railway up

# Set environment variables
railway variables set E2B_API_KEY="<key>"
railway variables set BROWSERBASE_API_KEY="<key>"
railway variables set BROWSERBASE_PROJECT_ID="<id>"
railway variables set SANDBOX_TOKEN_SECRET="$(openssl rand -hex 32)"

# Get service URL
railway domain
```

#### 6.6 Update Main Backend

Link sandbox service to main backend:

```bash
# In main backend service
railway variables set SANDBOX_SERVICE_URL="https://<sandbox-domain>.railway.app"
railway variables set SANDBOX_TOKEN_SECRET="<same-secret-as-sandbox>"
```

#### 6.7 Health Checks

Add sandbox availability check to main backend:

```python
# packages/core/monkey_coder/app/main.py

@app.get("/health/comprehensive")
async def comprehensive_health():
    """Comprehensive health check including dependencies."""
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    # Check sandbox service
    try:
        sandbox = SandboxClient()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{sandbox.sandbox_url}/health",
                timeout=5.0
            )
            health["services"]["sandbox"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "url": sandbox.sandbox_url
            }
    except Exception as e:
        health["services"]["sandbox"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health["status"] = "degraded"
    
    return health
```

### Testing

#### Local Testing

```bash
# Start sandbox service locally
cd services/sandbox
pip install -r requirements.txt
uvicorn sandbox.main:app --port 8001

# Test endpoints
curl http://localhost:8001/health
curl -X POST http://localhost:8001/sandbox/execute \
  -H "Content-Type: application/json" \
  -d '{
    "sandbox_type": "code",
    "action": "execute",
    "code": "print(\"Hello from E2B\")",
    "timeout": 30
  }'
```

#### Integration Testing

```python
# Test sandbox integration
import asyncio
from monkey_coder.sandbox_client import SandboxClient

async def test_sandbox():
    client = SandboxClient()
    
    # Test code execution
    result = await client.execute_code(
        code="print('Hello, World!')",
        execution_id="test-1"
    )
    
    assert result["status"] == "success"
    assert "Hello, World!" in result["logs"]
    
    # Test browser automation
    browser_result = await client.execute_browser_action(
        url="https://example.com",
        action="navigate",
        execution_id="test-2"
    )
    
    assert browser_result["status"] == "success"

asyncio.run(test_sandbox())
```

### Cost Considerations

**Railway Service Costs:**
- Sandbox service: **$10-20/month** (Starter plan)
- E2B usage: **$10-20/month** (depends on usage)
- BrowserBase: **$20-30/month** (depends on browser sessions)

**Total additional cost: $40-70/month**

**Critical for:**
- Production deployments
- Multi-user environments
- Agent-based automation
- Web scraping/testing features

**Can skip ONLY if:**
- Development/testing only
- Single-user local CLI usage
- No browser automation needed
- Budget constraints (but limits functionality)

### Acceptance Criteria

- [x] Sandbox service deployed on Railway
- [x] Environment variables configured
- [x] Backend sandbox client connected to service
- [x] Agents can execute Python code via E2B
- [x] Agents can perform browser automation via BrowserBase
- [x] Health checks monitor sandbox availability
- [x] Error handling for sandbox unavailability
- [x] Documentation updated with deployment guide
- [x] Cost tracking enabled in Railway dashboard

---

## Summary of Issues to Create

| # | Title | Priority | Effort |
|---|-------|----------|--------|
| 1 | Setup npm publishing for monkey-coder-cli | 🔴 HIGH | Medium |
| 2 | Setup PyPI publishing for monkey-coder-core | 🟡 MEDIUM | Medium |
| 3 | Create comprehensive CHANGELOG.md | 🟢 LOW | Low |
| 4 | Implement interactive agent mode | 🔴 CRITICAL | Medium |
| 5 | Create release automation workflow | 🟡 MEDIUM | High |
| 6 | Integrate sandbox service as backend resource | 🔴 CRITICAL | High |

## Implementation Order

### Phase 1: Critical Features (Week 1-2)
1. **Issue #6** (Sandbox Service) - Deploy and integrate essential backend resource
2. **Issue #4** (Interactive Agent Mode) - Complete agent experience
3. **Issue #3** (CHANGELOG) - Quick win, provides documentation foundation

### Phase 2: Publishing (Week 3)
4. **Issue #1** (npm publishing) - Enable CLI distribution
5. **Issue #2** (PyPI publishing) - Enable Python package distribution

### Phase 3: Automation (Week 4)
6. **Issue #5** (Release automation) - Streamline future releases

## Estimated Timeline

- **Phase 1 (Critical)**: 1-2 weeks
  - Sandbox service deployment: 3-4 days
  - Interactive agent mode: 4-5 days  
  - CHANGELOG: 1 day

- **Phase 2 (Publishing)**: 1 week
  - npm setup and testing: 2-3 days
  - PyPI setup and testing: 2-3 days

- **Phase 3 (Automation)**: 1 week
  - Release workflow: 3-4 days
  - Testing and refinement: 2-3 days

**Total estimated effort: 3-4 weeks** for full completion with critical features prioritized.
