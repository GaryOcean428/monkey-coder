/**
 * Utility functions for Monkey Coder CLI
 * File operations, formatting, and helper functions
 */

import fs from 'fs-extra';
import * as path from 'path';
import chalk from 'chalk';
import { ExecuteResponse } from './types.js';

/**
 * Read file content with error handling
 */
export async function readFileContent(filePath: string): Promise<string> {
  try {
    const absolutePath = path.resolve(filePath);
    if (!(await fs.pathExists(absolutePath))) {
      throw new Error(`File not found: ${filePath}`);
    }
    return await fs.readFile(absolutePath, 'utf-8');
  } catch (error) {
    throw new Error(`Failed to read file ${filePath}: ${error}`);
  }
}

/**
 * Write content to file with directory creation
 */
export async function writeFileContent(filePath: string, content: string): Promise<void> {
  try {
    const absolutePath = path.resolve(filePath);
    await fs.ensureDir(path.dirname(absolutePath));
    await fs.writeFile(absolutePath, content, 'utf-8');
  } catch (error) {
    throw new Error(`Failed to write file ${filePath}: ${error}`);
  }
}

/**
 * Get file extension and detect programming language
 */
export function detectLanguage(filePath: string): string {
  const ext = path.extname(filePath).toLowerCase();
  const languageMap: Record<string, string> = {
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.py': 'python',
    '.java': 'java',
    '.cpp': 'cpp',
    '.c': 'c',
    '.cs': 'csharp',
    '.php': 'php',
    '.rb': 'ruby',
    '.go': 'go',
    '.rs': 'rust',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.scala': 'scala',
    '.sh': 'shell',
    '.bash': 'shell',
    '.zsh': 'shell',
    '.fish': 'shell',
    '.md': 'markdown',
    '.html': 'html',
    '.css': 'css',
    '.scss': 'scss',
    '.sass': 'sass',
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.xml': 'xml',
    '.sql': 'sql',
  };
  return languageMap[ext] || 'text';
}

/**
 * Format execution response for display
 */
export function formatResponse(response: ExecuteResponse): string {
  const lines: string[] = [];
  
  lines.push(chalk.green('✓ Task completed successfully'));
  lines.push(chalk.gray(`Execution ID: ${response.execution_id}`));
  lines.push(chalk.gray(`Status: ${response.status}`));
  
  if (response.usage) {
    lines.push('');
    lines.push(chalk.cyan('Usage Statistics:'));
    lines.push(`  Tokens used: ${response.usage.tokens_used}`);
    lines.push(`  Input tokens: ${response.usage.tokens_input}`);
    lines.push(`  Output tokens: ${response.usage.tokens_output}`);
    lines.push(`  Execution time: ${response.usage.execution_time.toFixed(2)}s`);
    lines.push(`  Estimated cost: $${response.usage.cost_estimate.toFixed(4)}`);
  }
  
  if (response.result) {
    lines.push('');
    lines.push(chalk.cyan('Result:'));
    
    if (typeof response.result.result === 'string') {
      lines.push(response.result.result);
    } else {
      lines.push(JSON.stringify(response.result.result, null, 2));
    }
    
    if (response.result.confidence_score) {
      lines.push('');
      lines.push(chalk.gray(`Confidence: ${(response.result.confidence_score * 100).toFixed(1)}%`));
    }
    
    if (response.result.artifacts && response.result.artifacts.length > 0) {
      lines.push('');
      lines.push(chalk.cyan('Generated Artifacts:'));
      response.result.artifacts.forEach((artifact, index) => {
        lines.push(`  ${index + 1}. ${artifact.name || 'Unnamed artifact'}`);
        if (artifact.type) {
          lines.push(`     Type: ${artifact.type}`);
        }
      });
    }
  }
  
  return lines.join('\n');
}

/**
 * Format error for display
 */
export function formatError(error: Error | string): string {
  const message = typeof error === 'string' ? error : error.message;
  return chalk.red(`✗ Error: ${message}`);
}

/**
 * Format progress information
 */
export function formatProgress(step: string, percentage?: number, metadata?: Record<string, any>): string {
  const parts: string[] = [];
  
  if (percentage !== undefined) {
    const progressBar = createProgressBar(percentage);
    parts.push(chalk.cyan(`${progressBar} ${percentage.toFixed(1)}%`));
  }
  
  parts.push(chalk.yellow(step));
  
  if (metadata) {
    const metaInfo = Object.entries(metadata)
      .map(([key, value]) => `${key}: ${value}`)
      .join(', ');
    if (metaInfo) {
      parts.push(chalk.gray(`(${metaInfo})`));
    }
  }
  
  return parts.join(' ');
}

/**
 * Create a simple progress bar
 */
export function createProgressBar(percentage: number, width: number = 20): string {
  const filled = Math.floor((percentage / 100) * width);
  const empty = width - filled;
  return '[' + '█'.repeat(filled) + '░'.repeat(empty) + ']';
}

/**
 * Generate UUID v4
 */
export function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * Validate file path and ensure it's accessible
 */
export async function validateFilePath(filePath: string): Promise<void> {
  const absolutePath = path.resolve(filePath);
  
  try {
    const stats = await fs.stat(absolutePath);
    if (!stats.isFile()) {
      throw new Error(`Path is not a file: ${filePath}`);
    }
  } catch (error: any) {
    if (error.code === 'ENOENT') {
      throw new Error(`File not found: ${filePath}`);
    }
    throw new Error(`Cannot access file ${filePath}: ${error.message}`);
  }
}

/**
 * Truncate text to specified length
 */
export function truncateText(text: string, maxLength: number = 100): string {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength - 3) + '...';
}

/**
 * Format file size in human readable format
 */
export function formatFileSize(bytes: number): string {
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unit = 0;
  
  while (size >= 1024 && unit < units.length - 1) {
    size /= 1024;
    unit++;
  }
  
  return `${size.toFixed(1)} ${units[unit]}`;
}

/**
 * Sleep for specified milliseconds
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Check if string is valid JSON
 */
export function isValidJSON(str: string): boolean {
  try {
    JSON.parse(str);
    return true;
  } catch {
    return false;
  }
}

/**
 * Parse command line arguments for file paths
 */
export function parseFileArguments(args: string[]): string[] {
  return args.filter(arg => {
    // Filter out options (starting with -)
    return !arg.startsWith('-');
  });
}
