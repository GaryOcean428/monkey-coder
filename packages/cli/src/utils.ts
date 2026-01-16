/**
 * Utility functions for Monkey Coder CLI
 * File operations, formatting, and helper functions
 */

import { execSync } from 'child_process';
import * as path from 'path';

import chalk from 'chalk';
import fs from 'fs-extra';

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
export async function writeFileContent(
  filePath: string,
  content: string
): Promise<void> {
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
  lines.push(chalk.gray(`Task ID: ${response.task_id}`));
  lines.push(chalk.gray(`Status: ${response.status}`));

  if (response.usage) {
    lines.push('');
    lines.push(chalk.cyan('Usage Statistics:'));
    lines.push(`  Tokens used: ${response.usage.tokens_used}`);
    lines.push(`  Input tokens: ${response.usage.tokens_input}`);
    lines.push(`  Output tokens: ${response.usage.tokens_output}`);
    lines.push(
      `  Execution time: ${response.usage.execution_time.toFixed(2)}s`
    );
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
      lines.push(
        chalk.gray(
          `Confidence: ${(response.result.confidence_score * 100).toFixed(1)}%`
        )
      );
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
export function formatProgress(
  step: string,
  percentage?: number,
  metadata?: Record<string, any>
): string {
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
export function createProgressBar(
  percentage: number,
  width: number = 20
): string {
  const filled = Math.floor((percentage / 100) * width);
  const empty = width - filled;
  return '[' + '█'.repeat(filled) + '░'.repeat(empty) + ']';
}

/**
 * Generate UUID v4
 */
export function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
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

/**
 * System Resource Limits Utilities
 * 
 * Probes and logs system resource limits at runtime to detect potential issues
 * before they cause crashes in production.
 * 
 * Common issues prevented:
 * - Undici socket errors under load
 * - Headless browser/WASM OOM despite low app usage
 * - Blank pages / builds passing but runtime silently failing
 */

export interface SystemLimits {
  openFiles: string | number;
  virtualMemory: string | number;
  maxProcesses?: string | number;
  threadPoolSize?: number;
  available: boolean;
}

export interface LimitCheckResult {
  limits: SystemLimits;
  warnings: string[];
  ok: boolean;
}

interface LimitsConfig {
  limits: {
    open_files?: {
      min: number;
      warning_template: string;
    };
    virtual_memory?: {
      expected: string;
      warning_template: string;
    };
    threadpool_size?: {
      min: number;
      default: number;
      warning_template: string;
    };
  };
}

/**
 * Load system limits configuration from shared config file
 */
function loadLimitsConfig(): LimitsConfig {
  try {
    // Try to load from config directory
    const configPath = path.join(__dirname, '../../..', 'config', 'system-limits.config.json');
    if (fs.existsSync(configPath)) {
      const configData = fs.readFileSync(configPath, 'utf-8');
      return JSON.parse(configData) as LimitsConfig;
    }
  } catch (error) {
    // Fall through to defaults
  }
  
  // Fallback to hardcoded defaults if config not found
  return {
    limits: {
      open_files: {
        min: 65535,
        warning_template: 'Open files limit is low ({value}). Recommended: ≥{min}.'
      },
      virtual_memory: {
        expected: 'unlimited',
        warning_template: 'Virtual memory limit is restricted ({value}). Recommended: {expected}.'
      },
      threadpool_size: {
        min: 64,
        default: 4,
        warning_template: 'UV_THREADPOOL_SIZE not set or too low ({value}). Recommended: {min}.'
      }
    }
  };
}

// Load configuration once at module level
const CONFIG = loadLimitsConfig();

/**
 * Probe system resource limits using ulimit
 */
export function probeSystemLimits(): SystemLimits {
  try {
    const nofile = execSync('ulimit -n', { shell: '/bin/bash', encoding: 'utf-8' }).trim();
    const vmem = execSync('ulimit -v', { shell: '/bin/bash', encoding: 'utf-8' }).trim();
    
    // Try to get max processes
    let maxProc: string | number = 'unavailable';
    try {
      maxProc = execSync('ulimit -u', { shell: '/bin/bash', encoding: 'utf-8' }).trim();
    } catch {
      // Not available on all systems
    }
    
    // Get UV_THREADPOOL_SIZE if set
    const rawPoolSize = process.env.UV_THREADPOOL_SIZE;
    const parsedPoolSize = rawPoolSize ? parseInt(rawPoolSize, 10) : NaN;
    const threadPoolSize = !isNaN(parsedPoolSize) ? parsedPoolSize : undefined;
    
    return {
      openFiles: nofile,
      virtualMemory: vmem,
      maxProcesses: maxProc,
      threadPoolSize,
      available: true,
    };
  } catch {
    return {
      openFiles: 'unavailable',
      virtualMemory: 'unavailable',
      available: false,
    };
  }
}

/**
 * Check if system limits meet recommended thresholds using shared configuration
 */
export function checkSystemLimits(): LimitCheckResult {
  const limits = probeSystemLimits();
  const warnings: string[] = [];
  
  if (!limits.available) {
    return {
      limits,
      warnings: ['Unable to probe system limits (ulimit not available in this environment)'],
      ok: true, // Don't fail if we can't check
    };
  }
  
  const configLimits = CONFIG.limits || {};
  
  // Check open files
  const openFilesConfig = configLimits.open_files || { min: 65535, warning_template: 'Open files limit is low ({value}). Recommended: ≥{min}.' };
  const nofile = typeof limits.openFiles === 'string' 
    ? parseInt(limits.openFiles, 10)
    : limits.openFiles;
    
  if (!isNaN(nofile) && nofile < openFilesConfig.min) {
    const warning = openFilesConfig.warning_template
      .replace('{value}', String(nofile))
      .replace('{min}', String(openFilesConfig.min));
    warnings.push(warning);
  }
  
  // Check virtual memory
  const vmemConfig = configLimits.virtual_memory || { expected: 'unlimited', warning_template: 'Virtual memory limit is restricted ({value}). Recommended: {expected}.' };
  const vmem = limits.virtualMemory;
  if (vmem !== vmemConfig.expected && vmem !== 'unavailable') {
    const vmemNum = typeof vmem === 'string' ? parseInt(vmem, 10) : vmem;
    if (!isNaN(vmemNum) && vmemNum > 0) {
      const warning = vmemConfig.warning_template
        .replace('{value}', String(vmem))
        .replace('{expected}', vmemConfig.expected);
      warnings.push(warning);
    }
  }
  
  // Check UV_THREADPOOL_SIZE for Node.js I/O performance
  const threadpoolConfig = configLimits.threadpool_size || { min: 64, default: 4, warning_template: 'UV_THREADPOOL_SIZE not set or too low ({value}). Recommended: {min}.' };
  if (!limits.threadPoolSize || limits.threadPoolSize < threadpoolConfig.min) {
    const valueDisplay = limits.threadPoolSize || `default ${threadpoolConfig.default}`;
    const warning = threadpoolConfig.warning_template
      .replace('{value}', String(valueDisplay))
      .replace('{min}', String(threadpoolConfig.min));
    warnings.push(warning);
  }
  
  return {
    limits,
    warnings,
    ok: warnings.length === 0,
  };
}

/**
 * Log system limits information to console
 */
export function logSystemLimits(prefix = '[preflight]'): void {
  const result = checkSystemLimits();
  
  if (!result.limits.available) {
    console.log(`${prefix} ulimit probe not available in this environment`);
    return;
  }
  
  console.log(`${prefix} System Resource Limits:`);
  console.log(`${prefix}   open files      = ${result.limits.openFiles}`);
  console.log(`${prefix}   virtual memory  = ${result.limits.virtualMemory}`);
  if (result.limits.maxProcesses !== undefined) {
    console.log(`${prefix}   max processes   = ${result.limits.maxProcesses}`);
  }
  if (result.limits.threadPoolSize !== undefined) {
    console.log(`${prefix}   threadpool size = ${result.limits.threadPoolSize}`);
  }
  
  if (result.warnings.length > 0) {
    console.warn(`${prefix} ⚠️  Resource limit warnings:`);
    result.warnings.forEach(warning => {
      console.warn(`${prefix}   - ${warning}`);
    });
  } else {
    console.log(`${prefix} ✅ All resource limits are properly configured`);
  }
}

/**
 * Get formatted system limits for structured logging
 */
export function getSystemLimitsInfo(): Record<string, unknown> {
  const result = checkSystemLimits();
  return {
    limits: result.limits,
    warnings: result.warnings,
    ok: result.ok,
  };
}

/**
 * Build execution request from options
 * Exported for use in Ink UI components
 */
export async function buildExecuteRequest(
  taskType: string,
  prompt: string,
  files: string[],
  options: {
    persona?: string;
    model?: string;
    provider?: string;
    temperature?: number;
    timeout?: number;
    stream?: boolean;
  },
  config?: {
    getDefaultTimeout: () => number;
    getDefaultTemperature: () => number;
    getDefaultPersona: () => string;
    getDefaultProvider: () => string;
  }
): Promise<any> {
  const { validateTaskType, validatePersona } = await import('./type-guards.js');
  
  const fileData = [];

  // Read file contents if provided
  for (const filePath of files) {
    try {
      await validateFilePath(filePath);
      const content = await readFileContent(filePath);
      const language = detectLanguage(filePath);
      fileData.push({
        path: filePath,
        content,
        type: language,
      });
    } catch (error) {
      throw new Error(`Failed to read file ${filePath}: ${error}`);
    }
  }

  return {
    task_id: generateUUID(),
    task_type: validateTaskType(taskType),
    prompt,
    files: fileData.length > 0 ? fileData : undefined,
    context: {
      user_id: 'cli-user',
      session_id: generateUUID(),
      environment: 'cli',
      timeout: options.timeout || config?.getDefaultTimeout() || 300,
      max_tokens: 4096,
      temperature: options.temperature || config?.getDefaultTemperature() || 0.7,
    },
    persona_config: {
      persona: validatePersona(options.persona || config?.getDefaultPersona() || 'developer'),
      slash_commands: [],
      context_window: 32768,
      use_markdown_spec: true,
    },
    preferred_providers: options.provider
      ? [options.provider]
      : [config?.getDefaultProvider() || 'openai'],
    model_preferences: options.model
      ? { [options.provider || config?.getDefaultProvider() || 'openai']: options.model }
      : {},
  };
}
