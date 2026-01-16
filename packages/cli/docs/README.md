# Monkey Coder CLI Documentation

## Core Features

### 🤖 [Agent Mode](./agent-mode.md)
Local autonomous coding with AI-powered tool execution. Operates like Claude Code CLI with direct file system access and shell command execution.

```bash
monkey agent "your task description"
```

### 📦 MCP Integration
Connect to Model Context Protocol servers for extended functionality.

```bash
monkey mcp list
monkey mcp connect <server-name>
```

### 💾 Session Management
Persistent conversation and context management across invocations.

```bash
monkey session list
monkey session show <session-id>
```

### ⏮️ Checkpoint System
Git-based undo/redo with operation journaling.

```bash
monkey checkpoint create "description"
monkey checkpoint list
monkey checkpoint restore <id>
```

## Quick Links

- [Agent Mode Guide](./agent-mode.md) - Comprehensive agent mode documentation
- [MCP Servers](./mcp-servers.md) - Available MCP server integrations
- [Configuration](./configuration.md) - CLI configuration options
- [Examples](./examples.md) - Usage examples and recipes

## Getting Started

1. Install the CLI:
```bash
yarn global add monkey-coder-cli
```

2. Authenticate:
```bash
monkey auth login
```

3. Start using agent mode:
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key
monkey agent "Create a hello world TypeScript app"
```

## Command Reference

| Command | Description |
|---------|-------------|
| `agent` | Start local agent mode |
| `auth` | Authentication management |
| `session` | Session management |
| `checkpoint` | Checkpoint management |
| `mcp` | MCP server management |
| `config` | Configuration management |

For detailed help on any command:
```bash
monkey <command> --help
```
