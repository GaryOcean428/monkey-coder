# CLI Command Structure - Before & After

## Before Phase 1 Implementation

```
monkey-coder (v1.5.0)
├── implement     - Generate code implementation
├── analyze       - Analyze code for issues
├── build         - Build and optimize architecture
├── test          - Generate tests
├── chat          - Interactive AI chat
├── auth          - Authentication
│   ├── login
│   ├── logout
│   ├── status
│   └── refresh
├── usage         - View usage statistics
├── billing       - Billing management
├── mcp           - MCP server management
└── config        - Basic configuration (flat structure)
    ├── set
    ├── get
    ├── list
    └── reset

Total: 12 commands
```

## After Phase 1 Implementation

```
monkey-coder (v1.5.0)
├── implement     - Generate code implementation
├── analyze       - Analyze code for issues
├── build         - Build and optimize architecture
├── test          - Generate tests
├── chat          - Interactive AI chat
│
├── auth          - Authentication and session management
│   ├── login     - Login to Monkey Coder
│   ├── logout    - Logout from Monkey Coder
│   ├── status    - Check authentication status
│   └── refresh   - Refresh authentication token
│
├── usage         - View usage statistics and costs
├── billing       - Billing and payment management
├── mcp           - Manage MCP servers
│
├── repo (r)      - ⭐ NEW: Manage repositories
│   ├── create    - Create a new repository
│   ├── clone     - Clone a repository
│   ├── fork      - Fork a repository
│   ├── list (ls) - List repositories
│   └── view      - View repository details
│
├── config (cfg)  - ⭐ ENHANCED: Manage configuration
│   ├── get       - Get a configuration value
│   ├── set       - Set a configuration value
│   ├── list (ls) - List all configuration values
│   ├── edit      - Interactively edit configuration
│   ├── unset (delete) - Unset a configuration value
│   └── reset     - Reset configuration to defaults
│
├── git (g)       - ⭐ NEW: Git operations with AI assistance
│   ├── commit    - Create an AI-assisted commit
│   ├── branch    - List, create, or delete branches
│   └── status    - Show the working tree status
│
├── pr            - ⭐ NEW: Manage pull requests
│   ├── create    - Create a pull request
│   ├── list (ls) - List pull requests
│   ├── view      - View a pull request
│   ├── checkout (co) - Check out a pull request
│   └── review    - Review a pull request with AI
│
└── issue         - ⭐ NEW: Manage issues
    ├── create    - Create a new issue
    ├── list (ls) - List issues
    ├── view      - View an issue
    └── close     - Close an issue

Total: 35 commands (+ 7 aliases)
Legend: ⭐ NEW - New in Phase 1, ENHANCED - Significantly improved
        (alias) - Command alias for shortcuts
```

## Command Hierarchy Depth

### Level 1: Main Commands (10)
- implement, analyze, build, test, chat, auth, usage, billing, mcp, health
- **NEW:** repo, config, git, pr, issue

### Level 2: Subcommands (25)
- Auth (4): login, logout, status, refresh
- **NEW Repo (5):** create, clone, fork, list, view
- **NEW Config (6):** get, set, list, edit, unset, reset
- **NEW Git (3):** commit, branch, status
- **NEW PR (5):** create, list, view, checkout, review
- **NEW Issue (4):** create, list, view, close

### Level 3: Options & Flags (100+)
Examples:
- `--ai` (git commit, pr create, issue create)
- `--private` (repo create)
- `--state` (pr list, issue list)
- `--show-secrets` (config list)

## Alias Mapping

```
Short → Full Command
─────────────────────
r     → repo
cfg   → config
g     → git
ls    → list (where applicable)
co    → checkout
```

## Command Categories

### Core AI Commands (5)
- implement, analyze, build, test, chat

### Project Management (15)
- repo (5), pr (5), issue (4), git (3)

### Configuration & Auth (11)
- config (6), auth (4), usage (1)

### Infrastructure (4)
- billing, mcp, health

## Growth Trajectory

```
Current:  35 commands ████████████████████░░░░░░░░ 75%
Target:   40+ commands ████████████████████████████ 100%
Future:   60+ commands (with Phases 2-4)
```

## Usage Examples

### Before (Limited Options)
```bash
monkey implement "create a function"
monkey analyze file.js
monkey config set apiKey sk-123
```

### After (Rich Hierarchy)
```bash
# Repository management
monkey repo create my-app --private --init --license MIT
monkey r clone user/repo  # Using alias

# Enhanced configuration
monkey config edit  # Interactive editor
monkey cfg list --show-secrets  # Using alias

# Git with AI
monkey git commit --ai  # AI generates commit message
monkey g status  # Using alias

# Pull requests
monkey pr create --ai --draft
monkey pr review 123

# Issues
monkey issue create --title "Bug" --labels bug,urgent
```

## Architecture Benefits

1. **Discoverability:** Logical grouping makes commands easier to find
2. **Extensibility:** Easy to add new commands and subcommands
3. **Consistency:** Uniform patterns across all command groups
4. **Aliases:** Power users can work faster
5. **Help:** Rich contextual help at every level

## Next Evolution

Phase 2-4 will add:
- Interactive TUI components
- Tab completion
- Session management
- Extension system
- MCP protocol integration

Target: **60+ commands** with full GitHub CLI and Gemini CLI feature parity
