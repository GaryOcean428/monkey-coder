# 🚀 Continuous Publishing Setup Complete!

I've set up an automated workflow that publishes your packages to PyPI and npm on every commit to the main branch.

## ✅ What Was Created

1. **GitHub Actions Workflow** (`.github/workflows/continuous-publish.yml`)
   - Automatically detects changes in package directories
   - Bumps versions based on commit messages
   - Publishes to PyPI and npm
   - Creates GitHub releases

2. **Version Bumping Configs**
   - `packages/core/.bumpversion.cfg` - For Python core package
   - `packages/sdk/src/python/.bumpversion.cfg` - For Python SDK

3. **Documentation** (`docs/CONTINUOUS_PUBLISHING.md`)
   - Complete guide on how the workflow operates
   - Troubleshooting tips
   - Best practices

## 🔧 Required Setup Steps

### 1. Add GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions, then add:

- **PYPI_TOKEN**: Your PyPI API token
  - Get it from: https://pypi.org/manage/account/token/
  - Create a token with upload permissions for your packages

- **NPM_ACCESS_TOKEN**: Your npm access token  
  - Get it from: https://www.npmjs.com/settings/{your-username}/tokens
  - Create an "Automation" type token

### 2. (Optional) Slack Notifications

If you want Slack notifications, add:
- **SLACK_WEBHOOK_URL**: Your Slack webhook URL

## 📝 How to Use

### Commit Message Format

The workflow automatically bumps versions based on your commit messages:

```bash
# Major version bump (1.0.0 → 2.0.0)
git commit -m "feat!: redesigned API"
git commit -m "fix: bug fix

BREAKING CHANGE: removed old methods"

# Minor version bump (1.0.0 → 1.1.0)
git commit -m "feat: added new feature"

# Patch version bump (1.0.0 → 1.0.1)
git commit -m "fix: fixed bug"
git commit -m "docs: updated docs"
git commit -m "chore: cleaned up code"
```

### What Happens on Push

When you push to main:
1. Workflow checks which packages changed
2. Bumps version based on commit message
3. Commits the version change (with `[skip ci]`)
4. Builds and publishes packages
5. Creates a GitHub release

## 🎯 Quick Test

To test the workflow:

```bash
# Make a small change in a package
echo "# Test" >> packages/core/README.md

# Commit with a conventional message
git add .
git commit -m "docs: test continuous publishing"

# Push to main
git push origin main
```

Then check:
- GitHub Actions tab for workflow progress
- PyPI/npm for published packages
- Releases tab for new releases

## 📋 Package Names

Your packages will be published as:
- **PyPI**: `monkey-coder-core`, `monkey-coder-sdk`
- **npm**: `monkey-coder-cli`, `monkey-coder-sdk`

## 🛡️ Safety Features

- Checks if version already exists before publishing
- Uses `[skip ci]` to prevent infinite loops
- Only publishes changed packages
- Secure secret handling

## 🚨 Important Notes

1. **First Time**: Initial publish might fail if packages don't exist on registries yet
2. **Secrets**: Must be added before workflow can succeed
3. **Main Branch**: Only works on pushes to main branch
4. **File Changes**: Only triggers for non-test, non-markdown files in packages/

Happy continuous publishing! 🎉
