# AI-Powered Automated Workflows Documentation

This document describes the comprehensive AI-powered automation system for PR reviews, issue
creation, and Railway compliance checks.

## Overview

The automation system consists of several key components:

1. **AI-Powered PR Review** - Automated code review using GitHub Models
2. **Railway Compliance Checking** - Ensures deployments follow Railway best practices
3. **Automatic Issue Creation** - Creates and assigns issues for various failure scenarios
4. **Auto-fixing Capabilities** - Automatically fixes simple compliance issues

## Components

### 1. AI-Powered PR Review Workflow

**File:** `.GitHub/workflows/ai-pr-review.yml`

This workflow runs on every pull request and provides:

- **Railway Compliance Checks**: Validates port configuration, service URLs, CORS setup, WebSocket
  protocols, and Dockerfile compliance
- **AI Code Review**: Uses GitHub Models (GPT-4.1) to review code for:
  - Security vulnerabilities
  - Performance issues
  - Best practices
  - Railway-specific deployment concerns
- **Auto-fix Capability**: Automatically fixes linting, formatting, and simple Railway compliance
  issues
- **Issue Creation**: Creates GitHub issues for critical problems that can't be auto-fixed
- **Auto-approval**: Can automatically approve PRs that pass all checks with high scores

#### Triggering a Re-review

Add a comment with `/ai-review` to trigger a new AI review after making changes.

### 2. Railway Compliance Checker

**File:** `.GitHub/scripts/railway-compliance-checker.js`

Checks for common Railway deployment issues:

- **Port Configuration**
  - Ensures use of `process.env.PORT`
  - Verifies binding to `0.0.0.0`
  - No hard-coded ports

- **Service URLs**
  - No localhost or 127.0.0.1 URLs
  - Uses Railway reference variables
  - Proper internal/external URL handling

- **CORS Configuration**
  - No wildcard origins in production
  - Proper credentials handling
  - Environment-based configuration

- **WebSocket Protocol**
  - WSS for HTTPS frontends
  - WS for HTTP development
  - No protocol mismatches

- **Dockerfile Compliance**
  - Uses ARG PORT
  - No hard-coded EXPOSE values
  - Proper CMD configuration

### 3. Automated Issue Creation

**File:** `.GitHub/workflows/auto-issue-creation.yml`

Automatically creates issues for:

- **CI Failures**: Creates issues when tests, builds, or linting fails
- **Security Vulnerabilities**: Weekly scans create issues for critical vulnerabilities
- **Performance Regressions**: Detects and reports performance degradations
- **Deployment Failures**: Creates issues with Railway-specific debugging steps
- **Weekly Summaries**: Generates reports of all automated activity

#### Auto-assignment Rules

Issues are automatically assigned based on labels:

- `security` → security-team
- `performance` → performance-team
- `railway-compliance` → DevOps-team
- `core` → backend-team
- `cli` → cli-team
- `sdk` → sdk-team

### 4. Railway Auto-Fixer

**File:** `.GitHub/scripts/railway-auto-fixer.js`

Automatically fixes common Railway issues:

- Replaces hard-coded ports with `process.env.PORT`
- Adds host binding (`0.0.0.0`) where missing
- Replaces localhost URLs with environment variables
- Updates package.JSON start scripts
- Fixes Dockerfile port configurations
- Creates/updates `.env.example` with Railway variables

## Setup Instructions

### 1. Enable GitHub Models

The AI review features require access to GitHub Models. Ensure your repository has access to:

- GitHub Copilot
- GitHub Models API

### 2. Configure Team Assignments

Update the team assignments in `.GitHub/workflows/auto-issue-creation.yml`:

```javascript
const teamMembers = {
  'security-team': ['your-security-lead'],
  'performance-team': ['your-perf-engineer'],
  'DevOps-team': ['your-DevOps-lead'],
  // ... add your team members
};
```

### 3. Set Up Secrets

No additional secrets are required! The workflows use the built-in `GITHUB_TOKEN`.

### 4. Create Required Labels

Ensure your repository has these labels:

- `bug`
- `security`
- `performance`
- `railway-compliance`
- `auto-generated`
- `critical`
- `warning`
- `ci`
- `deployment`

### 5. Configure Branch Protection

For auto-approval to work, configure branch protection rules to:

- Require PR reviews
- Allow GitHub Actions to approve PRs
- Require status checks to pass

## Usage Examples

### Example 1: PR with Railway Compliance Issues

```yaml
# Bad: Hard-coded port
app.listen(3000)

# Good: Auto-fixed to
app.listen(process.env.PORT || 3000, '0.0.0.0')
```

### Example 2: Security Vulnerability Detection

The AI will comment on PRs with security issues:

```markdown
**Security Issue** (critical)

Potential SQL injection vulnerability detected at line 42. Use parameterized queries instead of
string concatenation.
```

### Example 3: Automatic Issue Creation

When a deployment fails, an issue is created:

````markdown
🚨 Deployment Failed: production

**Environment:** production **Service:** API **Error:** Container failed to start

### Railway Logs:

```text
Error: Cannot find module 'express'
```
````

### Common Railway Issues to Check:

- [ ] PORT environment variable is set correctly
- [ ] Service is binding to 0.0.0.0:$PORT
- [ ] All environment variables are configured

````

## Customization

### Adding New Compliance Checks

Edit `.GitHub/scripts/railway-compliance-checker.js`:

```javascript
checkCustomCompliance() {
  // Add your custom checks here
  const files = this.getRelevantFiles(['.js', '.ts']);
  // ... implement checks
  this.checks['Custom Compliance'] = allPassed;
}
````

### Modifying AI Review Prompts

Edit the prompts in `.GitHub/workflows/ai-pr-review.yml`:

```yaml
- name: Run AI Custom Review
  run: |
    gh models run gpt-4.1 "
    Your custom review prompt here...
    "
```

### Adding New Auto-fix Rules

Edit `.GitHub/scripts/railway-auto-fixer.js`:

```javascript
fixCustomIssue() {
  const fixes = [
    {
      pattern: /your-pattern/g,
      replacement: 'your-replacement',
      description: 'Fix description'
    }
  ];
  // Apply fixes...
}
```

## Best Practices

1. **Review AI Suggestions**: While AI reviews are helpful, always have humans review critical code
2. **Test Auto-fixes**: Ensure auto-fixes don't break functionality
3. **Monitor Issue Creation**: Avoid alert fatigue by tuning sensitivity
4. **Keep Rules Updated**: Regularly update compliance rules as your infrastructure evolves
5. **Use Staging First**: Test workflows on staging branches before main

## Troubleshooting

### AI Reviews Not Working

1. Check GitHub Models access
2. Verify workflow permissions
3. Check GitHub API rate limits

### Auto-fixes Breaking Code

1. Review the fix patterns in `railway-auto-fixer.js`
2. Add exclusions for specific files
3. Test fixes locally first

### Too Many Issues Created

1. Adjust severity thresholds
2. Increase time between scans
3. Filter out known false positives

## Integration with Other Tools

### Slack Notifications

Add Slack notifications for critical issues:

```yaml
- name: Notify Slack
  if: steps.analyze.outputs.severity == 'critical'
  uses: slackapi/slack-GitHub-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "Critical issue detected in PR #${{ GitHub.event.number }}"
      }
```

### Custom MCP Servers

Integrate with your MCP servers for additional capabilities:

```yaml
- name: Use Custom MCP Tool
  run: |
    npx your-mcp-server tool-name --args
```

## Metrics and Monitoring

Track automation effectiveness:

1. **PR Approval Time**: Measure time saved by auto-approval
2. **Issue Resolution Time**: Track how quickly auto-created issues are resolved
3. **Fix Success Rate**: Monitor percentage of successful auto-fixes
4. **False Positive Rate**: Track incorrect issue creation

## Future Enhancements

Planned improvements:

1. **Machine Learning**: Train custom models on your codebase
2. **Multi-language Support**: Extend beyond JS/TS/Python
3. **Advanced Security Scanning**: Integration with more security tools
4. **Predictive Issue Creation**: Create issues before problems occur
5. **Auto-PR Creation**: Automatically create PRs for dependency updates

## Support

For issues or questions:

1. Check the workflow logs in GitHub Actions
2. Review the generated reports in artifacts
3. Create an issue with the `automation` label
4. Contact the DevOps team

---

_This automation system is designed to enhance, not replace, human review and decision-making._
