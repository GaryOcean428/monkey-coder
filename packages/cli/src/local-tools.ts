/**
 * Local Tools Executor - Safe file and shell operations for local agent mode
 * 
 * Provides sandboxed execution of file operations and shell commands with
 * proper security controls, approval workflows, and checkpoint integration.
 */

import { spawn, SpawnOptions } from 'child_process';
import * as fs from 'fs';
import * as fsPromises from 'fs/promises';
import * as path from 'path';
import fg from 'fast-glob';
import chalk from 'chalk';

import { CheckpointManager, getCheckpointManager } from './checkpoint-manager.js';
import { getSandbox, DockerSandbox } from './sandbox/docker-executor.js';
import { loadConfig } from './config/loader.js';
import { PermissionManager } from './permissions.js';

// Types
export interface ToolResult {
  success: boolean;
  output?: string;
  error?: string;
  requiresApproval?: boolean;
}

export interface FileReadResult extends ToolResult {
  content?: string;
  encoding?: string;
}

export interface FileWriteResult extends ToolResult {
  bytesWritten?: number;
  path?: string;
}

export interface ShellResult extends ToolResult {
  stdout?: string;
  stderr?: string;
  exitCode?: number;
}

export interface PermissionConfig {
  allowedPaths: string[];       // Glob patterns for allowed paths
  deniedPaths: string[];        // Glob patterns for denied paths
  allowedCommands: string[];    // Allowed shell commands (with wildcards)
  deniedCommands: string[];     // Denied shell commands
  requireApproval: boolean;     // Require user approval for destructive ops
  maxFileSize: number;          // Max file size in bytes
  timeout: number;              // Command timeout in ms
}

const DEFAULT_PERMISSIONS: PermissionConfig = {
  allowedPaths: ['./**/*'],
  deniedPaths: [
    '**/.env*',
    '**/.git/**',
    '**/node_modules/**',
    '**/*.pem',
    '**/*.key',
    '**/secrets/**',
  ],
  allowedCommands: [
    'ls *', 'cat *', 'head *', 'tail *', 'wc *',
    'grep *', 'find *', 'tree *',
    'git status', 'git diff *', 'git log *', 'git branch *',
    'npm list *', 'npm outdated', 'npm audit',
    'yarn info *', 'yarn why *',
    'python --version', 'node --version',
    'echo *', 'pwd', 'whoami', 'date',
  ],
  deniedCommands: [
    'rm -rf /*', 'rm -rf ~/*', 'rm -rf /',
    'sudo *', 'su *',
    'chmod 777 *',
    'curl * | sh', 'wget * | sh',
    '* > /dev/*',
    'dd *',
    'mkfs *',
    ':(){:|:&};:',  // Fork bomb
  ],
  requireApproval: true,
  maxFileSize: 10 * 1024 * 1024,  // 10MB
  timeout: 30000,  // 30 seconds
};

/**
 * Check if a path matches any pattern in a list
 * Uses string matching instead of regex for security
 */
function matchesPattern(filepath: string, patterns: string[]): boolean {
  const normalizedPath = path.normalize(filepath).replace(/\\/g, '/');
  
  for (const pattern of patterns) {
    const normalizedPattern = pattern.replace(/\\/g, '/');
    
    // Handle exact match (no wildcards)
    if (!normalizedPattern.includes('*')) {
      if (normalizedPath === normalizedPattern || normalizedPath.startsWith(normalizedPattern + '/')) {
        return true;
      }
      continue;
    }
    
    // Handle ** (match any depth)
    if (normalizedPattern.includes('**')) {
      const parts = normalizedPattern.split('**');
      if (parts.length === 2) {
        const prefix = parts[0] || '';
        const suffix = parts[1] || '';
        const cleanPrefix = prefix.replace(/\/$/, '');
        const cleanSuffix = suffix.replace(/^\//, '');
        
        const matchesPrefix = !cleanPrefix || normalizedPath.startsWith(cleanPrefix);
        const matchesSuffix = !cleanSuffix || normalizedPath.endsWith(cleanSuffix);
        
        if (matchesPrefix && matchesSuffix) {
          return true;
        }
      }
      continue;
    }
    
    // Handle * (match within segment - does not cross /)
    if (normalizedPattern.includes('*')) {
      const parts = normalizedPattern.split('*');
      let currentIndex = 0;
      let matches = true;
      
      for (let i = 0; i < parts.length; i++) {
        const part = parts[i];
        if (part === '' || part === undefined) {
          if (i === 0 || i === parts.length - 1) continue;
        }
        
        if (!part) continue;  // Skip empty parts
        
        const index = normalizedPath.indexOf(part, currentIndex);
        if (index === -1) {
          matches = false;
          break;
        }
        
        // Check that * doesn't cross directory boundaries
        const segmentBetween = normalizedPath.slice(currentIndex, index);
        if (segmentBetween.includes('/')) {
          matches = false;
          break;
        }
        
        // First part must match start, last part must match end
        if (i === 0 && index !== 0) {
          matches = false;
          break;
        }
        if (i === parts.length - 1 && index + part.length !== normalizedPath.length) {
          matches = false;
          break;
        }
        
        currentIndex = index + part.length;
      }
      
      if (matches) {
        return true;
      }
    }
  }
  
  return false;
}

/**
 * Check if a command matches any pattern
 * Uses string matching instead of regex for security
 */
function commandMatchesPattern(command: string, patterns: string[]): boolean {
  for (const pattern of patterns) {
    // Handle exact match
    if (!pattern.includes('*')) {
      if (command === pattern) {
        return true;
      }
      continue;
    }
    
    // Handle wildcards with string matching
    const parts = pattern.split('*');
    let currentIndex = 0;
    let matches = true;
    
    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      if (part === '' || part === undefined) {
        if (i === 0 || i === parts.length - 1) continue;
      }
      
      if (!part) continue;  // Skip empty or undefined parts
      
      // Handle whitespace pattern matching
      const normalizedPart = part.replace(/\\s\+/g, ' ');
      const index = command.indexOf(normalizedPart, currentIndex);
      
      if (index === -1) {
        matches = false;
        break;
      }
      
      // First part must match start, last part must match end
      if (i === 0 && index !== 0) {
        matches = false;
        break;
      }
      if (i === parts.length - 1 && index + normalizedPart.length !== command.length) {
        matches = false;
        break;
      }
      
      currentIndex = index + normalizedPart.length;
    }
    
    if (matches) {
      return true;
    }
  }
  
  return false;
}

/**
 * Validate path is within allowed boundaries and not in denied list
 */
function validatePath(
  filepath: string,
  basePath: string,
  permissions: PermissionConfig
): { valid: boolean; error?: string } {
  const absolutePath = path.resolve(basePath, filepath);
  const normalizedBase = path.resolve(basePath);

  // Check for path traversal
  if (!absolutePath.startsWith(normalizedBase)) {
    return { valid: false, error: 'Path traversal detected' };
  }

  // Check denied paths first
  const relativePath = path.relative(normalizedBase, absolutePath);
  if (matchesPattern(relativePath, permissions.deniedPaths)) {
    return { valid: false, error: 'Path is in denied list' };
  }

  // Check allowed paths
  if (!matchesPattern(relativePath, permissions.allowedPaths)) {
    return { valid: false, error: 'Path is not in allowed list' };
  }

  return { valid: true };
}

/**
 * Validate command is allowed
 */
function validateCommand(
  command: string,
  permissions: PermissionConfig
): { valid: boolean; error?: string; requiresApproval?: boolean } {
  // Check denied commands first
  if (commandMatchesPattern(command, permissions.deniedCommands)) {
    return { valid: false, error: 'Command is explicitly denied' };
  }

  // Check allowed commands
  if (!commandMatchesPattern(command, permissions.allowedCommands)) {
    if (permissions.requireApproval) {
      return { valid: true, requiresApproval: true };
    }
    return { valid: false, error: 'Command is not in allowed list' };
  }

  return { valid: true };
}

/**
 * Local Tools Executor class
 */
export class LocalToolsExecutor {
  private basePath: string;
  private permissions: PermissionConfig;
  private permissionManager: PermissionManager;
  private checkpointManager: CheckpointManager | null = null;
  private approvalCallback?: (message: string) => Promise<boolean>;
  private sandbox: DockerSandbox | null = null;

  constructor(options: {
    basePath?: string;
    permissions?: Partial<PermissionConfig>;
    approvalCallback?: (message: string) => Promise<boolean>;
  } = {}) {
    this.basePath = options.basePath || process.cwd();
    this.permissions = { ...DEFAULT_PERMISSIONS, ...options.permissions };
    this.permissionManager = new PermissionManager(this.basePath);
    this.approvalCallback = options.approvalCallback;
  }

  /**
   * Initialize with checkpoint manager and Docker sandbox
   * Also loads permissions from config file if available
   */
  async initialize(): Promise<void> {
    // Load config file and merge permissions if available
    try {
      const config = await loadConfig(this.basePath);
      // Merge config permissions with constructor permissions (constructor takes precedence)
      this.permissions = { 
        ...DEFAULT_PERMISSIONS, 
        ...config.permissions,
        ...this.permissions 
      };
    } catch (error) {
      // Config loading is optional, use defaults if it fails
      console.warn(chalk.yellow('⚠ Failed to load config, using default permissions'));
    }
    
    this.checkpointManager = await getCheckpointManager(this.basePath);
    this.sandbox = await getSandbox();
    if (this.sandbox) {
      console.log(chalk.green('✓ Docker sandbox available'));
    } else {
      console.log(chalk.yellow('⚠ Docker not available, using basic sandbox'));
    }
  }

  /**
   * Request user approval for an operation
   */
  private async requestApproval(message: string): Promise<boolean> {
    if (!this.permissions.requireApproval) {
      return true;
    }

    if (this.approvalCallback) {
      return this.approvalCallback(message);
    }

    // Default: deny if no callback
    console.warn(`[LocalTools] Approval required but no callback set: ${message}`);
    return false;
  }

  /**
   * Read a file
   */
  async readFile(filepath: string): Promise<FileReadResult> {
    // Use PermissionManager for validation
    const permCheck = this.permissionManager.canReadFile(filepath);
    if (!permCheck.allowed) {
      return { success: false, error: permCheck.reason };
    }

    const absolutePath = path.resolve(this.basePath, filepath);

    try {
      const stats = await fsPromises.stat(absolutePath);
      
      if (stats.size > this.permissions.maxFileSize) {
        return { 
          success: false, 
          error: `File too large: ${stats.size} bytes (max: ${this.permissions.maxFileSize})` 
        };
      }

      const content = await fsPromises.readFile(absolutePath, 'utf-8');
      
      return {
        success: true,
        content,
        encoding: 'utf-8',
        output: `Read ${stats.size} bytes from ${filepath}`,
      };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Write to a file
   */
  async writeFile(filepath: string, content: string): Promise<FileWriteResult> {
    // Use PermissionManager for validation
    const permCheck = this.permissionManager.canWriteFile(filepath);
    if (!permCheck.allowed) {
      return { success: false, error: permCheck.reason };
    }

    const absolutePath = path.resolve(this.basePath, filepath);

    // Check approval for write operations if tool requires it
    if (this.permissionManager.toolRequiresApproval('file_write')) {
      const approved = await this.requestApproval(
        `Write ${content.length} bytes to ${filepath}?`
      );
      if (!approved) {
        return { success: false, error: 'Operation not approved', requiresApproval: true };
      }
    }

    try {
      // Record operation for undo
      let beforeContent: string | undefined;
      if (fs.existsSync(absolutePath)) {
        beforeContent = await fsPromises.readFile(absolutePath, 'utf-8');
      }

      // Ensure directory exists
      await fsPromises.mkdir(path.dirname(absolutePath), { recursive: true });
      
      // Write file
      await fsPromises.writeFile(absolutePath, content, 'utf-8');

      // Record operation
      if (this.checkpointManager) {
        if (beforeContent) {
          await this.checkpointManager.recordFileEdit(filepath, beforeContent, content);
        } else {
          await this.checkpointManager.recordFileCreate(filepath, content);
        }
      }

      return {
        success: true,
        bytesWritten: content.length,
        path: filepath,
        output: `Wrote ${content.length} bytes to ${filepath}`,
      };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Delete a file
   * Note: Uses write permission check as deletion is a form of file modification
   */
  async deleteFile(filepath: string): Promise<ToolResult> {
    // Use PermissionManager for validation - writeFile validation for deletion
    const permCheck = this.permissionManager.canWriteFile(filepath);
    if (!permCheck.allowed) {
      return { success: false, error: permCheck.reason };
    }

    const absolutePath = path.resolve(this.basePath, filepath);

    // Check approval if tool requires it
    if (this.permissionManager.toolRequiresApproval('file_delete')) {
      const approved = await this.requestApproval(`Delete file ${filepath}?`);
      if (!approved) {
        return { success: false, error: 'Operation not approved', requiresApproval: true };
      }
    }

    try {
      // Read content for undo
      const beforeContent = await fsPromises.readFile(absolutePath, 'utf-8');
      
      // Delete file
      await fsPromises.unlink(absolutePath);

      // Record operation
      if (this.checkpointManager) {
        await this.checkpointManager.recordFileDelete(filepath, beforeContent);
        await this.checkpointManager.recordFileDelete(absolutePath, beforeContent);
      }

      return { success: true, output: `Deleted ${filepath}` };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  /**
   * List files matching a pattern
   */
  async listFiles(pattern: string = '**/*'): Promise<ToolResult & { files?: string[] }> {
    try {
      const files = await fg(pattern, {
        cwd: this.basePath,
        ignore: this.permissions.deniedPaths,
        dot: false,
      });

      return {
        success: true,
        files,
        output: `Found ${files.length} files`,
      };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Execute a shell command
   */
  async executeCommand(command: string, args: string[] = []): Promise<ShellResult> {
    const fullCommand = args.length > 0 ? `${command} ${args.join(' ')}` : command;
    
    // Use PermissionManager for validation
    const permCheck = this.permissionManager.canExecuteCommand(fullCommand);
    if (!permCheck.allowed) {
      return { success: false, error: permCheck.reason };
    }

    // Check approval if required
    if (permCheck.requiresApproval || this.permissionManager.toolRequiresApproval('shell_execute')) {
      const approved = await this.requestApproval(
        `Execute command: ${fullCommand}?`
      );
      if (!approved) {
        return { success: false, error: 'Operation not approved', requiresApproval: true };
      }
    }

    return new Promise((resolve) => {
      const spawnOptions: SpawnOptions = {
        cwd: this.basePath,
        shell: false,  // Important: don't use shell to prevent injection
        timeout: this.permissions.timeout,
        env: { ...process.env, PATH: process.env.PATH },
      };

      // Use spawn with array args to prevent injection
      const child = spawn(command, args, spawnOptions);

      let stdout = '';
      let stderr = '';

      child.stdout?.on('data', (data) => {
        stdout += data.toString();
      });

      child.stderr?.on('data', (data) => {
        stderr += data.toString();
      });

      child.on('error', (error) => {
        resolve({
          success: false,
          error: error.message,
          stdout,
          stderr,
          exitCode: -1,
        });
      });

      child.on('close', (code) => {
        resolve({
          success: code === 0,
          stdout,
          stderr,
          exitCode: code || 0,
          output: stdout || stderr,
          error: code !== 0 ? stderr : undefined,
        });
      });
    });
  }

  /**
   * Execute a command in Docker sandbox if available
   */
  async executeCommandSandboxed(
    command: string,
    args: string[] = []
  ): Promise<ShellResult> {
    if (this.sandbox) {
      const result = await this.sandbox.execute([command, ...args], {
        binds: [`${this.basePath}:/workspace:rw`],
      });
      return {
        success: result.exitCode === 0,
        stdout: result.stdout,
        stderr: result.stderr,
        exitCode: result.exitCode,
        output: result.stdout || result.stderr,
        error: result.exitCode !== 0 ? result.stderr : undefined,
      };
    }
    // Fallback to basic spawn
    return this.executeCommand(command, args);
  }

  /**
   * Search for text in files
   * Uses case-insensitive string includes() instead of regex for security
   */
  async searchFiles(
    query: string,
    options: { pattern?: string; maxResults?: number; caseSensitive?: boolean } = {}
  ): Promise<ToolResult & { matches?: Array<{ file: string; line: number; content: string }> }> {
    const { pattern = '**/*', maxResults = 100, caseSensitive = false } = options;

    try {
      const files = await fg(pattern, {
        cwd: this.basePath,
        ignore: this.permissions.deniedPaths,
        dot: false,
      });

      const matches: Array<{ file: string; line: number; content: string }> = [];
      const searchTerm = caseSensitive ? query : query.toLowerCase();

      for (const file of files) {
        if (matches.length >= maxResults) break;

        const validation = validatePath(file, this.basePath, this.permissions);
        if (!validation.valid) continue;

        try {
          const content = await fsPromises.readFile(
            path.join(this.basePath, file),
            'utf-8'
          );

          const lines = content.split('\n');
          for (let i = 0; i < lines.length && matches.length < maxResults; i++) {
            const line = lines[i];
            if (!line) continue;
            
            const searchLine = caseSensitive ? line : line.toLowerCase();
            if (searchLine.includes(searchTerm)) {
              matches.push({
                file,
                line: i + 1,
                content: line.trim().slice(0, 200),
              });
            }
          }
        } catch {
          // Skip files that can't be read
        }
      }

      return {
        success: true,
        matches,
        output: `Found ${matches.length} matches`,
      };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Get file info
   */
  async getFileInfo(filepath: string): Promise<ToolResult & { 
    stats?: { size: number; modified: Date; isDirectory: boolean } 
  }> {
    const validation = validatePath(filepath, this.basePath, this.permissions);
    if (!validation.valid) {
      return { success: false, error: validation.error };
    }

    const absolutePath = path.resolve(this.basePath, filepath);

    try {
      const stats = await fsPromises.stat(absolutePath);
      
      return {
        success: true,
        stats: {
          size: stats.size,
          modified: stats.mtime,
          isDirectory: stats.isDirectory(),
        },
        output: `${filepath}: ${stats.size} bytes, modified ${stats.mtime.toISOString()}`,
      };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Update permissions at runtime
   */
  updatePermissions(permissions: Partial<PermissionConfig>): void {
    this.permissions = { ...this.permissions, ...permissions };
  }

  /**
   * Set approval callback
   */
  setApprovalCallback(callback: (message: string) => Promise<boolean>): void {
    this.approvalCallback = callback;
  }
}

// Singleton instance
let defaultExecutor: LocalToolsExecutor | null = null;

export async function getLocalToolsExecutor(options?: {
  basePath?: string;
  permissions?: Partial<PermissionConfig>;
}): Promise<LocalToolsExecutor> {
  if (!defaultExecutor) {
    defaultExecutor = new LocalToolsExecutor(options);
    await defaultExecutor.initialize();
  }
  return defaultExecutor;
}

export function closeLocalToolsExecutor(): void {
  defaultExecutor = null;
}
