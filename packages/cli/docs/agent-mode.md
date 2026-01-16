# Agent Mode - Local Autonomous Coding

The `monkey agent` command enables local-first autonomous coding with AI-powered tool execution.

## Quick Start

```bash
# Set your API key
export ANTHROPIC_API_KEY=sk-ant-your-key

# Run a task
monkey agent "Create a TypeScript utility function to format dates"
```

## Overview

Agent mode operates like Claude Code CLI or Gemini CLI - with direct file system access, shell command execution, and MCP tool orchestration.

## Modes

- **hybrid** (default): Local tools + Cloud AI
- **local**: Fully offline (requires local AI)
- **cloud**: Uses remote backend

## AI Providers

### Anthropic (Default)
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key
monkey agent "task" --provider anthropic
```

### OpenAI
```bash
export OPENAI_API_KEY=sk-your-key
monkey agent "task" --provider openai
```

### Google Gemini
```bash
export GOOGLE_API_KEY=your-key
monkey agent "task" --provider google
```

## Available Tools

1. **file_read** - Read file contents
2. **file_write** - Write content to files
3. **file_edit** - Edit files by replacing text
4. **file_delete** - Delete files
5. **shell_execute** - Execute shell commands
6. **glob_search** - Search files with patterns
7. **list_directory** - List directory contents

Plus any MCP tools from connected servers.

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--mode` | `hybrid` | Agent mode |
| `--provider` | `anthropic` | AI provider |
| `--model` | `claude-sonnet-4-20250514` | AI model |
| `--auto-approve` | `false` | Skip approval prompts |
| `--max-iterations` | `10` | Max tool iterations |

## Examples

### Create a Feature
```bash
monkey agent "Create a user profile component with TypeScript and React"
```

### Refactor Code
```bash
monkey agent "Refactor auth logic to use async/await"
```

### Debug
```bash
monkey agent "Find and fix the memory leak in server.ts"
```

## Security

By default, destructive operations require approval:
- File writes/edits/deletes
- Shell commands

Use `--auto-approve` to skip (with caution).

## Related Commands

- `monkey session` - Manage sessions
- `monkey checkpoint` - Manage checkpoints
- `monkey mcp` - Manage MCP servers
