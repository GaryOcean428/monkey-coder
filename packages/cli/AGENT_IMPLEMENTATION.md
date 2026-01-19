# Local Agent Mode Implementation

This document describes the implementation of the `monkey agent` command for autonomous coding tasks.

## Overview

The local agent mode enables autonomous file editing, shell execution, and multi-step task completion. Tools execute locally while the backend is only used for AI inference.

## Command Usage

### Basic Usage
```bash
# Run a single task
monkey agent --task "Create a hello world TypeScript file"

# Run in local-only mode (no backend)
monkey agent --local --task "Fix lint errors in src/"

# Continue previous session
monkey agent --continue

# Skip approval prompts (dangerous!)
monkey agent --task "Update dependencies" --no-approval
```

### Command Options

- `-t, --task <description>`: Task description to complete
- `-l, --local`: Local-only mode (no backend API)
- `--no-approval`: Skip approval prompts for dangerous operations
- `-c, --continue`: Continue previous session
- `-m, --model <model>`: AI model to use (default: claude-sonnet-4)
- `--base-url <url>`: Backend API base URL
- `--api-key <key>`: API key for authentication
- `--max-iterations <n>`: Maximum agent iterations (default: 20)

## Architecture

### Components

1. **AgentRunner** (`agent-runner.ts`)
   - Main agent execution loop
   - Tool execution coordinator
   - Session management integration
   - Checkpoint creation and management

2. **Agent Command** (`commands/agent.ts`)
   - CLI command registration
   - Option parsing and validation
   - AgentRunner instantiation

3. **Local Tools** (`tools/index.ts`)
   - File operations (read, write, edit, delete)
   - Shell command execution
   - Glob search and directory listing

4. **Session Manager** (`session-manager.ts`)
   - Conversation history persistence
   - Token counting and context window management
   - SQLite-backed storage

5. **Checkpoint Manager** (`checkpoint-manager.ts`)
   - Git-based checkpointing
   - Operation journaling
   - Undo/restore functionality

### Agent Loop

1. Initialize session and create initial checkpoint
2. Add user task to session
3. Loop (max 20 iterations):
   - Call AI API with tool schemas and conversation context
   - If no tool calls, task is complete
   - For each tool call:
     - Request user approval if dangerous
     - Create checkpoint before execution
     - Execute tool locally
     - Add result to session context
4. Save session for future continuation

### Tool Approval Workflow

Dangerous tools require user approval by default:
- `shell_execute`: Execute shell commands
- `file_write`: Write files
- `file_edit`: Edit existing files
- `file_delete`: Delete files

Safe tools execute without approval:
- `file_read`: Read file contents
- `list_directory`: List directory contents
- `glob_search`: Search for files by pattern

## Implementation Status

### ✅ Completed

- [x] AgentRunner class with agent loop
- [x] Tool execution with local tools
- [x] User approval workflow
- [x] Session persistence integration
- [x] Checkpoint creation before operations
- [x] CLI command with all options
- [x] TypeScript type definitions
- [x] Basic unit tests
- [x] Build verification

### ⚠️ Known Limitations

1. **AI Response Parsing**: Current implementation has simplified tool call parsing. The backend API needs to return tool calls in a structured format for the agent to parse and execute them.

2. **Interactive Mode**: `startInteractive()` method is not yet implemented. Only task-based mode (`--task`) is functional.

3. **Local-Only Mode**: The `--local` flag is defined but full local inference (without backend) requires integration with a local LLM provider.

4. **Tool Call Format**: The agent expects tool calls in the format:
   ```typescript
   {
     id: string;
     name: string;
     arguments: Record<string, unknown>;
   }
   ```

5. **Error Recovery**: Limited error handling for tool execution failures. Needs more robust retry logic.

## Future Enhancements

### Priority 1
- [ ] Implement proper AI response parsing for tool calls
- [ ] Add streaming support for real-time progress
- [ ] Implement interactive REPL mode
- [ ] Add better error recovery

### Priority 2
- [ ] Support for MCP server tools
- [ ] Multi-agent coordination
- [ ] Parallel tool execution
- [ ] Web UI for agent monitoring

### Priority 3
- [ ] Local LLM integration (Ollama, LM Studio)
- [ ] Agent memory across sessions
- [ ] Custom tool plugins
- [ ] Agent performance metrics

## Testing

### Manual Testing

1. **Test tool schema generation:**
   ```typescript
   const runner = new AgentRunner();
   const schemas = runner['buildToolSchemas']();
   console.log(schemas);
   ```

2. **Test dangerous tool detection:**
   ```typescript
   const runner = new AgentRunner();
   console.log(runner['isDangerous']('shell_execute')); // true
   console.log(runner['isDangerous']('file_read')); // false
   ```

3. **Test command help:**
   ```bash
   monkey agent --help
   ```

### Automated Testing

Run unit tests:
```bash
cd packages/cli
yarn test agent-runner.test.ts
```

Note: Full integration tests are pending due to ESM module configuration issues.

## API Integration

The agent integrates with the backend `/api/v1/execute` endpoint:

```typescript
{
  task_type: 'custom',
  prompt: '<user task>',
  context: {
    session_id: '<session-id>',
    max_tokens: 8000,
    temperature: 0.7
  },
  persona_config: {
    persona: 'developer',
    custom_instructions: '...'
  },
  model_preferences: {
    anthropic: 'claude-sonnet-4'
  }
}
```

The response should include tool calls in the result when the AI wants to execute tools.

## Security Considerations

1. **Path Traversal Prevention**: All file operations validate paths to prevent directory traversal attacks.

2. **Shell Injection Prevention**: Shell commands use `spawn` with explicit args array instead of shell execution.

3. **User Approval**: Dangerous operations require explicit user confirmation by default.

4. **Checkpointing**: Git checkpoints allow reverting dangerous operations.

5. **Operation Journaling**: All file changes are logged for audit and undo.

## Contributing

When contributing to the agent implementation:

1. Follow existing patterns in `session-manager.ts` and `checkpoint-manager.ts`
2. Add appropriate type definitions
3. Include unit tests for new functionality
4. Update this documentation
5. Test manually with sample tasks

## References

- Issue: [#XXX feat(cli): Implement Local Agent Mode with `monkey agent` command]
- Session Manager: `packages/cli/src/session-manager.ts`
- Checkpoint Manager: `packages/cli/src/checkpoint-manager.ts`
- Local Tools: `packages/cli/src/tools/index.ts`
- MCP Client: `packages/cli/src/mcp-client.ts`
