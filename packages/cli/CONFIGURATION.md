# .monkey-coder.json Example

This is a comprehensive example of a `.monkey-coder.json` configuration file showing all available options.

```json
{
  "version": 1,
  "permissions": {
    "allowedPaths": [
      "./**/*",
      "../shared-lib/**/*"
    ],
    "deniedPaths": [
      "**/.env*",
      "**/.git/**",
      "**/node_modules/**",
      "**/*.pem",
      "**/*.key",
      "**/secrets/**",
      "**/build/**",
      "**/dist/**"
    ],
    "allowedCommands": [
      "git status",
      "git diff *",
      "git log *",
      "git branch *",
      "npm *",
      "yarn *",
      "pnpm *",
      "bun *",
      "ls *",
      "cat *",
      "head *",
      "tail *",
      "grep *",
      "find *",
      "wc *",
      "echo *",
      "pwd",
      "whoami",
      "date"
    ],
    "deniedCommands": [
      "rm -rf /*",
      "rm -rf ~/*",
      "sudo *",
      "su *",
      "chmod 777 *",
      "curl * | sh",
      "wget * | sh",
      "* > /dev/*",
      "dd *",
      "mkfs *",
      ":(){:|:&};:"
    ],
    "requireApproval": true,
    "maxFileSize": 10485760,
    "timeout": 30000
  },
  "mcp": {
    "servers": [
      {
        "name": "filesystem",
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
        "enabled": true
      },
      {
        "name": "github",
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "enabled": true
      },
      {
        "name": "custom-api",
        "type": "http",
        "url": "https://your-mcp-server.example.com",
        "enabled": false
      }
    ]
  },
  "agent": {
    "defaultProvider": "anthropic",
    "defaultModel": "claude-sonnet-4-5-20250929",
    "maxIterations": 10,
    "autoApprove": false,
    "sandbox": "basic"
  }
}
```

## Configuration Options

### Version
- **version** (required): Configuration schema version. Currently only `1` is supported.

### Permissions

Controls what files and commands the agent can access.

#### Path Permissions
- **allowedPaths**: Array of glob patterns for allowed file paths
  - Example: `["./**/*", "../shared/**/*"]`
  - Default: `["./**/*"]`
  
- **deniedPaths**: Array of glob patterns for denied file paths (takes precedence)
  - Example: `["**/.env*", "**/.git/**", "**/node_modules/**"]`
  - Always deny sensitive files like `.env*`, private keys (`*.pem`, `*.key`)

#### Command Permissions
- **allowedCommands**: Array of command patterns that are allowed
  - Wildcards (`*`) are supported
  - Example: `["git *", "npm *", "ls *"]`
  
- **deniedCommands**: Array of command patterns that are explicitly denied (takes precedence)
  - Always deny destructive commands: `"rm -rf /*"`, `"sudo *"`, `"chmod 777 *"`

#### Safety Settings
- **requireApproval**: Boolean, whether to require user approval for commands
  - Default: `true`
  - Set to `false` for fully autonomous operation (not recommended)
  
- **maxFileSize**: Maximum file size in bytes that can be read
  - Default: `10485760` (10MB)
  
- **timeout**: Command execution timeout in milliseconds
  - Default: `30000` (30 seconds)

### MCP (Model Context Protocol)

Configure external tool servers that extend the agent's capabilities.

- **servers**: Array of MCP server configurations
  - **name**: Unique identifier for the server
  - **type**: Transport type - `"stdio"`, `"sse"`, or `"http"`
  - **command**: Command to execute (stdio only)
  - **args**: Command arguments array (stdio only)
  - **url**: Server URL (http/sse only)
  - **enabled**: Whether to connect to this server (default: `true`)

**Example MCP Servers:**
```json
{
  "servers": [
    {
      "name": "filesystem",
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    },
    {
      "name": "github",
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    },
    {
      "name": "brave-search",
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"]
    }
  ]
}
```

### Agent

Agent behavior defaults.

- **defaultProvider**: AI provider to use
  - Options: `"openai"`, `"anthropic"`, `"google"`
  - Default: `"anthropic"`
  
- **defaultModel**: Model identifier
  - Examples: `"claude-sonnet-4-5-20250929"`, `"gpt-4"`, `"gemini-pro"`
  - Default: `"claude-sonnet-4-5-20250929"`
  
- **maxIterations**: Maximum agent iterations per task
  - Default: `10`
  
- **autoApprove**: Automatically approve all tool executions
  - Default: `false`
  - ⚠️ Use with caution
  
- **sandbox**: Sandbox type for command execution
  - Options: `"none"`, `"basic"`, `"docker"`
  - Default: `"basic"`

## Configuration Precedence

Configurations are loaded and merged in this order:

1. **Defaults** - Built-in safe defaults
2. **Global config** - `~/.config/monkey-coder/config.json`
3. **Project config** - `.monkey-coder.json` in current or parent directories

Project configs override global configs, which override defaults.

## Commands

### Initialize Configuration
```bash
monkey config init
```

Creates a `.monkey-coder.json` with sensible defaults in the current directory.

### Show Resolved Configuration
```bash
monkey config show
monkey config show --json  # Output as JSON
```

Displays the final merged configuration from all sources.

### Show Configuration Paths
```bash
monkey config path
```

Shows where configuration files are searched for and which ones are currently active.

## Security Best Practices

1. **Always deny sensitive paths:**
   ```json
   "deniedPaths": [
     "**/.env*",
     "**/*.pem",
     "**/*.key",
     "**/secrets/**"
   ]
   ```

2. **Always deny destructive commands:**
   ```json
   "deniedCommands": [
     "rm -rf /*",
     "sudo *",
     "chmod 777 *"
   ]
   ```

3. **Keep `requireApproval` enabled** unless you fully trust the agent and code.

4. **Use specific allowed commands** rather than wildcard everything:
   ```json
   "allowedCommands": [
     "git status",
     "git diff *",
     "npm test",
     "yarn build"
   ]
   ```

5. **Set reasonable limits:**
   ```json
   {
     "maxFileSize": 10485760,  // 10MB
     "timeout": 30000,         // 30 seconds
     "maxIterations": 10
   }
   ```

## Troubleshooting

### Config not loading
- Check file name: must be `.monkey-coder.json`, `.monkeycoderrc`, or `.monkeycoderrc.json`
- Verify JSON syntax: use `monkey config show` to see errors
- Check file location: must be in current directory or parent directories

### Permissions not working
- Verify glob patterns match your file structure
- Remember `deniedPaths` takes precedence over `allowedPaths`
- Remember `deniedCommands` takes precedence over `allowedCommands`

### MCP servers not connecting
- Ensure server packages are installed
- Check server `enabled` flag is `true`
- Verify command and args are correct
- Check server logs for errors
