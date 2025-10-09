# UV Package Manager Setup

## Overview

This project now uses [uv](https://github.com/astral-sh/uv) for Python package management in the `packages/core` directory. UV is a fast Python package installer and resolver, written in Rust.

## Installation

### Linux/macOS
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Usage

### Install Dependencies
```bash
cd packages/core
uv sync
```

This will:
1. Create a virtual environment in `.venv/`
2. Install all dependencies from `pyproject.toml`
3. Generate/update `uv.lock` for reproducible builds

### Run Python with UV
```bash
# Run a Python command
uv run python -c "import monkey_coder; print('Success')"

# Run pytest
uv run pytest

# Run any Python script
uv run python your_script.py
```

### Add New Dependencies
```bash
# Add to dependencies
uv add package-name

# Add to dev dependencies
uv add --dev package-name
```

### Update Dependencies
```bash
# Update all dependencies
uv sync --upgrade

# Update specific package
uv add package-name@latest
```

## Configuration

### pyproject.toml
The Python project configuration is in `packages/core/pyproject.toml`:
- `requires-python = ">=3.12"` - Minimum Python version
- `[tool.uv]` section configures UV-specific settings
- `managed = true` enables UV project management

### uv.lock
The `uv.lock` file is committed to version control for reproducible builds. It contains:
- Exact versions of all dependencies
- Dependency resolution tree
- Source URLs and checksums

## Railway Deployment

When deploying to Railway with UV:

1. **Install UV in build step**:
```json
{
  "steps": {
    "install-uv": {
      "commands": [
        "curl -LsSf https://astral.sh/uv/install.sh | sh",
        "export PATH=\"$HOME/.local/bin:$PATH\""
      ]
    },
    "install-deps": {
      "commands": [
        "cd packages/core",
        "uv sync --frozen"
      ],
      "inputs": [{"step": "install-uv"}]
    }
  }
}
```

2. **Use UV in start command**:
```json
{
  "deploy": {
    "startCommand": "cd packages/core && uv run uvicorn monkey_coder.app.main:app --host 0.0.0.0 --port $PORT"
  }
}
```

## Benefits

### Speed
- 10-100x faster than pip for dependency resolution
- Parallel downloads and installs
- Efficient caching

### Reliability
- Reproducible builds with uv.lock
- Better dependency resolution
- Clear error messages

### Developer Experience
- Single command for setup (`uv sync`)
- Automatic virtual environment management
- Compatible with existing pip/pyproject.toml workflows

## Migration from pip

If you previously used pip:

1. Your existing `pyproject.toml` works as-is
2. Run `uv sync` to generate `uv.lock`
3. Commit `uv.lock` to version control
4. Update CI/CD to use UV commands

## Troubleshooting

### Command not found: uv
```bash
export PATH="$HOME/.local/bin:$PATH"
# Add to ~/.bashrc or ~/.zshrc for persistence
```

### Lock file out of sync
```bash
cd packages/core
uv sync --upgrade
```

### Virtual environment issues
```bash
cd packages/core
rm -rf .venv
uv sync
```

## References

- [UV Documentation](https://github.com/astral-sh/uv)
- [Python Packaging Guide](https://packaging.python.org/)
- [pyproject.toml Specification](https://peps.python.org/pep-0621/)
