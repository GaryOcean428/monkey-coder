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
import * as os from 'os';
import fg from 'fast-glob';
import { CheckpointManager, getCheckpointManager } from './checkpoint-manager.js';

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
 */
function matchesPattern(filepath: string, patterns: string[]): boolean {
  const normalizedPath = path.normalize(filepath);
  
  for (const pattern of patterns) {
    // Simple glob matching (supports * and **)
    const regex = pattern
      .replace(/\*\*/g, '<<<GLOBSTAR>>>')
      .replace(/\*/g, '[^/]*')
      .replace(/<<<GLOBSTAR>>>/g, '.*')
      .replace(/\//g, '\\/');
    
    if (new RegExp(`^${regex}$`).test(normalizedPath)) {
      return true;
    }
  }
  
  return false;
}

/**
 * Check if a command matches any pattern
 */
function commandMatchesPattern(command: string, patterns: string[]): boolean {
  for (const pattern of patterns) {
    const regex = pattern
      .replace(/\*/g, '.*')
      .replace(/\s+/g, '\\s+');
    
    if (new RegExp(`^${regex}$`).test(command)) {
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
  private checkpointManager: CheckpointManager | null = null;
  private approvalCallback?: (message: string) => Promise<boolean>;

  constructor(options: {
    basePath?: string;
    permissions?: Partial<PermissionConfig>;
    approvalCallback?: (message: string) => Promise<boolean>;
  } = {}) {
    this.basePath = options.basePath || process.cwd();
    this.permissions = { ...DEFAULT_PERMISSIONS, ...options.permissions };
    this.approvalCallback = options.approvalCallback;
  }

  /**
   * Initialize with checkpoint manager
   */
  async initialize(): Promise<void> {
    this.checkpointManager = await getCheckpointManager(this.basePath);
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
    const validation = validatePath(filepath, this.basePath, this.permissions);
    if (!validation.valid) {
      return { success: false, error: validation.error };
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
    const validation = validatePath(filepath, this.basePath, this.permissions);
    if (!validation.valid) {
      return { success: false, error: validation.error };
    }

    const absolutePath = path.resolve(this.basePath, filepath);

    // Check approval for write operations
    const approved = await this.requestApproval(
      `Write ${content.length} bytes to ${filepath}?`
    );
    if (!approved) {
      return { success: false, error: 'Operation not approved', requiresApproval: true };
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
        if (beforeContent !== undefined) {
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
   */
  async deleteFile(filepath: string): Promise<ToolResult> {
    const validation = validatePath(filepath, this.basePath, this.permissions);
    if (!validation.valid) {
      return { success: false, error: validation.error };
    }

    const absolutePath = path.resolve(this.basePath, filepath);

    // Check approval
    const approved = await this.requestApproval(`Delete file ${filepath}?`);
    if (!approved) {
      return { success: false, error: 'Operation not approved', requiresApproval: true };
    }

    try {
      // Read content for undo
      const beforeContent = await fsPromises.readFile(absolutePath, 'utf-8');
      
      // Delete file
      await fsPromises.unlink(absolutePath);

      // Record operation
      if (this.checkpointManager) {
        await this.checkpointManager.recordFileDelete(filepath, beforeContent);
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
    
    const validation = validateCommand(fullCommand, this.permissions);
    if (!validation.valid) {
      return { success: false, error: validation.error };
    }

    if (validation.requiresApproval) {
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
   * Search for text in files
   */
  async searchFiles(
    query: string,
    options: { pattern?: string; maxResults?: number } = {}
  ): Promise<ToolResult & { matches?: Array<{ file: string; line: number; content: string }> }> {
    const { pattern = '**/*', maxResults = 100 } = options;

    try {
      const files = await fg(pattern, {
        cwd: this.basePath,
        ignore: this.permissions.deniedPaths,
        dot: false,
      });

      const matches: Array<{ file: string; line: number; content: string }> = [];
      const regex = new RegExp(query, 'gi');

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
            if (line && regex.test(line)) {
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
