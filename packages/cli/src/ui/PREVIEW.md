# Ink UI Visual Preview

This document shows what the Ink-based terminal UI looks like in action.

## Chat Mode Interface

```
╭───────────────────────────────────────────────────────────╮
│ 🐵 Monkey Coder | Mode: chat | Tokens: 1247             │
╰───────────────────────────────────────────────────────────╯

You · 10:30:45
  How do I implement a React hook for data fetching?

Monkey · 10:30:47
  Here's a simple custom hook for data fetching with error handling:

╭─────────────────────────────────────────────────────────────╮
│ typescript                                                   │
│    1 │ import { useState, useEffect } from 'react';          │
│    2 │                                                        │
│    3 │ function useFetch<T>(url: string) {                   │
│    4 │   const [data, setData] = useState<T | null>(null);  │
│    5 │   const [loading, setLoading] = useState(true);       │
│    6 │   const [error, setError] = useState<Error | null>... │
│    7 │                                                        │
│    8 │   useEffect(() => {                                   │
│    9 │     fetch(url)                                        │
│   10 │       .then(res => res.json())                        │
│   11 │       .then(setData)                                  │
│   12 │       .catch(setError)                                │
│   13 │       .finally(() => setLoading(false));              │
│   14 │   }, [url]);                                          │
│   15 │                                                        │
│   16 │   return { data, loading, error };                    │
│   17 │ }                                                      │
╰─────────────────────────────────────────────────────────────╯

  This hook provides loading states, error handling, and automatic
  refetching when the URL changes. You can use it like:
  
  const { data, loading, error } = useFetch<User>('/api/user');

┌─────────────────────────────────────────────────────────────┐
│ › Type your message...█                                      │
└─────────────────────────────────────────────────────────────┘

Press ESC or Ctrl+C to exit | Press Enter to send
```

## Agent Mode with Tool Approval

```
╭───────────────────────────────────────────────────────────╮
│ 🐵 Monkey Coder | Mode: agent | Tokens: 2341             │
╰───────────────────────────────────────────────────────────╯

You · 10:35:12
  Create a new config file with API settings

Monkey · 10:35:14
  I'll create a configuration file for you.

╭─────────────────────────────────────────────────────────────╮
│ ⚠️  Tool Execution Request                                  │
│ Tool: file_write                                            │
│                                                              │
│ Arguments:                                                   │
│   {                                                          │
│     "path": "src/config.ts",                                │
│     "content": "export const config = {\n  apiUrl: '...',..." │
│   }                                                          │
│                                                              │
│ [Y]es / [N]o / [ESC] to cancel                             │
╰─────────────────────────────────────────────────────────────╯

○ Create config file
○ Validate configuration
○ Update imports in main file

┌─────────────────────────────────────────────────────────────┐
│ › Waiting for approval...                                    │
└─────────────────────────────────────────────────────────────┘

Press ESC or Ctrl+C to exit | Press Enter to send
```

## Diff Viewer

```
╭───────────────────────────────────────────────────────────╮
│ 🐵 Monkey Coder | Mode: agent | Tokens: 1823             │
╰───────────────────────────────────────────────────────────╯

Monkey · 10:40:22
  I'll update the API endpoint configuration.

┌─────────────────────────────────────────────────────────────┐
│ src/api/config.ts                                           │
│    1   export const API_CONFIG = {                          │
│    2 -   baseUrl: 'http://localhost:3000',                  │
│    2 +   baseUrl: process.env.API_URL || 'http://localhost' │
│    3     timeout: 5000,                                     │
│    4     retries: 3,                                        │
│    5   };                                                   │
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐│
│ │ Apply changes? [Y]es / [N]o                             ││
│ └──────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Task Progress Hierarchy

```
╭───────────────────────────────────────────────────────────╮
│ 🐵 Monkey Coder | Mode: agent | Tokens: 3104             │
╰───────────────────────────────────────────────────────────╯

⏳ Set up new React component
  ✓ Create component file
    ✓ Generate TypeScript interface
    ✓ Write component implementation
  ⏳ Create test file
    ✓ Set up test suite
    ○ Write unit tests
    ○ Add integration tests
  ○ Update index exports

⚡ Executing: file_write

┌─────────────────────────────────────────────────────────────┐
│ › Processing...                                              │
└─────────────────────────────────────────────────────────────┘
```

## Color Legend

In actual terminal output:

- **Cyan** (🐵 Monkey Coder, borders) - Brand color
- **Green** (You, ✓, +) - User messages, success, additions
- **Blue** (› prompt) - Input prompt
- **Yellow** (⚡, ⏳, Monkey) - Processing, warnings, assistant
- **Red** (✗, -) - Errors, deletions
- **Gray** (timestamps, context, ○) - Metadata, pending tasks
- **White** (inverse text) - Cursor, highlights

## Status Icons

- **🐵** - Monkey Coder branding
- **⏳** - Thinking/Processing (hourglass)
- **⚡** - Tool execution (lightning bolt)
- **✓** - Completed (checkmark)
- **✗** - Failed (X mark)
- **○** - Pending (circle)
- **⚠️** - Warning/Approval needed
- **█** - Cursor (inverse space)

## Interactive Elements

All components respond to keyboard input:
- Text appears as you type (character-by-character)
- Backspace deletes the last character
- Enter submits the current input
- Y/N keys for approvals
- ESC cancels/exits
- Ctrl+C force exits

## Terminal Requirements

- Minimum 80 columns × 24 rows
- ANSI color support (256-color recommended)
- Unicode support for emojis and box-drawing characters
- Modern terminal emulator (iTerm2, Windows Terminal, Hyper, etc.)

## Tips

1. **Syntax Highlighting**: Code blocks automatically detect language and apply colors
2. **Word Wrapping**: Long lines wrap automatically to fit terminal width
3. **Scrolling**: Message history scrolls automatically as new messages arrive
4. **Context Preservation**: All messages persist to SQLite for session continuity
5. **Graceful Degradation**: Falls back to simpler display on limited terminals
