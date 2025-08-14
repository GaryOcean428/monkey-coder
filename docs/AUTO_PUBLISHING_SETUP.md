# Automated Publishing Setup Guide

## Overview

Monkey Coder automatically publishes all packages on every commit to the main branch. This ensures users always have access to the latest features and fixes immediately.

## How It Works

1. **Every commit to main** triggers the GitHub Actions workflow
2. **Changed packages** are automatically detected
3. **Version numbers** are auto-incremented (patch version)
4. **Packages are built and published** to npm/PyPI
5. **Version bumps are committed** back to the repository

## Required GitHub Secrets

To enable auto-publishing, add these secrets to your GitHub repository:

### 1. NPM Token
1. Go to https://www.npmjs.com/
2. Sign in to your account
3. Click your profile → Access Tokens
4. Generate New Token → Classic Token
5. Select "Automation" type
6. Copy the token
7. Add to GitHub: Settings → Secrets → Actions → New repository secret
   - Name: `NPM_TOKEN`
   - Value: Your npm token

### 2. PyPI Token
1. Go to https://pypi.org/
2. Sign in to your account
3. Go to Account Settings → API tokens
4. Add API token → Scope: "Entire account" or specific projects
5. Copy the token (starts with `pypi-`)
6. Add to GitHub: Settings → Secrets → Actions → New repository secret
   - Name: `PYPI_TOKEN`
   - Value: Your PyPI token

## Workflow Features

### Automatic Version Bumping
- Every commit automatically increments the patch version
- Example: 1.3.6 → 1.3.7 → 1.3.8
- Commits with `[skip ci]` in the message won't trigger publishing

### Smart Change Detection
- Only publishes packages that have actual changes
- Detects changes in:
  - `packages/cli/` → publishes monkey-coder-cli to npm
  - `packages/sdk/` → publishes both npm and PyPI SDKs
  - `packages/core/` → publishes monkey-coder-core to PyPI

### Manual Force Publish
- Go to Actions → Auto-Publish Packages → Run workflow
- Select "Force publish all packages" to publish everything regardless of changes

## Version Management

### Automatic Versioning Rules
- **Patch**: Incremented automatically on every commit (1.0.0 → 1.0.1)
- **Minor**: Manually update before commit for new features (1.0.0 → 1.1.0)
- **Major**: Manually update before commit for breaking changes (1.0.0 → 2.0.0)

### Manual Version Updates
If you need to control the version:

```bash
# For npm packages
cd packages/cli
npm version minor  # or major
git add package.json
git commit -m "feat: new feature [skip ci]"

# For Python packages
# Edit pyproject.toml or setup.py manually
git commit -m "feat: new feature [skip ci]"
```

## Preventing Auto-Publish

Add `[skip ci]` to your commit message to skip automatic publishing:

```bash
git commit -m "docs: update README [skip ci]"
```

## Package Registry Status

View published packages:
- npm CLI: https://www.npmjs.com/package/monkey-coder-cli
- npm SDK: https://www.npmjs.com/package/monkey-coder-sdk
- PyPI Core: https://pypi.org/project/monkey-coder-core/
- PyPI SDK: https://pypi.org/project/monkey-coder-sdk/

## Troubleshooting

### Publishing Failures

**npm: 403 Forbidden**
- Check NPM_TOKEN is valid
- Ensure you have publish rights to the package
- Token might be expired - generate a new one

**PyPI: Invalid or non-existent authentication**
- Check PYPI_TOKEN is valid
- Ensure token starts with `pypi-`
- Token scope must include the packages

**Version Already Exists**
- This is normal if no changes were made
- The workflow will skip publishing
- Force a version bump if needed

### Checking Workflow Status

1. Go to your repository on GitHub
2. Click "Actions" tab
3. View "Auto-Publish Packages" workflow
4. Check the logs for any errors

## Benefits of Auto-Publishing

✅ **Instant Updates**: Users get fixes and features immediately
✅ **No Manual Steps**: Eliminates human error in publishing
✅ **Consistent Versions**: All packages stay in sync
✅ **Transparent Process**: All publishes are tracked in git history
✅ **Rollback Capable**: Can revert commits if issues arise

## Security Considerations

- Tokens are stored securely in GitHub Secrets
- Workflow only runs on main branch
- Version commits are tagged with `[skip ci]` to prevent loops
- All publishes are logged and auditable

## Local Development

During development, you can test publishing locally:

```bash
# Check current versions
./scripts/publish-all.sh

# Test build without publishing
cd packages/cli && npm run build
cd packages/sdk && npm run build:ts
cd packages/core && python -m build
```

## Monitoring Publications

After each commit to main, check:
1. GitHub Actions tab for workflow status
2. npm/PyPI to verify new versions are live
3. Installation test: `npm install monkey-coder-sdk@latest`

## Contact

For publishing issues or access:
- GitHub Issues: https://github.com/GaryOcean428/monkey-coder/issues
- Email: support@monkeycoder.dev