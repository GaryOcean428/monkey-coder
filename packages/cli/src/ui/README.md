# Ink Terminal UI Components

This directory contains React-based terminal UI components built with [Ink v5](https://github.com/vadimdemedes/ink) for rich, interactive CLI experiences.

## Overview

The Ink UI system provides:
- **Rich terminal interfaces** with React components
- **Session management** with persistent conversation history
- **Agent mode** with MCP tool execution and approval dialogs
- **Syntax-highlighted code blocks** for better readability
- **File diff visualization** for reviewing changes
- **Hierarchical task progress** with real-time status updates

## Architecture

```
ui/
├── App.tsx                 # Main application component
├── types.ts               # Shared TypeScript types
├── index.ts               # Public exports
├── components/            # Reusable UI components
│   ├── CodeBlock.tsx     # Syntax-highlighted code display
│   ├── DiffViewer.tsx    # File diff visualization
│   ├── MessageComponent.tsx  # Chat message display
│   ├── TaskList.tsx      # Hierarchical task progress
│   └── ToolApproval.tsx  # Tool execution approval dialog
└── hooks/                 # React hooks for state management
    ├── useSession.ts     # Session persistence and context management
    └── useAgent.ts       # MCP agent and tool execution
```

## Components

### App Component

The main entry point that orchestrates all UI elements:

```tsx
import { renderApp } from './ui';

const { waitUntilExit } = renderApp({
  mode: 'chat',  // or 'agent'
  workingDirectory: process.cwd(),
  onMessage: async (content) => {
    // Handle user input
    return response;
  },
});

await waitUntilExit();
```

**Props:**
- `mode`: `'chat'` | `'agent'` - Operating mode
- `workingDirectory`: Optional working directory for session
- `mcpServers`: MCP server configurations (agent mode only)
- `onMessage`: Async callback for handling user messages
- `initialPrompt`: Optional initial message to send

### MessageComponent

Displays chat messages with role-based styling:

```tsx
<MessageComponent 
  message={{
    id: 'msg-1',
    role: 'user',  // 'user' | 'assistant' | 'tool' | 'system'
    content: 'Hello, world!',
    isCode: false,
    timestamp: Date.now()
  }}
/>
```

**Features:**
- Color-coded by role (green for user, cyan for assistant, yellow for tool, gray for system)
- Timestamps in human-readable format
- Automatic code block rendering for code messages

### CodeBlock

Syntax-highlighted code display using `cli-highlight`:

```tsx
<CodeBlock 
  code={sourceCode}
  language="typescript"
  showLineNumbers={true}
/>
```

**Supported Languages:**
- JavaScript, TypeScript, Python, Java, C++, Rust, Go
- HTML, CSS, JSON, YAML, Markdown
- And many more via cli-highlight

### DiffViewer

File diff visualization with approval workflow:

```tsx
<DiffViewer 
  filename="src/index.ts"
  diff={[
    { type: 'context', content: 'import { App } from "./app"', lineNumber: 1 },
    { type: 'remove', content: 'const port = 3000', lineNumber: 2 },
    { type: 'add', content: 'const port = process.env.PORT || 3000', lineNumber: 2 },
  ]}
  showApproval={true}
  onApprove={() => console.log('Approved')}
  onReject={() => console.log('Rejected')}
/>
```

**Diff Line Types:**
- `add`: Green (+) - Added lines
- `remove`: Red (-) - Removed lines
- `context`: Gray - Unchanged context lines

### TaskList

Hierarchical task progress indicator:

```tsx
<TaskList 
  tasks={[
    {
      id: '1',
      title: 'Install dependencies',
      status: 'completed',
      subtasks: [
        { id: '1-1', title: 'npm install', status: 'completed' }
      ]
    },
    {
      id: '2',
      title: 'Build project',
      status: 'running'
    }
  ]}
/>
```

**Status Icons:**
- `pending`: ○ (gray circle)
- `running`: ⏳ (hourglass emoji)
- `completed`: ✓ (green checkmark)
- `failed`: ✗ (red X)

### ToolApproval

Interactive dialog for approving tool execution:

```tsx
<ToolApproval 
  toolName="file_write"
  args={{
    path: "src/config.ts",
    content: "export const API_KEY = '...'"
  }}
  onApprove={() => executeTool()}
  onReject={() => cancelTool()}
/>
```

**Keyboard Shortcuts:**
- `Y` or `Enter` - Approve
- `N` or `Esc` - Reject

## Hooks

### useSession

Manages conversation sessions with SQLite persistence:

```tsx
const {
  sessionId,
  messages,
  addMessage,
  clearMessages,
  getTokenCount,
  loading,
  error,
} = useSession({
  workingDirectory: process.cwd(),
  gitBranch: 'main',
  maxTokens: 8000,
});

// Add a message
addMessage('user', 'How do I use React hooks?');
```

**Features:**
- Automatic session creation and persistence
- Token counting with tiktoken
- Message history retrieval
- Context window management

### useAgent

Manages MCP tool execution and agent workflows:

```tsx
const {
  tasks,
  currentTool,
  pendingToolCall,
  executeTool,
  approveTool,
  rejectTool,
  isExecuting,
  error,
} = useAgent({
  mcpServers: [
    {
      name: 'filesystem',
      type: 'stdio',
      command: 'npx',
      args: ['@modelcontextprotocol/server-filesystem', process.cwd()]
    }
  ],
  autoApprove: false,
});

// Execute a tool
await executeTool({
  name: 'file_read',
  args: { path: 'src/index.ts' }
});
```

**Features:**
- Multi-server MCP connection management
- Tool discovery and execution
- Approval workflow for destructive operations
- Hierarchical task tracking

## Usage Examples

### Basic Chat Mode

```typescript
import { createInkChatCommand } from './commands/chat-ink';
import { ConfigManager } from './config';

const config = new ConfigManager();
const chatCommand = createInkChatCommand(config);

// Register with Commander.js
program.addCommand(chatCommand);
```

Run: `monkey chat-ink --persona developer`

### Agent Mode with MCP

```typescript
import { createInkAgentCommand } from './commands/agent-ink';

const agentCommand = createInkAgentCommand(config);
program.addCommand(agentCommand);
```

Run: `monkey agent-ink --mcp-config ~/.monkey-coder/mcp-servers.json`

### MCP Server Configuration

Create `~/.monkey-coder/mcp-servers.json`:

```json
{
  "servers": [
    {
      "name": "filesystem",
      "type": "stdio",
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/path/to/workspace"]
    },
    {
      "name": "github",
      "type": "stdio",
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_..."
      }
    }
  ]
}
```

## Keyboard Shortcuts

Global shortcuts available in all Ink UI modes:

- **Ctrl+C** or **Esc** - Exit the application
- **Enter** - Submit current input / Confirm action
- **Y** - Approve (in approval dialogs)
- **N** - Reject (in approval dialogs)
- **Backspace** - Delete last character

## Terminal Requirements

### Minimum Requirements
- ANSI color support (most modern terminals)
- Unicode support for icons and emojis
- Minimum 80x24 terminal size

### Recommended
- 24-bit true color support
- iTerm2, Hyper, Windows Terminal, or similar modern terminal
- Monospace font with good Unicode coverage (Fira Code, JetBrains Mono, etc.)

### Graceful Degradation
The UI automatically degrades gracefully for terminals with limited capabilities:
- Falls back to simple ASCII characters if Unicode is not supported
- Uses 8-color palette if 24-bit color is unavailable
- Simplifies layout for small terminal sizes

## Development

### Building

```bash
cd packages/cli
yarn build
```

### Testing Components

```bash
# Test chat mode
yarn tsx src/commands/chat-ink.ts

# Test agent mode
yarn tsx src/commands/agent-ink.ts --mcp-config test-config.json
```

### Adding New Components

1. Create component in `src/ui/components/YourComponent.tsx`
2. Export from `src/ui/index.ts`
3. Import and use in `App.tsx` or other components

Example component structure:

```tsx
import React from 'react';
import { Box, Text } from 'ink';

interface YourComponentProps {
  title: string;
  onAction: () => void;
}

export const YourComponent: React.FC<YourComponentProps> = ({ title, onAction }) => {
  return (
    <Box borderStyle="round" padding={1}>
      <Text bold>{title}</Text>
    </Box>
  );
};
```

## Troubleshooting

### Component Not Rendering
- Ensure terminal supports ANSI escape codes
- Check terminal size is adequate (min 80x24)
- Verify Ink version is 5.x: `yarn why ink`

### Input Not Working
- Verify raw mode is enabled in terminal
- Check for conflicting key handlers
- Ensure stdin is in TTY mode

### Styling Issues
- Some terminals may not support all Box props (borderStyle, colors)
- Test in multiple terminal emulators
- Use `supports-color` package to detect capabilities

### Performance
- Limit message history to prevent re-renders
- Use React.memo() for expensive components
- Debounce rapid state updates

## Resources

- [Ink Documentation](https://github.com/vadimdemedes/ink)
- [Ink UI Components](https://github.com/inkjs/ui)
- [cli-highlight](https://github.com/felixfbecker/cli-highlight)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## Contributing

When adding new UI components:
1. Follow the existing component patterns
2. Add TypeScript types to `types.ts`
3. Export from `index.ts`
4. Document props and usage in this README
5. Test in multiple terminal environments
6. Ensure accessibility (screen readers, keyboard navigation)
