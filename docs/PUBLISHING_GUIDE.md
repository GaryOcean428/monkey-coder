# Monkey Coder Publishing Guide

This guide covers the publishing process for both the Python (PyPI) and TypeScript (NPM) packages.

## Prerequisites

### Environment Setup
Ensure you have the following environment variables set:
```bash
export PYPI_TOKEN="your-pypi-token"
export NPM_ACCESS_TOKEN="your-npm-token"
```

### Tools Required
- Python 3.8+
- Node.js 18+
- Yarn
- Git

## Package Validation

Before publishing, run the validation script to ensure everything is properly configured:

```bash
./scripts/validate-packages.sh
```

This script will check:
- Package structure and files
- Dependencies
- Build processes
- Version numbers
- Authentication tokens

## Publishing Process

### 1. Python Core Package (monkey-coder-core)

#### Current Version: 1.0.3 ✅ Published

**Features Included:**
- Complete multi-agent framework
- MCP (Model Context Protocol) integration
- Built-in MCP servers (filesystem, github, browser, database)
- Advanced routing system
- Model validation and compatibility
- Sentry error tracking
- Quantum execution framework

**Package URL:** https://pypi.org/project/monkey-coder-core/1.0.3/

**Publish Command:**
```bash
./scripts/publish-pypi.sh  # Publishes both Python packages
```

**Manual Publishing (if script fails):**
```bash
cd packages/core
python -m pip install --upgrade build twine
python -m build
python -m twine upload dist/* --username __token__ --password $PYPI_TOKEN
```

**After Publishing:**
```bash
# Test installation
pip install monkey-coder-core

# Verify
python -c "import monkey_coder; print(monkey_coder.__version__)"
```

### 2. Python SDK Package (monkey-coder-sdk)

#### Current Version: 1.0.1 ✅ Published

**Features Included:**
- Python SDK for Monkey Coder API
- Client authentication
- API helpers and types
- Request/response handling

**Package URL:** https://pypi.org/project/monkey-coder-sdk/1.0.1/

**Manual Publishing (if script fails):**
```bash
cd packages/sdk/src/python
python -m pip install --upgrade build twine
python -m build
python -m twine upload dist/* --username __token__ --password $PYPI_TOKEN
```

**After Publishing:**
```bash
# Test installation
pip install monkey-coder-sdk

# Verify SDK
python -c "import monkey_coder_sdk; print('SDK installed successfully')"
```

### 3. TypeScript CLI Package (monkey-coder-cli)

#### Current Version: 1.0.0 ✅ Published

**Features Included:**
- Complete CLI interface
- Authentication system (login/logout/status)
- Usage tracking and billing
- MCP server management commands
- Streaming support
- Interactive chat mode

**Package Name:** `monkey-coder-cli` (unscoped for personal NPM account)

**Publish Command:**
```bash
./scripts/publish-npm.sh
```

**Manual Publishing (if script fails):**
```bash
cd packages/cli
yarn install
yarn build
yarn config set npmAuthToken $NPM_ACCESS_TOKEN
yarn npm publish --access public
```

**After Publishing:**
```bash
# Test installation
npm install -g monkey-coder-cli

# Verify
monkey --version
```

## Post-Publishing Checklist

### 1. Verify Package Availability
- [x] Check PyPI Core: https://pypi.org/project/monkey-coder-core/
- [x] Check PyPI SDK: https://pypi.org/project/monkey-coder-sdk/
- [x] Check NPM: https://www.npmjs.com/package/monkey-coder-cli

### 2. Test Installation
```bash
# Create a test environment
python -m venv test_env
source test_env/bin/activate

# Install all packages
pip install monkey-coder-core
pip install monkey-coder-sdk
npm install -g monkey-coder-cli  # After publishing

# Test basic functionality
monkey --help
monkey health
monkey auth status
monkey mcp list
```

### 3. Update Documentation
- [x] Update README.md with installation instructions
- [x] Update version numbers in documentation
- [ ] Create release notes

### 4. Git Tagging
```bash
# Tag the releases
git tag -a core-v1.0.3 -m "Release monkey-coder-core v1.0.3"
git tag -a sdk-v1.0.1 -m "Release monkey-coder-sdk v1.0.1"
git tag -a cli-v1.0.0 -m "Release monkey-coder-cli v1.0.0"

# Push tags
git push origin --tags
```

### 5. GitHub Release
Create releases on GitHub with:
- Release notes
- Key features
- Breaking changes (if any)
- Migration guide (if needed)

## Version Management

### Updating Versions

**Python Core Package:**
```bash
# Edit packages/core/pyproject.toml
# Update version = "X.Y.Z"
```

**Python SDK Package:**
```bash
# Edit packages/sdk/src/python/setup.py
# Update version="X.Y.Z"
```

**TypeScript CLI Package:**
```bash
# Edit packages/cli/package.json
# Update "version": "X.Y.Z"
```

### Versioning Strategy
- **Major (X.0.0)**: Breaking changes
- **Minor (0.X.0)**: New features, backward compatible
- **Patch (0.0.X)**: Bug fixes, patches

## Troubleshooting

### PyPI Issues
1. **Authentication Failed**
   - Verify token starts with `pypi-`
   - Check token permissions on PyPI

2. **Package Name Conflict**
   - Package name might be taken
   - Consider using a different name

### NPM Issues
1. **Authentication Failed**
   - Verify NPM token is valid
   - Run `yarn npm whoami` to check auth

2. **Scope Access**
   - Package is now unscoped: `monkey-coder-cli`
   - No organization needed for personal publishing

### Build Issues
1. **TypeScript Build Fails**
   ```bash
   cd packages/cli
   yarn clean
   yarn install
   yarn build
   ```

2. **Python Core Build Fails**
   ```bash
   cd packages/core
   rm -rf dist/ build/ *.egg-info
   python -m build
   ```

3. **Python SDK Build Fails**
   ```bash
   cd packages/sdk/src/python
   rm -rf dist/ build/ *.egg-info
   python -m build
   ```

## Security Notes

### Token Management
- Never commit tokens to git
- Use environment variables
- Rotate tokens regularly
- Use scoped tokens when possible

### Package Security
- Review dependencies before publishing
- Run security audits:
  ```bash
  # Python
  pip audit
  
  # NPM
  npm audit
  ```

## Maintenance

### Regular Updates
1. Update dependencies monthly
2. Address security vulnerabilities immediately
3. Monitor usage and issues
4. Respond to user feedback

### Deprecation Policy
- Announce deprecations 3 months in advance
- Provide migration guides
- Support deprecated versions for 6 months

## Support Channels

- GitHub Issues: Bug reports and feature requests
- Discord: Community support
- Email: Critical security issues

## Analytics and Monitoring

### PyPI Statistics
- Core: https://pypistats.org/packages/monkey-coder-core
- SDK: https://pypistats.org/packages/monkey-coder-sdk

### NPM Statistics  
- CLI: https://npm-stat.com/charts.html?package=monkey-coder-cli

### Error Tracking
- Sentry dashboard for runtime errors
- GitHub Issues for user-reported problems

## Next Steps After Publishing

1. **Announce the Release**
   - Blog post
   - Social media
   - Developer forums

2. **Update Examples**
   - Create example projects
   - Update tutorials
   - Record demo videos

3. **Monitor Feedback**
   - Watch GitHub issues
   - Monitor social media mentions
   - Respond to questions

4. **Plan Next Release**
   - Gather feature requests
   - Prioritize improvements
   - Set release schedule
