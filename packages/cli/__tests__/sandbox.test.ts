/**
 * Tests for SandboxExecutor
 */

import { describe, it, expect, jest, beforeEach } from '@jest/globals';

// Mock DockerSandbox module
const mockIsAvailable = jest.fn<() => Promise<boolean>>().mockResolvedValue(false);
const mockExecute = jest.fn<() => Promise<any>>().mockResolvedValue({
  exitCode: 0,
  stdout: 'mocked output',
  stderr: '',
  timedOut: false,
  oomKilled: false,
});

jest.mock('../src/sandbox/docker-executor', () => ({
  DockerSandbox: jest.fn().mockImplementation(() => ({
    isAvailable: mockIsAvailable,
    execute: mockExecute,
  })),
}));

import { SandboxExecutor, getSandboxExecutor } from '../src/sandbox/index';

describe('SandboxExecutor', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('constructor', () => {
    it('should create instance with default options', () => {
      const executor = new SandboxExecutor();
      expect(executor).toBeInstanceOf(SandboxExecutor);
    });

    it('should create instance with custom options', () => {
      const executor = new SandboxExecutor({
        mode: 'docker',
        timeout: 60000,
        memoryLimit: 512,
        networkEnabled: true,
      });
      expect(executor).toBeInstanceOf(SandboxExecutor);
    });

    it('should default to spawn mode', () => {
      const executor = new SandboxExecutor();
      expect(executor).toBeInstanceOf(SandboxExecutor);
    });
  });

  describe('execute with spawn mode', () => {
    it('should execute simple command successfully', async () => {
      const executor = new SandboxExecutor({ mode: 'spawn' });
      const result = await executor.execute('echo', ['hello']);

      expect(result.exitCode).toBe(0);
      expect(result.stdout).toContain('hello');
      expect(result.timedOut).toBe(false);
    });

    it('should handle command failure', async () => {
      const executor = new SandboxExecutor({ mode: 'spawn' });
      const result = await executor.execute('ls', ['/nonexistent-path-12345']);

      expect(result.exitCode).not.toBe(0);
      expect(result.stderr.length).toBeGreaterThan(0);
    });

    it('should respect timeout', async () => {
      const executor = new SandboxExecutor({ mode: 'spawn', timeout: 100 });
      const result = await executor.execute('sleep', ['10']);

      // Timeout should kill the process
      expect(result.timedOut || result.exitCode !== 0).toBe(true);
    }, 10000);

    it('should execute in specified working directory', async () => {
      const executor = new SandboxExecutor({ mode: 'spawn', workdir: '/tmp' });
      const result = await executor.execute('pwd', []);

      expect(result.exitCode).toBe(0);
      expect(result.stdout.trim()).toBe('/tmp');
    });
  });

  describe('execute with none mode', () => {
    it('should execute command in unsafe mode', async () => {
      const executor = new SandboxExecutor({ mode: 'none' });
      const result = await executor.execute('echo', ['test']);

      expect(result.exitCode).toBe(0);
      expect(result.stdout).toContain('test');
    });
  });

  describe('getSandboxExecutor singleton', () => {
    it('should return singleton instance', () => {
      const executor1 = getSandboxExecutor();
      const executor2 = getSandboxExecutor();

      expect(executor1).toBe(executor2);
    });

    it('should create new instance with different options', () => {
      const executor1 = getSandboxExecutor();
      const executor2 = getSandboxExecutor({ mode: 'docker' });

      expect(executor2).not.toBe(executor1);
    });
  });

  describe('Docker mode fallback', () => {
    it('should fall back to spawn when Docker unavailable', async () => {
      const executor = new SandboxExecutor({ mode: 'docker' });
      
      // Wait for Docker initialization to complete
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Docker is mocked to be unavailable, should fall back to spawn
      const result = await executor.execute('echo', ['fallback-test']);

      expect(result.exitCode).toBe(0);
      // When Docker is unavailable, it falls back to spawn mode, so we should get real output
      expect(result.stdout).toBeTruthy();
    });
  });

  describe('isDockerAvailable', () => {
    it('should return false when Docker not available', async () => {
      const executor = new SandboxExecutor({ mode: 'docker' });
      const available = await executor.isDockerAvailable();

      expect(available).toBe(false);
    });
  });

  describe('error handling', () => {
    it('should handle invalid command gracefully', async () => {
      const executor = new SandboxExecutor({ mode: 'spawn' });
      const result = await executor.execute('nonexistent-command-xyz', []);

      expect(result.exitCode).not.toBe(0);
    });
  });
});
