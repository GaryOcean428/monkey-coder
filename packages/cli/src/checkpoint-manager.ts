/**
 * Checkpoint Manager - Git-based checkpoints with operation journaling
 * 
 * Provides undo/restore capabilities for file operations using Git commits
 * as snapshots and operation journaling for fine-grained rollback.
 */

import * as git from 'isomorphic-git';
import * as fs from 'fs';
import * as fsPromises from 'fs/promises';
import * as path from 'path';
import * as os from 'os';
import { randomUUID } from 'crypto';

// Types
export interface CheckpointEntry {
  id: string;
  sha: string;
  message: string;
  timestamp: number;
  files: string[];
}

export interface OperationEntry {
  id: string;
  checkpointId: string;
  type: 'file_create' | 'file_edit' | 'file_delete' | 'file_rename';
  filePath: string;
  beforeContent?: string;
  afterContent?: string;
  oldPath?: string; // For renames
  timestamp: number;
  status: 'active' | 'undone';
}

export interface CheckpointState {
  checkpoints: CheckpointEntry[];
  operations: OperationEntry[];
  currentCheckpointId: string | null;
}

// Configuration
const CONFIG_DIR = path.join(os.homedir(), '.monkey-coder');
const CHECKPOINTS_DIR = path.join(CONFIG_DIR, 'checkpoints');
const STATE_FILE = path.join(CHECKPOINTS_DIR, 'state.json');
const MAX_CHECKPOINTS = 50;
const MAX_AGE_DAYS = 30;

/**
 * Ensure checkpoint directory exists
 */
async function ensureCheckpointsDir(): Promise<void> {
  await fsPromises.mkdir(CHECKPOINTS_DIR, { recursive: true });
}

/**
 * Load checkpoint state
 */
async function loadState(): Promise<CheckpointState> {
  try {
    await ensureCheckpointsDir();
    const data = await fsPromises.readFile(STATE_FILE, 'utf-8');
    return JSON.parse(data);
  } catch {
    return {
      checkpoints: [],
      operations: [],
      currentCheckpointId: null,
    };
  }
}

/**
 * Save checkpoint state
 */
async function saveState(state: CheckpointState): Promise<void> {
  await ensureCheckpointsDir();
  await fsPromises.writeFile(STATE_FILE, JSON.stringify(state, null, 2));
}

/**
 * Checkpoint Manager class
 */
export class CheckpointManager {
  private workingDir: string;
  private state: CheckpointState | null = null;

  constructor(workingDir: string = process.cwd()) {
    this.workingDir = workingDir;
  }

  /**
   * Initialize and load state
   */
  async initialize(): Promise<void> {
    this.state = await loadState();
    
    // Initialize git repo if not exists
    const gitDir = path.join(this.workingDir, '.git');
    if (!fs.existsSync(gitDir)) {
      await git.init({ fs, dir: this.workingDir });
    }
  }

  /**
   * Get current state
   */
  private getState(): CheckpointState {
    if (!this.state) {
      throw new Error('CheckpointManager not initialized. Call initialize() first.');
    }
    return this.state;
  }

  /**
   * Create a checkpoint before making changes
   */
  async createCheckpoint(message: string): Promise<CheckpointEntry> {
    const state = this.getState();
    const id = randomUUID();
    const timestamp = Date.now();

    // Get list of modified files
    const statusMatrix = await git.statusMatrix({ fs, dir: this.workingDir });
    const modifiedFiles: string[] = [];

    for (const [filepath, headStatus, workdirStatus, stageStatus] of statusMatrix) {
      // Stage modified files
      if (workdirStatus !== stageStatus || headStatus !== workdirStatus) {
        try {
          await git.add({ fs, dir: this.workingDir, filepath });
          modifiedFiles.push(filepath);
        } catch {
          // Skip files that can't be added (e.g., gitignored)
        }
      }
    }

    // Create commit
    let sha = '';
    try {
      sha = await git.commit({
        fs,
        dir: this.workingDir,
        message: `[checkpoint] ${message}`,
        author: {
          name: 'Monkey Coder',
          email: 'checkpoint@monkey-coder.local',
        },
      });
    } catch (error: any) {
      // If nothing to commit, get current HEAD
      if (error.message?.includes('nothing to commit')) {
        const head = await git.resolveRef({ fs, dir: this.workingDir, ref: 'HEAD' });
        sha = head;
      } else {
        throw error;
      }
    }

    const checkpoint: CheckpointEntry = {
      id,
      sha,
      message,
      timestamp,
      files: modifiedFiles,
    };

    state.checkpoints.push(checkpoint);
    state.currentCheckpointId = id;

    // Cleanup old checkpoints
    await this.cleanupOldCheckpoints();
    await saveState(state);

    return checkpoint;
  }

  /**
   * Record a file operation for fine-grained undo
   */
  async recordOperation(
    type: OperationEntry['type'],
    filePath: string,
    options: {
      beforeContent?: string;
      afterContent?: string;
      oldPath?: string;
    } = {}
  ): Promise<OperationEntry> {
    const state = this.getState();

    const operation: OperationEntry = {
      id: randomUUID(),
      checkpointId: state.currentCheckpointId || '',
      type,
      filePath,
      beforeContent: options.beforeContent,
      afterContent: options.afterContent,
      oldPath: options.oldPath,
      timestamp: Date.now(),
      status: 'active',
    };

    state.operations.push(operation);
    await saveState(state);

    return operation;
  }

  /**
   * Undo the last operation
   */
  async undoLastOperation(): Promise<OperationEntry | null> {
    const state = this.getState();

    // Find last active operation
    const lastOp = [...state.operations]
      .reverse()
      .find(op => op.status === 'active');

    if (!lastOp) {
      return null;
    }

    const fullPath = path.join(this.workingDir, lastOp.filePath);

    switch (lastOp.type) {
      case 'file_create':
        // Delete the created file
        if (fs.existsSync(fullPath)) {
          await fsPromises.unlink(fullPath);
        }
        break;

      case 'file_edit':
        // Restore previous content
        if (lastOp.beforeContent !== undefined) {
          await fsPromises.writeFile(fullPath, lastOp.beforeContent, 'utf-8');
        }
        break;

      case 'file_delete':
        // Recreate the deleted file
        if (lastOp.beforeContent !== undefined) {
          await fsPromises.mkdir(path.dirname(fullPath), { recursive: true });
          await fsPromises.writeFile(fullPath, lastOp.beforeContent, 'utf-8');
        }
        break;

      case 'file_rename':
        // Rename back
        if (lastOp.oldPath) {
          const oldFullPath = path.join(this.workingDir, lastOp.oldPath);
          if (fs.existsSync(fullPath)) {
            await fsPromises.rename(fullPath, oldFullPath);
          }
        }
        break;
    }

    lastOp.status = 'undone';
    await saveState(state);

    return lastOp;
  }

  /**
   * Restore to a specific checkpoint
   */
  async restoreCheckpoint(checkpointId: string): Promise<boolean> {
    const state = this.getState();

    const checkpoint = state.checkpoints.find(cp => cp.id === checkpointId);
    if (!checkpoint) {
      throw new Error(`Checkpoint not found: ${checkpointId}`);
    }

    // Checkout the commit
    await git.checkout({
      fs,
      dir: this.workingDir,
      ref: checkpoint.sha,
      force: true,
    });

    // Mark all operations after this checkpoint as undone
    for (const op of state.operations) {
      if (op.timestamp > checkpoint.timestamp) {
        op.status = 'undone';
      }
    }

    state.currentCheckpointId = checkpointId;
    await saveState(state);

    return true;
  }

  /**
   * List all checkpoints
   */
  listCheckpoints(): CheckpointEntry[] {
    return this.getState().checkpoints;
  }

  /**
   * List operations for current checkpoint
   */
  listOperations(checkpointId?: string): OperationEntry[] {
    const state = this.getState();
    const targetId = checkpointId || state.currentCheckpointId;

    if (!targetId) {
      return state.operations.filter(op => op.status === 'active');
    }

    return state.operations.filter(
      op => op.checkpointId === targetId && op.status === 'active'
    );
  }

  /**
   * Get the current checkpoint
   */
  getCurrentCheckpoint(): CheckpointEntry | null {
    const state = this.getState();
    if (!state.currentCheckpointId) return null;
    return state.checkpoints.find(cp => cp.id === state.currentCheckpointId) || null;
  }

  /**
   * Clean up old checkpoints based on retention policy
   */
  private async cleanupOldCheckpoints(): Promise<number> {
    const state = this.getState();
    const now = Date.now();
    const cutoff = now - MAX_AGE_DAYS * 24 * 60 * 60 * 1000;
    let removed = 0;

    // Remove checkpoints older than cutoff
    state.checkpoints = state.checkpoints.filter(cp => {
      if (cp.timestamp < cutoff) {
        removed++;
        return false;
      }
      return true;
    });

    // Keep only MAX_CHECKPOINTS most recent
    if (state.checkpoints.length > MAX_CHECKPOINTS) {
      const excess = state.checkpoints.length - MAX_CHECKPOINTS;
      state.checkpoints = state.checkpoints.slice(excess);
      removed += excess;
    }

    // Clean up orphaned operations
    const validCheckpointIds = new Set(state.checkpoints.map(cp => cp.id));
    state.operations = state.operations.filter(
      op => !op.checkpointId || validCheckpointIds.has(op.checkpointId)
    );

    if (removed > 0) {
      await saveState(state);
    }

    return removed;
  }

  /**
   * Get diff between current state and a checkpoint
   */
  async getDiff(checkpointId: string): Promise<string> {
    const state = this.getState();
    const checkpoint = state.checkpoints.find(cp => cp.id === checkpointId);

    if (!checkpoint) {
      throw new Error(`Checkpoint not found: ${checkpointId}`);
    }

    // Get current HEAD
    const head = await git.resolveRef({ fs, dir: this.workingDir, ref: 'HEAD' });

    // Get commit objects
    const [headCommit, checkpointCommit] = await Promise.all([
      git.readCommit({ fs, dir: this.workingDir, oid: head }),
      git.readCommit({ fs, dir: this.workingDir, oid: checkpoint.sha }),
    ]);

    // Simple diff representation (full diff would require more complex implementation)
    const changedFiles: string[] = [];

    // Walk trees and compare
    const headTree = await git.readTree({ fs, dir: this.workingDir, oid: headCommit.commit.tree });
    const checkpointTree = await git.readTree({ fs, dir: this.workingDir, oid: checkpointCommit.commit.tree });

    const headFiles = new Map(headTree.tree.map(e => [e.path, e.oid]));
    const checkpointFiles = new Map(checkpointTree.tree.map(e => [e.path, e.oid]));

    // Find changed files
    for (const [path, oid] of headFiles) {
      const checkpointOid = checkpointFiles.get(path);
      if (!checkpointOid) {
        changedFiles.push(`+ ${path} (added)`);
      } else if (checkpointOid !== oid) {
        changedFiles.push(`~ ${path} (modified)`);
      }
    }

    for (const [path] of checkpointFiles) {
      if (!headFiles.has(path)) {
        changedFiles.push(`- ${path} (deleted)`);
      }
    }

    return changedFiles.join('\n') || 'No changes';
  }
}

// Singleton instance
let defaultManager: CheckpointManager | null = null;

export async function getCheckpointManager(workingDir?: string): Promise<CheckpointManager> {
  if (!defaultManager) {
    defaultManager = new CheckpointManager(workingDir);
    await defaultManager.initialize();
  }
  return defaultManager;
}

export function closeCheckpointManager(): void {
  defaultManager = null;
}
