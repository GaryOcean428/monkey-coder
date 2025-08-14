# Monkey Coder Publishing Guide

## Package Version Status (as of 2025-01-14)

| Package | Registry | Published Version | Local Version | Status |
|---------|----------|------------------|---------------|---------|
| monkey-coder-cli | npm | 1.4.0 | 1.4.0 | ✅ Up to date |
| monkey-coder-sdk | npm | 1.3.4 | 1.3.6 | ⚠️ Needs publish |
| monkey-coder-core | PyPI | 1.0.4 | 1.1.0 | ⚠️ Needs publish |
| monkey-coder-sdk | PyPI | 1.0.1 | 1.1.0 | ⚠️ Needs publish |

## Unified SDK Distribution Strategy

The SDK is published to both npm and PyPI for maximum developer reach:

### For TypeScript/JavaScript Developers
- **Package**: `monkey-coder-sdk` on npm
- **Install**: `npm install monkey-coder-sdk`
- **Documentation**: https://docs.monkeycoder.dev/sdk/typescript

### For Python Developers
- **Package**: `monkey-coder-sdk` on PyPI
- **Install**: `pip install monkey-coder-sdk`
- **Documentation**: https://docs.monkeycoder.dev/sdk/python

### Unified Features
Both SDKs provide:
- Complete API client implementation
- Type-safe interfaces
- Async/await support
- Streaming responses
- Error handling
- Authentication management
- Provider abstraction

## Publishing Workflow

### Prerequisites

1. **npm Authentication**:
   ```bash
   npm login
   ```

2. **PyPI Authentication**:
   ```bash
   # Install twine if not already installed
   pip install twine
   
   # Configure PyPI credentials
   # Create ~/.pypirc with your credentials or use keyring
   ```

3. **Version Synchronization**:
   - CLI and SDK TypeScript versions can be independent
   - Python SDK should match TypeScript SDK major.minor version
   - Core Python package can version independently

### Publishing Commands

#### 1. Publish CLI to npm (if updated)
```bash
cd packages/cli
npm version patch  # or minor/major
npm publish
git add package.json
git commit -m "chore(cli): bump version to $(grep version package.json | cut -d'"' -f4)"
```

#### 2. Publish TypeScript SDK to npm
```bash
cd packages/sdk
npm version patch  # Bump from 1.3.4 to 1.3.6
npm run build:ts
npm publish
git add package.json
git commit -m "chore(sdk): bump TypeScript version to $(grep version package.json | cut -d'"' -f4)"
```

#### 3. Publish Core to PyPI
```bash
cd packages/core

# Update version in pyproject.toml
# Current: 1.0.4 → 1.1.0

# Build the package
python -m build

# Upload to PyPI
python -m twine upload dist/*

# Clean up
rm -rf dist/ *.egg-info/

git add pyproject.toml
git commit -m "chore(core): bump version to 1.1.0"
```

#### 4. Publish Python SDK to PyPI
```bash
cd packages/sdk/src/python

# Update version in setup.py
# Current: 1.0.1 → 1.1.0

# Build the package
python setup.py sdist bdist_wheel

# Upload to PyPI
python -m twine upload dist/*

# Clean up
rm -rf dist/ build/ *.egg-info/

git add setup.py
git commit -m "chore(sdk-python): bump version to 1.1.0"
```

## Automated Publishing Script

Use the provided `scripts/publish-all.sh` script to publish all packages:

```bash
# Publish all packages with version bumps
./scripts/publish-all.sh

# Publish only specific packages
./scripts/publish-all.sh --only-npm
./scripts/publish-all.sh --only-pypi
```

## Version Management Best Practices

### Semantic Versioning
- **MAJOR**: Breaking API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Version Alignment
- TypeScript and Python SDKs should maintain feature parity
- Major and minor versions should align between SDK implementations
- Patch versions can differ for platform-specific fixes

### Release Notes
Always update CHANGELOG.md with:
- Version number and date
- New features
- Bug fixes
- Breaking changes
- Migration guides (for major versions)

## Troubleshooting

### npm Publishing Issues

**Error: 402 Payment Required**
- Ensure the package name is not taken
- Check if you need to use a scoped package name

**Error: 403 Forbidden**
- Verify you're logged in: `npm whoami`
- Check package ownership: `npm owner ls monkey-coder-sdk`

### PyPI Publishing Issues

**Error: Invalid distribution**
- Ensure setup.py/pyproject.toml is valid
- Check that all required files are present
- Verify Python version compatibility

**Error: Version already exists**
- PyPI doesn't allow re-uploading the same version
- Bump the version number and try again

## CI/CD Integration

### GitHub Actions Workflow
The repository includes `.github/workflows/publish.yml` for automated publishing:

```yaml
name: Publish Packages

on:
  release:
    types: [published]
  workflow_dispatch:
    inputs:
      packages:
        description: 'Packages to publish'
        required: true
        default: 'all'
        type: choice
        options:
          - all
          - npm-only
          - pypi-only

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - uses: actions/setup-python@v4
      - run: ./scripts/publish-all.sh
```

## Package Registry Links

### npm Packages
- [monkey-coder-cli](https://www.npmjs.com/package/monkey-coder-cli)
- [monkey-coder-sdk](https://www.npmjs.com/package/monkey-coder-sdk)

### PyPI Packages
- [monkey-coder-core](https://pypi.org/project/monkey-coder-core/)
- [monkey-coder-sdk](https://pypi.org/project/monkey-coder-sdk/)

## Contact

For publishing access or issues:
- GitHub: https://github.com/GaryOcean428/monkey-coder
- Email: support@monkeycoder.dev