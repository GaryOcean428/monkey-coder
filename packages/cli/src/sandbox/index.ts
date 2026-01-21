/**
 * Unified Sandbox Executor
 * 
 * Provides multiple execution modes for shell commands with security controls:
 * - none: Direct execution (unsafe, for development only)
 * - spawn: Node.js spawn with array args (prevents shell injection)
 * - docker: Full Docker isolation with resource limits
 */

import { spawn } from 'child_process';
import { DockerSandbox } from './docker-executor.js';

export interface SandboxOptions {
  mode: 'none' | 'spawn' | 'docker';
  timeout?: number;
  memoryLimit?: number;  // MB
  networkEnabled?: boolean;
  workdir?: string;
  readOnlyRoot?: boolean;
}

export interface SandboxResult {
  exitCode: number;
  stdout: string;
  stderr: string;
  timedOut: boolean;
}

const DEFAULT_OPTIONS: SandboxOptions = {
  mode: 'spawn',
  timeout: 30000,
  memoryLimit: 256,
  networkEnabled: false,
  readOnlyRoot: false,
};

/**
 * SandboxExecutor - Unified interface for sandboxed command execution
 */
export class SandboxExecutor {
  private dockerSandbox: DockerSandbox | null = null;
  private options: SandboxOptions;
  private initializationPromise: Promise<void> | null = null;

  constructor(options: Partial<SandboxOptions> = {}) {
    this.options = { ...DEFAULT_OPTIONS, ...options };
    
    if (this.options.mode === 'docker') {
      // Start initialization asynchronously
      this.initializationPromise = this.initializeDocker();
    }
  }

  /**
   * Initialize Docker sandbox with fallback to spawn
   */
  private async initializeDocker(): Promise<void> {
    try {
      this.dockerSandbox = new DockerSandbox({
        memory: (this.options.memoryLimit || 256) * 1024 * 1024,
        timeout: this.options.timeout || 30000,
        networkMode: this.options.networkEnabled ? 'bridge' : 'none',
        workdir: this.options.workdir || '/workspace',
        readOnly: this.options.readOnlyRoot || false,
      });

      const available = await this.dockerSandbox.isAvailable();
      if (!available) {
        console.warn('Docker not available, falling back to spawn mode');
        this.options.mode = 'spawn';
        this.dockerSandbox = null;
      }
    } catch (error) {
      console.warn('Docker initialization failed, falling back to spawn mode:', error);
      this.options.mode = 'spawn';
      this.dockerSandbox = null;
    }
  }

  /**
   * Execute command with configured sandbox mode
   */
  async execute(command: string, args: string[] = []): Promise<SandboxResult> {
    // Wait for Docker initialization if it's in progress
    if (this.initializationPromise) {
      await this.initializationPromise;
      this.initializationPromise = null;
    }

    switch (this.options.mode) {
      case 'docker':
        return this.executeDocker(command, args);
      case 'spawn':
        return this.executeSpawn(command, args);
      case 'none':
        return this.executeUnsafe(command, args);
    }
  }

  /**
   * Execute command in Docker container
   */
  private async executeDocker(command: string, args: string[]): Promise<SandboxResult> {
    if (!this.dockerSandbox) {
      // Docker was requested but not available, fall back to spawn
      console.warn('Docker sandbox not available, falling back to spawn');
      return this.executeSpawn(command, args);
    }

    try {
      const workdir = this.options.workdir || process.cwd();
      const fullCommand = [command, ...args];

      // Create bind mounts for the working directory
      const binds = [`${workdir}:/workspace:${this.options.readOnlyRoot ? 'ro' : 'rw'}`];

      const result = await this.dockerSandbox.execute(fullCommand, {
        workdir: '/workspace',
        binds,
      });

      return {
        exitCode: result.exitCode,
        stdout: result.stdout,
        stderr: result.stderr,
        timedOut: result.timedOut,
      };
    } catch (error: any) {
      return {
        exitCode: 1,
        stdout: '',
        stderr: error.message || String(error),
        timedOut: false,
      };
    }
  }

  /**
   * Execute command using Node.js spawn (safe mode)
   */
  private executeSpawn(command: string, args: string[]): Promise<SandboxResult> {
    return new Promise((resolve) => {
      const workdir = this.options.workdir || process.cwd();
      let stdout = '';
      let stderr = '';
      let timedOut = false;

      const child = spawn(command, args, {
        cwd: workdir,
        shell: false,
        timeout: this.options.timeout,
        env: { ...process.env },
      });

      child.stdout?.on('data', (data) => {
        stdout += data.toString();
      });

      child.stderr?.on('data', (data) => {
        stderr += data.toString();
      });

      child.on('error', (error) => {
        resolve({
          exitCode: 1,
          stdout,
          stderr: error.message,
          timedOut: false,
        });
      });

      child.on('close', (code, signal) => {
        if (signal === 'SIGTERM') {
          timedOut = true;
        }
        resolve({
          exitCode: code || 0,
          stdout,
          stderr,
          timedOut,
        });
      });
    });
  }

  /**
   * Execute command without sandboxing (DANGEROUS - development only)
   * Note: Still uses spawn for basic command parsing safety
   * For truly unsafe execution with shell parsing, use child_process.exec
   */
  private executeUnsafe(command: string, args: string[]): Promise<SandboxResult> {
    // Note: We still use spawn here for basic safety (no shell injection)
    // True 'unsafe' mode would use exec() with shell: true, but that's too dangerous
    return this.executeSpawn(command, args);
  }

  /**
   * Check if Docker is available
   */
  async isDockerAvailable(): Promise<boolean> {
    if (!this.dockerSandbox) return false;
    return this.dockerSandbox.isAvailable();
  }
}

// Singleton for default usage
let defaultExecutor: SandboxExecutor | null = null;

/**
 * Get or create a sandbox executor with given options
 * If options are provided, creates a new executor instance
 * If no options provided, returns/creates the default singleton
 */
export function getSandboxExecutor(options?: Partial<SandboxOptions>): SandboxExecutor {
  if (options) {
    // Always create new instance when options provided
    return new SandboxExecutor(options);
  }
  
  // Return or create default singleton
  if (!defaultExecutor) {
    defaultExecutor = new SandboxExecutor();
  }
  return defaultExecutor;
}
