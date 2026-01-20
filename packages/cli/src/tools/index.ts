/**
 * Local Tools - Built-in tool implementations for agentic workflows
 * 
 * These tools can be executed locally without requiring the backend,
 * enabling local-first operation similar to Claude Code CLI.
 */

import * as fs from 'fs';
import * as fsPromises from 'fs/promises';
import * as path from 'path';
import { spawn } from 'child_process';
import fastGlob from 'fast-glob';
import { getCheckpointManager } from '../checkpoint-manager';
import { getSandboxExecutor } from '../sandbox/index';

// Types
export interface ToolResult {
  success: boolean;
  output: string;
  error?: string;
}

export interface FileReadParams {
  path: string;
  encoding?: BufferEncoding;
}

export interface FileWriteParams {
  path: string;
  content: string;
  createDirs?: boolean;
}

export interface FileEditParams {
  path: string;
  oldText: string;
  newText: string;
}

export interface ShellExecuteParams {
  command: string;
  args?: string[];
  cwd?: string;
  timeout?: number;
  sandboxMode?: 'none' | 'spawn' | 'docker';
}

export interface GlobSearchParams {
  pattern: string;
  cwd?: string;
  ignore?: string[];
}

// Path validation to prevent traversal attacks
function validatePath(basePath: string, targetPath: string): string {
  const normalizedBase = path.resolve(basePath);
  const normalizedTarget = path.resolve(basePath, targetPath);
  
  if (!normalizedTarget.startsWith(normalizedBase)) {
    throw new Error(`Path traversal detected: ${targetPath}`);
  }
  
  return normalizedTarget;
}

/**
 * Read a file's contents
 */
export async function fileRead(params: FileReadParams): Promise<ToolResult> {
  try {
    const safePath = validatePath(process.cwd(), params.path);
    const content = await fsPromises.readFile(safePath, params.encoding || 'utf-8');
    
    return {
      success: true,
      output: content as string,
    };
  } catch (error) {
    return {
      success: false,
      output: '',
      error: `Failed to read file: ${error}`,
    };
  }
}

/**
 * Write content to a file
 */
export async function fileWrite(params: FileWriteParams): Promise<ToolResult> {
  try {
    const safePath = validatePath(process.cwd(), params.path);
    const checkpointMgr = getCheckpointManager();
    
    // Check if file exists for checkpoint
    const exists = fs.existsSync(safePath);
    const beforeContent = exists ? await fsPromises.readFile(safePath, 'utf-8') : undefined;
    
    // Create directories if needed
    if (params.createDirs) {
      await fsPromises.mkdir(path.dirname(safePath), { recursive: true });
    }
    
    // Write file
    await fsPromises.writeFile(safePath, params.content, 'utf-8');
    
    // Record operation
    if (exists && beforeContent !== undefined) {
      await checkpointMgr.recordFileEdit(safePath, beforeContent, params.content);
    } else {
      await checkpointMgr.recordFileCreate(safePath, params.content);
    }
    
    return {
      success: true,
      output: `Successfully wrote ${params.content.length} bytes to ${params.path}`,
    };
  } catch (error) {
    return {
      success: false,
      output: '',
      error: `Failed to write file: ${error}`,
    };
  }
}

/**
 * Edit a file by replacing text
 */
export async function fileEdit(params: FileEditParams): Promise<ToolResult> {
  try {
    const safePath = validatePath(process.cwd(), params.path);
    const checkpointMgr = getCheckpointManager();
    
    const beforeContent = await fsPromises.readFile(safePath, 'utf-8');
    
    if (!beforeContent.includes(params.oldText)) {
      return {
        success: false,
        output: '',
        error: `Text to replace not found in file: ${params.path}`,
      };
    }
    
    const afterContent = beforeContent.replace(params.oldText, params.newText);
    await fsPromises.writeFile(safePath, afterContent, 'utf-8');
    
    await checkpointMgr.recordFileEdit(safePath, beforeContent, afterContent);
    
    return {
      success: true,
      output: `Successfully edited ${params.path}`,
    };
  } catch (error) {
    return {
      success: false,
      output: '',
      error: `Failed to edit file: ${error}`,
    };
  }
}

/**
 * Delete a file
 */
export async function fileDelete(filePath: string): Promise<ToolResult> {
  try {
    const safePath = validatePath(process.cwd(), filePath);
    const checkpointMgr = getCheckpointManager();
    
    const beforeContent = await fsPromises.readFile(safePath, 'utf-8');
    await fsPromises.unlink(safePath);
    
    await checkpointMgr.recordFileDelete(safePath, beforeContent);
    
    return {
      success: true,
      output: `Successfully deleted ${filePath}`,
    };
  } catch (error) {
    return {
      success: false,
      output: '',
      error: `Failed to delete file: ${error}`,
    };
  }
}

/**
 * Execute a shell command safely
 */
export async function shellExecute(params: ShellExecuteParams): Promise<ToolResult> {
  const checkpointMgr = getCheckpointManager();
  
  // Get sandbox executor with configured mode
  const sandbox = getSandboxExecutor({
    mode: params.sandboxMode || 'spawn',
    timeout: params.timeout || 30000,
    workdir: params.cwd,
  });

  const args = params.args || [];
  const result = await sandbox.execute(params.command, args);

  // Record the command for checkpoint tracking
  const fullCommand = [params.command, ...args].join(' ');
  await checkpointMgr.recordBashCommand(fullCommand);

  if (result.timedOut) {
    return {
      success: false,
      output: result.stdout,
      error: `Command timed out after ${params.timeout || 30000}ms`,
    };
  }

  return {
    success: result.exitCode === 0,
    output: result.stdout || 'Command completed successfully',
    error: result.stderr || undefined,
  };
}

/**
 * Search for files using glob patterns
 */
export async function globSearch(params: GlobSearchParams): Promise<ToolResult> {
  try {
    const cwd = params.cwd || process.cwd();
    const ignore = params.ignore || ['**/node_modules/**', '**/.git/**'];
    
    const files = await fastGlob(params.pattern, {
      cwd,
      ignore,
      onlyFiles: true,
      absolute: false,
    });
    
    return {
      success: true,
      output: files.join('\n'),
    };
  } catch (error) {
    return {
      success: false,
      output: '',
      error: `Glob search failed: ${error}`,
    };
  }
}

/**
 * List directory contents
 */
export async function listDirectory(dirPath: string): Promise<ToolResult> {
  try {
    const safePath = validatePath(process.cwd(), dirPath);
    const entries = await fsPromises.readdir(safePath, { withFileTypes: true });
    
    const output = entries.map(entry => {
      const type = entry.isDirectory() ? 'd' : entry.isSymbolicLink() ? 'l' : 'f';
      return `${type} ${entry.name}`;
    }).join('\n');
    
    return {
      success: true,
      output,
    };
  } catch (error) {
    return {
      success: false,
      output: '',
      error: `Failed to list directory: ${error}`,
    };
  }
}

// Tool registry for MCP integration
export const TOOL_REGISTRY = {
  file_read: {
    name: 'file_read',
    description: 'Read the contents of a file',
    inputSchema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Path to the file to read' },
        encoding: { type: 'string', description: 'File encoding (default: utf-8)' },
      },
      required: ['path'],
    },
    execute: fileRead,
  },
  file_write: {
    name: 'file_write',
    description: 'Write content to a file',
    inputSchema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Path to the file to write' },
        content: { type: 'string', description: 'Content to write' },
        createDirs: { type: 'boolean', description: 'Create parent directories if needed' },
      },
      required: ['path', 'content'],
    },
    execute: fileWrite,
  },
  file_edit: {
    name: 'file_edit',
    description: 'Edit a file by replacing text',
    inputSchema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Path to the file to edit' },
        oldText: { type: 'string', description: 'Text to replace' },
        newText: { type: 'string', description: 'Replacement text' },
      },
      required: ['path', 'oldText', 'newText'],
    },
    execute: fileEdit,
  },
  file_delete: {
    name: 'file_delete',
    description: 'Delete a file',
    inputSchema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Path to the file to delete' },
      },
      required: ['path'],
    },
    execute: (params: { path: string }) => fileDelete(params.path),
  },
  shell_execute: {
    name: 'shell_execute',
    description: 'Execute a shell command',
    inputSchema: {
      type: 'object',
      properties: {
        command: { type: 'string', description: 'Command to execute' },
        args: { type: 'array', items: { type: 'string' }, description: 'Command arguments' },
        cwd: { type: 'string', description: 'Working directory' },
        timeout: { type: 'number', description: 'Timeout in milliseconds' },
        sandboxMode: { 
          type: 'string', 
          enum: ['none', 'spawn', 'docker'],
          description: 'Sandbox mode: none (unsafe), spawn (safe), docker (isolated)' 
        },
      },
      required: ['command'],
    },
    execute: shellExecute,
  },
  glob_search: {
    name: 'glob_search',
    description: 'Search for files using glob patterns',
    inputSchema: {
      type: 'object',
      properties: {
        pattern: { type: 'string', description: 'Glob pattern to search' },
        cwd: { type: 'string', description: 'Base directory for search' },
        ignore: { type: 'array', items: { type: 'string' }, description: 'Patterns to ignore' },
      },
      required: ['pattern'],
    },
    execute: globSearch,
  },
  list_directory: {
    name: 'list_directory',
    description: 'List contents of a directory',
    inputSchema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Path to the directory' },
      },
      required: ['path'],
    },
    execute: (params: { path: string }) => listDirectory(params.path),
  },
};

export type ToolName = keyof typeof TOOL_REGISTRY;
