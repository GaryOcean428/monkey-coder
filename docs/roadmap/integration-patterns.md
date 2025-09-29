[← Back to Roadmap Index](./index.md)

## Integration Patterns

### IDE Integrations

```json
// VS Code extension manifest
{
  "name": "monkey-coder-vscode",
  "version": "1.0.0",
  "engines": { "vscode": "^1.80.0" },
  "contributes": {
    "commands": [
      {
        "command": "monkey-coder.generateCode",
        "title": "Generate Code with Monkey Coder"
      },
      {
        "command": "monkey-coder.analyzeCode",
        "title": "Analyze Code with Monkey Coder"
      }
    ],
    "keybindings": [
      {
        "command": "monkey-coder.generateCode",
        "key": "ctrl+shift+g",
        "when": "editorTextFocus"
      }
    ]
  }
}
```

### Git Hooks Integration

```bash
#!/bin/sh
# .git/hooks/pre-commit
# Monkey Coder pre-commit hook

# Run code analysis on staged files
staged_files=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|ts|tsx|js|jsx)$')

if [ -n "$staged_files" ]; then
    echo "Running Monkey Coder analysis on staged files..."
    monkey analyze --files "$staged_files" --format JSON > /tmp/monkey-analysis.JSON

    # Check for critical issues
    critical_issues=$(jq '.issues[] | select(.severity == "critical")' /tmp/monkey-analysis.JSON)

    if [ -n "$critical_issues" ]; then
        echo "Critical issues found. Commit aborted."
        echo "$critical_issues"
        exit 1
    fi
fi
```

### CI/CD Pipeline Integration

```yaml
# GitHub Actions integration
- name: Monkey Coder Analysis
  uses: monkey-coder/GitHub-action@v1
  with:
    API-key: ${{ secrets.MONKEY_CODER_API_KEY }}
    command: 'analyze'
    files: ${{ GitHub.event.pull_request.changed_files }}
    fail-on-issues: 'critical,high'
```

### API Integration Examples

**Node.js SDK Usage:**

```javascript
import { MonkeyCoderClient } from 'monkey-coder-sdk';

const client = new MonkeyCoderClient({
  apiKey: process.env.MONKEY_CODER_API_KEY,
  baseUrl: 'https://api.monkey-coder.com/v1'
});

// Generate code
const result = await client.execute({
  prompt: 'Create a user authentication system',
  persona: 'developer',
  taskType: 'code_generation',
  context: {
    language: 'TypeScript',
    framework: 'express'
  }
});

console.log(result.generatedCode);
```

**Python SDK Usage:**

```python
from monkey_coder_sdk import MonkeyCoderClient

client = MonkeyCoderClient(
    api_key=os.getenv('MONKEY_CODER_API_KEY'),
    base_url='HTTPS://API.monkey-coder.com/v1'
)

# Analyze existing code
result = client.execute(
    prompt='Analyze this code for security vulnerabilities',
    persona='security_expert',
    task_type='code_analysis',
    context={'language': 'Python', 'code': existing_code}
)

print(result.analysis_report)
```

### Webhook Integration

**Webhook Event Types:**
- `task.completed` - Task execution completed
- `task.failed` - Task execution failed
- `user.authenticated` - User logged in
- `quota.exceeded` - Usage quota exceeded
- `model.updated` - AI model configuration updated

**Webhook Payload Example:**

```json
{
  "event": "task.completed",
  "timestamp": "2025-01-31T21:00:00Z",
  "data": {
    "task_id": "task_123456",
    "user_id": "user_789",
    "prompt": "Create a REST API",
    "result": {
      "success": true,
      "generated_code": "...",
      "model_used": "gpt-4.1",
      "tokens_consumed": 245,
      "processing_time_ms": 1500
    }
  },
  "signature": "sha256=..."
}
