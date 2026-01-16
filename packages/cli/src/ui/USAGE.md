# Ink UI Usage Examples

This document provides practical examples of using the Ink-based terminal UI components in the Monkey Coder CLI.

## Quick Start

### Interactive Chat Mode

The simplest way to start using Ink UI:

```bash
# Using the new Ink-based chat command
monkey chat-ink

# With custom options
monkey chat-ink --persona developer --provider openai --model gpt-4
```

### Agent Mode with Tool Execution

For agentic workflows with MCP tool support:

```bash
# Start agent mode
monkey agent-ink

# With custom MCP server configuration
monkey agent-ink --mcp-config ~/.monkey-coder/mcp-servers.json
```

## Command Options

### chat-ink Command

```bash
monkey chat-ink [options]

Options:
  -p, --persona <persona>     AI persona (default: "developer")
  --model <model>             AI model to use
  --provider <provider>       AI provider (openai, anthropic, etc.)
  -t, --temperature <temp>    Temperature 0.0-2.0 (default: 0.7)
  --stream                    Enable streaming (default: true)
  --api-key <key>            Override API key
  --base-url <url>           Override API base URL
```

### agent-ink Command

```bash
monkey agent-ink [options]

Options:
  -p, --persona <persona>     AI persona (default: "agent")
  --model <model>             AI model to use
  --provider <provider>       AI provider
  -t, --temperature <temp>    Temperature 0.0-2.0
  --stream                    Enable streaming (default: true)
  --mcp-config <path>        Path to MCP servers config
```

## Configuration

### MCP Server Configuration

Create `~/.monkey-coder/mcp-servers.json`:

```json
{
  "servers": [
    {
      "name": "filesystem",
      "type": "stdio",
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-filesystem",
        "/path/to/your/project"
      ]
    },
    {
      "name": "github",
      "type": "stdio",
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your-github-token"
      }
    },
    {
      "name": "web-search",
      "type": "sse",
      "url": "http://localhost:3000/mcp"
    }
  ]
}
```

### Session Configuration

Sessions are automatically persisted to `~/.monkey-coder/sessions.db`.

To configure session behavior, use environment variables:

```bash
# Set max context tokens
export MONKEY_CODER_MAX_TOKENS=8000

# Set model for token counting
export MONKEY_CODER_TOKEN_MODEL=gpt-4
```

## Usage Scenarios

### 1. Code Review with Syntax Highlighting

```bash
# Start chat mode
monkey chat-ink --persona reviewer

# In the chat:
> Review the following TypeScript code:
> 
> ```typescript
> function processData(data: unknown) {
>   return data.map(x => x * 2);
> }
> ```
```

The code will be displayed with syntax highlighting, and the AI will provide feedback.

### 2. File Operations with Approval

```bash
# Start agent mode
monkey agent-ink --mcp-config ~/.monkey-coder/mcp-servers.json

# In the agent mode:
> Create a new file called config.ts with default configuration
```

The agent will:
1. Show a tool approval dialog with the file path and content
2. Wait for your approval (Y/N)
3. Execute the tool if approved
4. Show the result

### 3. Multi-Step Tasks

```bash
monkey agent-ink

# Request a complex task:
> Set up a new React component with tests
>   1. Create component file
>   2. Create test file
>   3. Update index to export component
```

The agent will:
- Show hierarchical task progress
- Request approval for each file operation
- Update status in real-time
- Show completion status for each subtask

### 4. Diff Review Before Writing

```bash
monkey agent-ink

# Request file modification:
> Update the API endpoint URL from localhost to production
```

The agent will:
- Show a diff viewer with before/after
- Highlight additions in green, deletions in red
- Request approval before writing
- Apply changes only if approved

## Interactive Features

### Keyboard Navigation

While in Ink UI mode:

- **Enter** - Submit input or confirm action
- **Esc** - Exit or cancel current operation  
- **Ctrl+C** - Force exit
- **Y** - Approve tool execution
- **N** - Reject tool execution
- **Backspace** - Delete last character

### Visual Indicators

- **🐵** - Monkey Coder branding
- **⏳** - AI thinking or processing
- **⚡** - Tool execution in progress
- **✓** - Task completed successfully
- **✗** - Task failed
- **○** - Task pending
- **⚠️** - Warning or approval needed

## Advanced Usage

### Programmatic API

You can also use the Ink UI programmatically:

```typescript
import { renderApp } from './ui';
import { MonkeyCoderAPIClient } from './api-client';

const client = new MonkeyCoderAPIClient('http://localhost:8000', 'your-api-key');

const { waitUntilExit } = renderApp({
  mode: 'chat',
  workingDirectory: process.cwd(),
  onMessage: async (content) => {
    const response = await client.execute({
      task_type: 'custom',
      prompt: content,
      // ... other options
    });
    
    return response.result?.result || 'No response';
  },
});

await waitUntilExit();
```

### Custom Session Management

```typescript
import { useSession } from './ui/hooks/useSession';

// In your React component:
const {
  sessionId,
  messages,
  addMessage,
  getTokenCount,
} = useSession({
  workingDirectory: '/path/to/project',
  gitBranch: 'feature/new-ui',
  maxTokens: 16000,
});

// Add messages
addMessage('user', 'Hello!');
addMessage('assistant', 'Hi there!');

// Check token usage
console.log(`Tokens used: ${getTokenCount()}`);
```

### Custom Tool Execution

```typescript
import { useAgent } from './ui/hooks/useAgent';

const {
  tasks,
  executeTool,
  pendingToolCall,
  approveTool,
  rejectTool,
} = useAgent({
  mcpServers: [/* your MCP servers */],
  autoApprove: false, // Require manual approval
});

// Execute a tool
await executeTool({
  name: 'file_write',
  args: {
    path: 'src/config.ts',
    content: 'export const CONFIG = {};',
  },
});

// Check for pending approval
if (pendingToolCall) {
  // Show your custom approval UI
  const approved = await askUser();
  
  if (approved) {
    await approveTool();
  } else {
    rejectTool();
  }
}
```

## Troubleshooting

### Terminal Not Rendering Correctly

If the UI looks broken:

1. Ensure your terminal supports ANSI colors:
   ```bash
   echo -e "\033[31mRed\033[0m \033[32mGreen\033[0m \033[34mBlue\033[0m"
   ```

2. Check terminal size:
   ```bash
   tput cols  # Should be >= 80
   tput lines # Should be >= 24
   ```

3. Update your terminal emulator to a modern version

### Input Not Working

If keyboard input doesn't work:

1. Make sure stdin is a TTY:
   ```bash
   [ -t 0 ] && echo "TTY" || echo "Not a TTY"
   ```

2. Don't pipe input into the command
3. Run directly in terminal, not through tmux/screen (or configure properly)

### MCP Tools Not Found

If tools aren't available:

1. Verify MCP server configuration:
   ```bash
   cat ~/.monkey-coder/mcp-servers.json
   ```

2. Test MCP server manually:
   ```bash
   npx @modelcontextprotocol/server-filesystem /path/to/workspace
   ```

3. Check server connection logs in agent mode

### Session Not Persisting

If sessions aren't saved:

1. Check permissions on config directory:
   ```bash
   ls -la ~/.monkey-coder/
   ```

2. Ensure SQLite database is writable:
   ```bash
   sqlite3 ~/.monkey-coder/sessions.db ".databases"
   ```

3. Check for disk space issues

## Best Practices

### 1. Session Management

- Use descriptive session names for easy identification
- Regularly review and clean up old sessions
- Export important sessions before cleanup

### 2. Tool Approval

- Always review tool arguments before approval
- Use auto-approve only for trusted, non-destructive operations
- Keep an eye on file paths in tool calls

### 3. Performance

- Limit message history to recent context
- Use smaller context windows for simple tasks
- Clear sessions periodically to free up space

### 4. Security

- Never store API keys in MCP server configs
- Use environment variables for sensitive data
- Review all file write operations before approval
- Be cautious with shell execution tools

## Examples Repository

For more examples, see:
- [Basic Chat Examples](../../examples/chat/)
- [Agent Workflows](../../examples/agent/)
- [Custom Components](../../examples/components/)

## Getting Help

- GitHub Issues: https://github.com/GaryOcean428/monkey-coder/issues
- Documentation: https://docs.monkey-coder.dev
- Discord: https://discord.gg/monkey-coder
