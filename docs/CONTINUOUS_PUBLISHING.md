# Continuous Publishing Workflow

This project includes an automated continuous publishing workflow that publishes packages to PyPI and npm registries on every commit to the main branch.

## Overview

The workflow automatically:
1. Detects changes in package directories
2. Bumps version numbers based on commit messages
3. Publishes updated packages to registries
4. Creates GitHub releases with changelogs

## How It Works

### Trigger Conditions

The workflow runs when:
- Code is pushed to the `main` branch
- Changes are made to files in `packages/` directories
- Changes are NOT in test files, spec files, or markdown files

### Version Bumping

Version numbers are automatically bumped based on commit message patterns:
- **Major version** (1.0.0 → 2.0.0): Commit contains `BREAKING CHANGE` or ends with `!`
- **Minor version** (1.0.0 → 1.1.0): Commit starts with `feat`
- **Patch version** (1.0.0 → 1.0.1): All other commits

### Package Detection

The workflow detects changes in:
- **NPM packages**: `packages/cli/`, `packages/sdk/src/typescript/`, `packages/web/`
- **PyPI packages**: `packages/core/`, `packages/sdk/src/python/`

### Publishing Process

1. **Check for changes** in package directories
2. **Bump versions** automatically based on commit type
3. **Commit version changes** with `[skip ci]` to avoid loops
4. **Build packages** with appropriate tools
5. **Check if version exists** to avoid duplicate publishes
6. **Publish to registries** if version is new
7. **Create GitHub release** with changelog

## Required Secrets

Add these secrets to your GitHub repository:

### PyPI Publishing
- `PYPI_TOKEN`: PyPI API token for publishing Python packages
  - Get from: https://pypi.org/manage/account/token/
  - Scope: Can upload to specific projects or entire account

### NPM Publishing
- `NPM_ACCESS_TOKEN`: NPM access token for publishing JavaScript packages
  - Get from: https://www.npmjs.com/settings/{username}/tokens
  - Type: Automation token recommended

### Optional
- `SLACK_WEBHOOK_URL`: For Slack notifications (optional)

## Setting Up Secrets

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each required secret

## Commit Message Guidelines

To control version bumping, use these commit message patterns:

```bash
# Major version bump (breaking changes)
git commit -m "feat!: completely redesigned API"
git commit -m "fix: corrected issue

BREAKING CHANGE: removed deprecated methods"

# Minor version bump (new features)
git commit -m "feat: added new quantum routing capability"

# Patch version bump (bug fixes, docs, etc.)
git commit -m "fix: corrected memory leak in agent system"
git commit -m "docs: updated installation instructions"
git commit -m "chore: cleaned up dependencies"
```

## Published Packages

### NPM Packages
- `@monkey-coder/cli` - Command-line interface
- `@monkey-coder/sdk` - JavaScript/TypeScript SDK

### PyPI Packages
- `monkey-coder-core` - Core Python library
- `monkey-coder-sdk` - Python SDK

## Manual Publishing

If you need to publish manually, use the existing scripts:

```bash
# Publish all packages
./scripts/publish-all.sh

# Publish only npm packages
./scripts/publish-npm.sh

# Publish only PyPI packages
./scripts/publish-pypi.sh
```

## Troubleshooting

### Workflow Not Running
- Ensure changes are in `packages/` directories
- Check that you're pushing to `main` branch
- Verify file changes aren't excluded (tests, specs, markdown)

### Publishing Failures
- Check GitHub Actions logs for detailed errors
- Verify secrets are correctly set
- Ensure package versions don't already exist on registries

### Version Conflicts
- The workflow checks if versions exist before publishing
- If a version exists, publishing is skipped
- Manual version bumps may be needed to resolve conflicts

## Best Practices

1. **Use conventional commits** for predictable version bumping
2. **Test locally** before pushing to main
3. **Monitor GitHub Actions** for any failures
4. **Keep secrets secure** and rotate periodically
5. **Review releases** created by the workflow

## Workflow File

The workflow is defined in: `.github/workflows/continuous-publish.yml`

## Disabling Continuous Publishing

To temporarily disable:
1. Comment out the workflow file
2. Or add `[skip ci]` to commit messages
3. Or work in a feature branch until ready

## Security Considerations

- Secrets are never logged or exposed
- Workflow has minimal permissions
- Version checks prevent accidental overwrites
- Git commits use a bot identity
