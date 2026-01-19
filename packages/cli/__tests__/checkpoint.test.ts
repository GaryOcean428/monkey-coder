import { describe, it, expect, jest, beforeEach, afterEach } from '@jest/globals';
import { CheckpointManager, getCheckpointManager } from '../src/checkpoint-manager';
import * as os from 'os';
import * as path from 'path';
import * as fs from 'fs';
import * as fsPromises from 'fs/promises';

// Mock isomorphic-git
jest.mock('isomorphic-git', () => ({
  init: jest.fn(),
  findRoot: jest.fn(),
  statusMatrix: jest.fn(() => Promise.resolve([])),
  add: jest.fn(),
  remove: jest.fn(),
  commit: jest.fn(() => Promise.resolve('mock-sha-123')),
  checkout: jest.fn(),
  log: jest.fn(() => Promise.resolve([{ oid: 'current-sha' }])),
}));

describe('CheckpointManager', () => {
  let manager: CheckpointManager;
  const testDir = path.join(os.tmpdir(), '.monkey-coder-checkpoint-test');
  const checkpointsDir = path.join(os.homedir(), '.monkey-coder', 'checkpoints');

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Create test directories
    if (!fs.existsSync(testDir)) {
      fs.mkdirSync(testDir, { recursive: true });
    }
    
    manager = new CheckpointManager(testDir);
    
    // Clear operations for clean test state
    manager.clearOperations();
  });

  afterEach(async () => {
    // Cleanup test checkpoints
    try {
      if (fs.existsSync(checkpointsDir)) {
        const files = await fsPromises.readdir(checkpointsDir);
        for (const file of files) {
          if (file.endsWith('.json')) {
            await fsPromises.unlink(path.join(checkpointsDir, file));
          }
        }
      }
    } catch {
      // Ignore cleanup errors
    }
  });

  describe('createCheckpoint', () => {
    it('creates a checkpoint with message and files', async () => {
      const git = await import('isomorphic-git');
      (git.findRoot as jest.Mock<any>).mockResolvedValue(testDir);
      (git.statusMatrix as jest.Mock<any>).mockResolvedValue([
        ['test.txt', 1, 2, 2],
        ['test2.txt', 0, 1, 1],
      ]);

      const checkpoint = await manager.createCheckpoint('Test checkpoint');

      expect(checkpoint).toHaveProperty('id');
      expect(checkpoint).toHaveProperty('sha');
      expect(checkpoint.message).toBe('Test checkpoint');
      expect(checkpoint).toHaveProperty('timestamp');
      expect(checkpoint).toHaveProperty('operationCount');
      expect(checkpoint).toHaveProperty('files');
      expect(Array.isArray(checkpoint.files)).toBe(true);
    });

    it('includes changed files in checkpoint', async () => {
      const git = await import('isomorphic-git');
      (git.findRoot as jest.Mock<any>).mockResolvedValue(testDir);
      (git.statusMatrix as jest.Mock<any>).mockResolvedValue([
        ['file1.txt', 1, 2, 1],
        ['file2.txt', 0, 1, 0],
      ]);

      const checkpoint = await manager.createCheckpoint('Files test');

      expect(checkpoint.files).toHaveLength(2);
      expect(checkpoint.files).toContain('file1.txt');
      expect(checkpoint.files).toContain('file2.txt');
    });
  });

  describe('listCheckpoints', () => {
    it('returns empty array when no checkpoints exist', async () => {
      const checkpoints = await manager.listCheckpoints();
      expect(Array.isArray(checkpoints)).toBe(true);
    });

    it('returns checkpoints sorted by timestamp descending', async () => {
      const git = await import('isomorphic-git');
      (git.findRoot as jest.Mock<any>).mockResolvedValue(testDir);
      (git.statusMatrix as jest.Mock<any>).mockResolvedValue([]);

      // Create multiple checkpoints with delays to ensure different timestamps
      const cp1 = await manager.createCheckpoint('First');
      await new Promise(resolve => setTimeout(resolve, 10));
      const cp2 = await manager.createCheckpoint('Second');
      await new Promise(resolve => setTimeout(resolve, 10));
      const cp3 = await manager.createCheckpoint('Third');

      const checkpoints = await manager.listCheckpoints();

      // Should be sorted newest first
      expect(checkpoints[0]?.id).toBe(cp3.id);
      expect(checkpoints[1]?.id).toBe(cp2.id);
      expect(checkpoints[2]?.id).toBe(cp1.id);
    });
  });

  describe('getDiff', () => {
    it('returns diff for checkpoint', async () => {
      const git = await import('isomorphic-git');
      (git.findRoot as jest.Mock<any>).mockResolvedValue(testDir);
      (git.statusMatrix as jest.Mock<any>)
        .mockResolvedValueOnce([])  // For create checkpoint
        .mockResolvedValueOnce([    // For getDiff
          ['modified.txt', 1, 2],
          ['added.txt', 0, 1],
          ['deleted.txt', 1, 0],
        ]);

      const checkpoint = await manager.createCheckpoint('Before changes');
      const diff = await manager.getDiff(checkpoint.id);

      expect(typeof diff).toBe('string');
      expect(diff.length).toBeGreaterThan(0);
    });

    it('handles partial checkpoint ID', async () => {
      const git = await import('isomorphic-git');
      (git.findRoot as jest.Mock<any>).mockResolvedValue(testDir);
      (git.statusMatrix as jest.Mock<any>)
        .mockResolvedValueOnce([])
        .mockResolvedValueOnce([]);

      const checkpoint = await manager.createCheckpoint('Test');
      const partialId = checkpoint.id.slice(0, 8);
      
      const diff = await manager.getDiff(partialId);
      expect(typeof diff).toBe('string');
    });

    it('throws error for non-existent checkpoint', async () => {
      const git = await import('isomorphic-git');
      (git.findRoot as jest.Mock<any>).mockResolvedValue(testDir);

      await expect(
        manager.getDiff('nonexistent-id')
      ).rejects.toThrow('Checkpoint not found');
    });
  });

  describe('undoLastOperation', () => {
    it('returns null when no operations exist', async () => {
      const result = await manager.undoLastOperation();
      expect(result).toBeNull();
    });
  });

  describe('listOperations', () => {
    it('returns empty array when no operations exist', () => {
      const operations = manager.listOperations();
      expect(Array.isArray(operations)).toBe(true);
      expect(operations).toHaveLength(0);
    });

    it('respects limit parameter', async () => {
      // Record some operations
      for (let i = 0; i < 5; i++) {
        await manager.recordFileCreate(`file${i}.txt`, 'content');
      }

      const operations = manager.listOperations(3);
      expect(operations).toHaveLength(3);
    });
  });

  describe('restoreCheckpoint', () => {
    it('restores to checkpoint by ID', async () => {
      const git = await import('isomorphic-git');
      (git.findRoot as jest.Mock<any>).mockResolvedValue(testDir);
      (git.statusMatrix as jest.Mock<any>).mockResolvedValue([]);

      const checkpoint = await manager.createCheckpoint('Restore test');

      await manager.restoreCheckpoint(checkpoint.id);

      expect(git.checkout).toHaveBeenCalledWith(
        expect.objectContaining({
          ref: checkpoint.sha,
          force: true,
        })
      );
    });

    it('throws error for non-existent checkpoint', async () => {
      await expect(
        manager.restoreCheckpoint('nonexistent-id')
      ).rejects.toThrow('Checkpoint not found');
    });
  });
});

describe('getCheckpointManager', () => {
  it('returns singleton instance', () => {
    const manager1 = getCheckpointManager();
    const manager2 = getCheckpointManager();
    expect(manager1).toBe(manager2);
  });

  it('creates new instance for different working directory', () => {
    const manager1 = getCheckpointManager('/path1');
    const manager2 = getCheckpointManager('/path2');
    expect(manager1).not.toBe(manager2);
  });
});
