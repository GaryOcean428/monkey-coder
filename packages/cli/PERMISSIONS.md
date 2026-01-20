# Permission System

Glob-based permission system for file access and command execution, inspired by Claude Code's settings.json approach.

## Overview

The permission system provides fine-grained control over:
- **File Read**: Which files the agent can read
- **File Write**: Which files the agent can modify or create
- **Shell Execute**: Which commands the agent can run
- **Approval Requirements**: Which operations require user approval

## Configuration Locations

Permissions are loaded from two locations (project > global):

1. **Global**: `~/.monkey-coder/permissions.json` - System-wide defaults
2. **Project**: `./.monkeyrc.json` - Project-specific overrides

## Default Permissions

### File Read
**Allow:**
- `**/*` - All files by default

**Deny:**
- `**/.env*` - Environment files
- `**/secrets*` - Secret files
- `**/*.pem` - PEM certificates
- `**/*.key` - Key files
- `**/.ssh/**` - SSH directory

### File Write
**Allow:**
- `**/*` - All files by default

**Deny:**
- `**/.git/**` - Git directory
- `**/node_modules/**` - Dependencies
- `**/.env*` - Environment files
- `**/*.pem` - Certificates
- `**/*.key` - Key files

### Shell Execute
**Allow:**
- `npm *`, `yarn *`, `pnpm *` - Package managers
- `git *` - Git commands
- `node *`, `python *`, `pytest *` - Runtimes and testing
- `ls *`, `cat *`, `grep *`, `find *` - Safe utilities

**Deny:**
- `rm -rf /*` - Dangerous deletions
- `sudo *` - Elevated privileges
- `curl * | sh`, `wget * | sh` - Piped execution
- `dd *`, `mkfs *` - Low-level operations

### Require Approval
- `shell_execute` - All shell commands
- `file_delete` - File deletions
- `file_write` - File modifications

## CLI Commands

### List Permissions
```bash
# Show merged permissions (global + project)
monkey config permissions list

# Show only global permissions
monkey config permissions list --global

# Show only project permissions
monkey config permissions list --project

# Output as JSON
monkey config permissions list --json
```

### Add Allow Rules
```bash
# Allow reading TypeScript files
monkey config permissions allow fileRead "src/**/*.ts"

# Allow docker commands
monkey config permissions allow shellExecute "docker *"

# Allow writing to dist (project-specific)
monkey config permissions allow fileWrite "dist/**/*" --project
```

### Add Deny Rules
```bash
# Deny reading .env files
monkey config permissions deny fileRead "**/.env*"

# Deny dangerous rm command
monkey config permissions deny shellExecute "rm -rf /*"

# Deny writing to node_modules (project-specific)
monkey config permissions deny fileWrite "**/node_modules/**" --project
```

### Test Permissions
```bash
# Test if .env file can be read
monkey config permissions test read ".env"

# Test if src/index.ts can be written
monkey config permissions test write "src/index.ts"

# Test if npm install command is allowed
monkey config permissions test command "npm install"
```

### Reset Permissions
```bash
# Reset global permissions to defaults
monkey config permissions reset --global

# Remove all project-specific permissions
monkey config permissions reset --project

# Skip confirmation
monkey config permissions reset --global --force
```

## Glob Pattern Examples

### File Patterns
- `**/*.ts` - All TypeScript files (any depth)
- `src/**/*.js` - All JS files in src (any depth)
- `*.json` - All JSON files in current directory
- `.env*` - All files starting with .env
- `**/.git/**` - All files in .git directory (any depth)

### Command Patterns
- `npm *` - Any npm command
- `git status` - Exact command
- `docker run *` - Docker run with any arguments
- `rm -rf /*` - Dangerous deletion pattern

## Programmatic Usage

```typescript
import { PermissionManager } from './permissions';

const permMgr = new PermissionManager('/path/to/project');

// Check file read permission
const readCheck = permMgr.canReadFile('src/index.ts');
if (readCheck.allowed) {
  // Read file
} else {
  console.error(readCheck.reason);
}

// Check file write permission
const writeCheck = permMgr.canWriteFile('dist/output.js');
if (writeCheck.allowed) {
  // Write file
}

// Check command execution permission
const cmdCheck = permMgr.canExecuteCommand('npm install');
if (cmdCheck.allowed) {
  if (cmdCheck.requiresApproval) {
    // Request user approval
  }
  // Execute command
}

// Check if tool requires approval
if (permMgr.toolRequiresApproval('file_write')) {
  // Request approval before writing
}
```

## Project Configuration (.monkeyrc.json)

```json
{
  "permissions": {
    "fileRead": {
      "allow": ["**/*.ts", "**/*.tsx"],
      "deny": ["**/*.test.ts"]
    },
    "fileWrite": {
      "allow": ["src/**/*"],
      "deny": ["src/generated/**"]
    },
    "shellExecute": {
      "allow": ["npm run *", "docker-compose *"],
      "deny": ["npm publish"]
    },
    "requireApproval": ["shell_execute"]
  }
}
```

## Global Configuration (~/.monkey-coder/permissions.json)

```json
{
  "fileRead": {
    "allow": ["**/*"],
    "deny": ["**/.env*", "**/secrets*", "**/*.pem", "**/*.key", "**/.ssh/**"]
  },
  "fileWrite": {
    "allow": ["**/*"],
    "deny": ["**/.git/**", "**/node_modules/**", "**/.env*"]
  },
  "shellExecute": {
    "allow": ["npm *", "yarn *", "git *", "node *", "python *"],
    "deny": ["rm -rf /*", "sudo *", "curl * | sh", "wget * | sh"]
  },
  "requireApproval": ["shell_execute", "file_delete", "file_write"]
}
```

## Security Best Practices

1. **Start Restrictive**: Begin with a minimal allow list and expand as needed
2. **Explicit Denials**: Always explicitly deny dangerous operations
3. **Require Approval**: Use `requireApproval` for sensitive operations
4. **Project Overrides**: Use project configs for project-specific needs
5. **Test First**: Use `monkey config permissions test` before running operations
6. **Review Regularly**: Audit permissions periodically

## Pattern Precedence

When checking permissions:
1. **Deny patterns** are checked first
2. If denied, access is immediately blocked
3. **Allow patterns** are checked next
4. If no allow pattern matches, access is blocked
5. **Project rules** override global rules (patterns are merged)

## Approval Workflow

For operations requiring approval:
1. Permission check passes
2. System checks `requireApproval` list
3. If required, approval callback is invoked
4. User approves or denies the operation
5. Operation proceeds or is blocked

## Troubleshooting

### Permission Denied Errors

```bash
# Check current permissions
monkey config permissions list

# Test specific operation
monkey config permissions test read "path/to/file"

# View effective rules (merged)
monkey config permissions list --json
```

### Adding New Patterns

```bash
# Add to project (recommended for project-specific needs)
monkey config permissions allow fileRead "newPattern" --project

# Add to global (for system-wide defaults)
monkey config permissions allow fileRead "newPattern" --global
```

### Reset After Mistakes

```bash
# Reset project permissions
monkey config permissions reset --project --force

# Reset global permissions
monkey config permissions reset --global --force
```

## Migration from Basic Pattern Matching

The new PermissionManager uses `minimatch` for proper glob pattern matching instead of basic string operations. Benefits:

- ✅ Standard glob pattern syntax
- ✅ Proper `**` (globstar) support
- ✅ Correct `*` (wildcard) behavior
- ✅ Dot file handling
- ✅ Better path normalization

If you had custom pattern matching logic, it should be replaced with PermissionManager calls.
