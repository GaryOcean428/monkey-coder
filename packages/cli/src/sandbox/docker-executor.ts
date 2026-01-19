/**
 * Docker-based Sandboxed Execution
 * 
 * Provides secure, isolated execution of untrusted code using Docker containers
 * with resource limits, network isolation, and security controls.
 */

import Docker from 'dockerode';

export interface SandboxConfig {
  image: string;
  memory: number;        // bytes
  cpuPeriod: number;
  cpuQuota: number;
  timeout: number;       // ms
  networkMode: 'none' | 'bridge';
  workdir: string;
  readOnly: boolean;
}

export interface SandboxResult {
  exitCode: number;
  stdout: string;
  stderr: string;
  timedOut: boolean;
  oomKilled: boolean;
}

const DEFAULT_CONFIG: SandboxConfig = {
  image: 'node:20-alpine',
  memory: 128 * 1024 * 1024,  // 128MB
  cpuPeriod: 100000,
  cpuQuota: 50000,            // 50% CPU
  timeout: 30000,             // 30s
  networkMode: 'none',
  workdir: '/workspace',
  readOnly: false,
};

/**
 * DockerSandbox class for isolated command execution
 */
export class DockerSandbox {
  private docker: Docker;
  private config: SandboxConfig;

  constructor(config: Partial<SandboxConfig> = {}) {
    this.docker = new Docker();
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Check if Docker is available
   */
  async isAvailable(): Promise<boolean> {
    try {
      await this.docker.ping();
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Execute command in sandboxed container
   */
  async execute(
    command: string[],
    options: {
      workdir?: string;
      env?: Record<string, string>;
      stdin?: string;
      binds?: string[];  // Host:Container mount paths
    } = {}
  ): Promise<SandboxResult> {
    const container = await this.docker.createContainer({
      Image: this.config.image,
      Cmd: command,
      WorkingDir: options.workdir || this.config.workdir,
      Env: Object.entries(options.env || {}).map(([k, v]) => `${k}=${v}`),
      HostConfig: {
        AutoRemove: true,
        Memory: this.config.memory,
        MemorySwap: this.config.memory,  // No swap
        CpuPeriod: this.config.cpuPeriod,
        CpuQuota: this.config.cpuQuota,
        NetworkMode: this.config.networkMode,
        CapDrop: ['ALL'],
        SecurityOpt: ['no-new-privileges'],
        PidsLimit: 50,
        ReadonlyRootfs: this.config.readOnly,
        Binds: options.binds,
      },
      AttachStdout: true,
      AttachStderr: true,
      AttachStdin: !!options.stdin,
      OpenStdin: !!options.stdin,
      Tty: false,
    });

    let stdout = '';
    let stderr = '';
    let timedOut = false;
    let oomKilled = false;

    try {
      // Set up timeout
      const timeoutId = setTimeout(async () => {
        timedOut = true;
        try {
          await container.stop();
        } catch {
          // Container may already be stopped
        }
      }, this.config.timeout);

      // Attach to streams
      const stream = await container.attach({
        stream: true,
        stdout: true,
        stderr: true,
        stdin: !!options.stdin,
      });

      // Demux stdout/stderr
      container.modem.demuxStream(
        stream,
        {
          write: (chunk: Buffer) => { stdout += chunk.toString(); },
          end: () => {},
        },
        {
          write: (chunk: Buffer) => { stderr += chunk.toString(); },
          end: () => {},
        }
      );

      // Write stdin if provided
      if (options.stdin) {
        stream.write(options.stdin);
        stream.end();
      }

      // Start container
      await container.start();

      // Wait for completion
      const { StatusCode } = await container.wait();
      clearTimeout(timeoutId);

      // Check for OOM
      const inspect = await container.inspect().catch(() => null);
      oomKilled = inspect?.State?.OOMKilled || false;

      return {
        exitCode: StatusCode,
        stdout,
        stderr,
        timedOut,
        oomKilled,
      };
    } catch (error: any) {
      return {
        exitCode: -1,
        stdout,
        stderr: stderr || error.message,
        timedOut,
        oomKilled,
      };
    }
  }

  /**
   * Execute code in language-specific container
   */
  async executeCode(
    code: string,
    language: 'python' | 'node' | 'bash',
    options: { binds?: string[] } = {}
  ): Promise<SandboxResult> {
    const configs: Record<string, { image: string; cmd: string[] }> = {
      python: { image: 'python:3.13-alpine', cmd: ['python', '-c', code] },
      node: { image: 'node:20-alpine', cmd: ['node', '-e', code] },
      bash: { image: 'alpine:latest', cmd: ['sh', '-c', code] },
    };

    const config = configs[language];
    if (!config) {
      throw new Error(`Unsupported language: ${language}`);
    }

    // Temporarily switch image
    const originalImage = this.config.image;
    this.config.image = config.image;

    try {
      return await this.execute(config.cmd, options);
    } finally {
      this.config.image = originalImage;
    }
  }
}

// Singleton with fallback to spawn
let sandbox: DockerSandbox | null = null;
let dockerAvailable: boolean | null = null;

/**
 * Get singleton DockerSandbox instance, or null if Docker unavailable
 */
export async function getSandbox(): Promise<DockerSandbox | null> {
  if (dockerAvailable === null) {
    sandbox = new DockerSandbox();
    dockerAvailable = await sandbox.isAvailable();
  }
  return dockerAvailable ? sandbox : null;
}
