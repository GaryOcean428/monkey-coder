[← Back to Roadmap Index](../roadmap.md)

## Development Workflow

### Local Development Setup

**Prerequisites:**

```bash
# System requirements
node >= 18.0.0
Python >= 3.8
yarn >= 4.9.2
Docker >= 24.0.0
git >= 2.40.0

# Environment setup
cp .env.example .env
# Configure required API keys:
# OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY
```

**Installation:**

```bash
# Clone and setup
git clone https://github.com/GaryOcean428/monkey-coder.git
cd monkey-coder
yarn install

# Build all packages
yarn build

# Run tests
yarn test

# Start development servers
yarn dev  # Starts CLI, core, and web development servers
```

### Development Commands

**Core Development:**

```bash
# CLI development
cd packages/cli
yarn dev          # Watch mode for CLI development
yarn typecheck    # TypeScript validation
yarn lint:fix     # Fix linting issues

# Python core development
cd packages/core
Python -m pytest -v                    # Run tests
Python -m pytest --cov=monkey_coder   # Coverage
black .                                # Format code
mypy monkey_coder                      # Type checking

# SDK development
cd packages/sdk
yarn build:ts      # Build TypeScript SDK
yarn build:Python # Build Python SDK
yarn examples:node # Test Node.js examples
```

**Quality Assurance:**

```bash
# Run all quality checks
yarn lint          # Lint all packages
yarn typecheck     # TypeScript checking
yarn test:coverage # Test with coverage
yarn format:check  # Code formatting validation

# Markdown documentation
yarn lint:md       # Lint markdown files
yarn lint:md:fix   # Fix markdown issues
```

### IDE Configuration

**VS Code Settings (`.vscode/settings.JSON`):**

```json
{
  "TypeScript.preferences.importModuleSpecifier": "relative",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "Python.defaultInterpreterPath": "./packages/core/.venv/bin/Python",
  "Python.linting.enabled": true,
  "Python.linting.mypyEnabled": true,
  "Python.formatting.provider": "black"
}
```

**Recommended Extensions:**
- TypeScript and JavaScript Language Features
- Python Extension Pack
- Prettier - Code formatter
- ESLint
- Black Formatter
- YAML Support
