# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
python -m pytest                    # Run tests
python -m pytest -v                 # Verbose tests
python -m pytest --cov=monkey_coder # Coverage
black .                             # Format code
isort .                             # Sort imports
mypy monkey_coder                   # Type checking

# SDK package (TypeScript + Python)
cd packages/sdk
yarn build:ts      # Build TypeScript SDK
yarn build:python  # Build Python SDK
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
- **packages/cli/**: TypeScript CLI with Commander.js, providing commands like `implement`, `analyze`, `build`, `test`, and `chat`
- **packages/core/**: Python FastAPI orchestration engine with multi-agent support, MCP integration, and quantum task execution
- **packages/sdk/**: Dual TypeScript/Python SDK for API integration
- **packages/web/**: Next.js web interface (optional)
- **docs/**: Docusaurus documentation site with interactive examples
- **services/**: Optional microservices (sandbox execution)

### Key Technologies
- **Frontend**: TypeScript, Commander.js, Chalk, Ora (CLI); Next.js, React (Web)
- **Backend**: Python 3.8+, FastAPI, Pydantic, asyncio
- **AI Integration**: OpenAI, Anthropic, Google GenAI, Groq, Qwen-Agent
- **Infrastructure**: Docker, Railway deployment, Sentry monitoring
- **Testing**: Jest (TypeScript), Pytest (Python)

### Core Components

#### CLI Architecture (`packages/cli/`)
- **cli.ts**: Main command dispatcher with authentication hooks
- **api-client.ts**: HTTP client for backend communication with streaming support
- **config.ts**: Configuration management with file persistence
- **commands/**: Modular command implementations (auth, usage, mcp)
- **splash.ts**: ASCII art splash screen (can be disabled with `--no-splash`)

#### Python Core (`packages/core/`)
- **monkey_coder/core/orchestrator.py**: Multi-agent task orchestration
- **monkey_coder/core/quantum_executor.py**: Advanced quantum task execution
- **monkey_coder/mcp/**: Model Context Protocol server management
- **monkey_coder/providers/**: AI provider adapters (OpenAI, Anthropic, etc.)
- **monkey_coder/agents/**: Specialized agent implementations
- **monkey_coder/billing/**: Stripe integration for usage tracking

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
The CLI stores configuration in `~/.monkey-coder/config.json`:
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
python -m pytest tests/test_quantum.py

# Test with debugging
yarn test --verbose
python -m pytest -v -s

# Integration tests
python -m pytest -m integration
```

## Development Workflow

### Authentication Flow
Commands requiring API access (`implement`, `analyze`, `build`, `test`, `chat`) automatically check for authentication:
1. Check for `--api-key` flag
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
- **monkey-coder-core** (PyPI): v1.0.3 - Python orchestration core
- **monkey-coder-sdk** (PyPI): v1.0.1 - Python SDK
- **monkey-coder-cli** (npm): v1.1.0 - TypeScript CLI (ready to publish)

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
1. **Build failures**: Check TypeScript compilation with `yarn typecheck`
2. **Python import errors**: Ensure virtual environment is activated
3. **API authentication**: Use `monkey auth status` to check login state
4. **Streaming issues**: Check network connectivity and timeout settings

### Debug Commands
```bash
# CLI debug mode
monkey --verbose implement "your prompt"

# Python debugging
python -m monkey_coder.core.orchestrator --debug

# Check health
monkey health
```

### Log Locations
- CLI logs: Console output with colored formatting
- Python logs: `packages/core/data/logs/`
- Sentry: Centralized error tracking in production

## Commit Conventions

Follow conventional commits with these scopes:
- `feat(cli)`: New CLI features
- `fix(core)`: Python core bug fixes
- `docs`: Documentation updates
- `test(sdk)`: SDK test additions
- `chore(deps)`: Dependency updates

Valid commit types: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, `test`