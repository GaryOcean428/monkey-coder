/**
 * Checkpoint Manager - Git-based checkpointing with operation journaling
 * 
 * Provides undo/restore capabilities through Git commits and fine-grained
 * operation journaling for individual file changes.
 */

import * as git from 'isomorphic-git';
import * as fs from 'fs';
import * as fsPromises from 'fs/promises';
import * as path from 'path';
import * as os from 'os';
import { randomUUID } from 'crypto';

// Types
export interface Operation {
  id: string;
  type: 'file_create' | 'file_edit' | 'file_delete' | 'bash_command';
  timestamp: number;
  file?: string;
  beforeContent?: string;
  afterContent?: string;
  command?: string;
  status: 'active' | 'undone';
}

export interface Checkpoint {
  id: string;
  sha: string;
  message: string;
  timestamp: number;
  operationCount: number;
  files: string[];
}

// Configuration
const CONFIG_DIR = path.join(os.homedir(), '.monkey-coder');
const CHECKPOINTS_DIR = path.join(CONFIG_DIR, 'checkpoints');
const JOURNAL_FILE = path.join(CONFIG_DIR, 'operations.jsonl');
const MAX_CHECKPOINTS = 50;
const MAX_CHECKPOINT_AGE_DAYS = 30;

/**
 * Checkpoint Manager for undo/restore functionality
 */
export class CheckpointManager {
  private workingDir: string;
  private operations: Operation[] = [];
  private checkpointBranch = 'monkey-coder-checkpoints';

  constructor(workingDir: string = process.cwd()) {
    this.workingDir = workingDir;
    this.ensureDirectories();
    this.loadOperations();
  }

  private ensureDirectories(): void {
    if (!fs.existsSync(CONFIG_DIR)) {
      fs.mkdirSync(CONFIG_DIR, { recursive: true });
    }
    if (!fs.existsSync(CHECKPOINTS_DIR)) {
      fs.mkdirSync(CHECKPOINTS_DIR, { recursive: true });
    }
  }

  private loadOperations(): void {
    try {
      if (fs.existsSync(JOURNAL_FILE)) {
        const content = fs.readFileSync(JOURNAL_FILE, 'utf-8');
        this.operations = content
          .trim()
          .split('\n')
          .filter(line => line)
          .map(line => JSON.parse(line));
      }
    } catch (error) {
      console.error('Failed to load operations journal:', error);
      this.operations = [];
    }
  }

  private async persistOperation(op: Operation): Promise<void> {
    await fsPromises.appendFile(JOURNAL_FILE, JSON.stringify(op) + '\n');
  }

  /**
   * Check if the working directory is a git repository
   */
  async isGitRepo(): Promise<boolean> {
    try {
      await git.findRoot({ fs, filepath: this.workingDir });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Initialize git repo if needed
   */
  async ensureGitRepo(): Promise<void> {
    if (!(await this.isGitRepo())) {
      await git.init({ fs, dir: this.workingDir, defaultBranch: 'main' });
    }
  }

  /**
   * Record a file creation operation
   */
  async recordFileCreate(filePath: string, content: string): Promise<Operation> {
    const op: Operation = {
      id: randomUUID(),
      type: 'file_create',
      timestamp: Date.now(),
      file: path.relative(this.workingDir, filePath),
      afterContent: content,
      status: 'active',
    };
    this.operations.push(op);
    await this.persistOperation(op);
    return op;
  }

  /**
   * Record a file edit operation
   */
  async recordFileEdit(filePath: string, before: string, after: string): Promise<Operation> {
    const op: Operation = {
      id: randomUUID(),
      type: 'file_edit',
      timestamp: Date.now(),
      file: path.relative(this.workingDir, filePath),
      beforeContent: before,
      afterContent: after,
      status: 'active',
    };
    this.operations.push(op);
    await this.persistOperation(op);
    return op;
  }

  /**
   * Record a file deletion operation
   */
  async recordFileDelete(filePath: string, content: string): Promise<Operation> {
    const op: Operation = {
      id: randomUUID(),
      type: 'file_delete',
      timestamp: Date.now(),
      file: path.relative(this.workingDir, filePath),
      beforeContent: content,
      status: 'active',
    };
    this.operations.push(op);
    await this.persistOperation(op);
    return op;
  }

  /**
   * Record a bash command execution
   */
  async recordBashCommand(command: string): Promise<Operation> {
    const op: Operation = {
      id: randomUUID(),
      type: 'bash_command',
      timestamp: Date.now(),
      command,
      status: 'active',
    };
    this.operations.push(op);
    await this.persistOperation(op);
    return op;
  }

  /**
   * Create a git checkpoint
   */
  async createCheckpoint(message: string): Promise<Checkpoint> {
    await this.ensureGitRepo();

    // Stage all changes and collect changed files
    const statusMatrix = await git.statusMatrix({ fs, dir: this.workingDir });
    const changedFiles: string[] = [];
    
    for (const [filepath, headStatus, workdirStatus, stageStatus] of statusMatrix) {
      if (workdirStatus !== stageStatus) {
        changedFiles.push(filepath);
        if (workdirStatus === 0) {
          await git.remove({ fs, dir: this.workingDir, filepath });
        } else {
          await git.add({ fs, dir: this.workingDir, filepath });
        }
      }
    }

    const sha = await git.commit({
      fs,
      dir: this.workingDir,
      message: `[checkpoint] ${message}`,
      author: {
        name: 'Monkey Coder',
        email: 'checkpoint@monkey-coder.local',
      },
    });

    const checkpoint: Checkpoint = {
      id: randomUUID(),
      sha,
      message,
      timestamp: Date.now(),
      operationCount: this.operations.filter(o => o.status === 'active').length,
      files: changedFiles,
    };

    const checkpointFile = path.join(CHECKPOINTS_DIR, `${checkpoint.id}.json`);
    await fsPromises.writeFile(checkpointFile, JSON.stringify(checkpoint, null, 2));

    return checkpoint;
  }

  /**
   * List all checkpoints
   */
  async listCheckpoints(): Promise<Checkpoint[]> {
    const checkpoints: Checkpoint[] = [];

    try {
      const files = await fsPromises.readdir(CHECKPOINTS_DIR);
      
      for (const file of files) {
        if (file.endsWith('.json')) {
          const content = await fsPromises.readFile(
            path.join(CHECKPOINTS_DIR, file),
            'utf-8'
          );
          checkpoints.push(JSON.parse(content));
        }
      }
    } catch (error) {
      // Directory might not exist yet
    }

    return checkpoints.sort((a, b) => b.timestamp - a.timestamp);
  }

  /**
   * Restore to a checkpoint
   */
  async restoreCheckpoint(checkpointId: string): Promise<void> {
    const checkpoints = await this.listCheckpoints();
    const checkpoint = checkpoints.find(c => c.id === checkpointId);

    if (!checkpoint) {
      throw new Error(`Checkpoint not found: ${checkpointId}`);
    }

    await git.checkout({
      fs,
      dir: this.workingDir,
      ref: checkpoint.sha,
      force: true,
    });
  }

  /**
   * Undo the last operation
   */
  async undoLast(): Promise<Operation | null> {
    const lastActive = this.operations.findLast((o: Operation) => o.status === 'active');
    
    if (!lastActive) {
      return null;
    }

    const filePath = lastActive.file 
      ? path.join(this.workingDir, lastActive.file)
      : null;

    switch (lastActive.type) {
      case 'file_create':
        if (filePath && fs.existsSync(filePath)) {
          await fsPromises.unlink(filePath);
        }
        break;

      case 'file_edit':
        if (filePath && lastActive.beforeContent !== undefined) {
          await fsPromises.writeFile(filePath, lastActive.beforeContent);
        }
        break;

      case 'file_delete':
        if (filePath && lastActive.beforeContent !== undefined) {
          const dir = path.dirname(filePath);
          if (!fs.existsSync(dir)) {
            await fsPromises.mkdir(dir, { recursive: true });
          }
          await fsPromises.writeFile(filePath, lastActive.beforeContent);
        }
        break;

      case 'bash_command':
        console.warn('Cannot automatically undo bash command:', lastActive.command);
        break;
    }

    lastActive.status = 'undone';
    await this.rewriteJournal();

    return lastActive;
  }

  /**
   * Redo the last undone operation
   */
  async redoLast(): Promise<Operation | null> {
    const lastUndone = this.operations.findLast((o: Operation) => o.status === 'undone');

    if (!lastUndone) {
      return null;
    }

    const filePath = lastUndone.file
      ? path.join(this.workingDir, lastUndone.file)
      : null;

    switch (lastUndone.type) {
      case 'file_create':
        if (filePath && lastUndone.afterContent !== undefined) {
          const dir = path.dirname(filePath);
          if (!fs.existsSync(dir)) {
            await fsPromises.mkdir(dir, { recursive: true });
          }
          await fsPromises.writeFile(filePath, lastUndone.afterContent);
        }
        break;

      case 'file_edit':
        if (filePath && lastUndone.afterContent !== undefined) {
          await fsPromises.writeFile(filePath, lastUndone.afterContent);
        }
        break;

      case 'file_delete':
        if (filePath && fs.existsSync(filePath)) {
          await fsPromises.unlink(filePath);
        }
        break;

      case 'bash_command':
        console.warn('Cannot automatically redo bash command:', lastUndone.command);
        break;
    }

    lastUndone.status = 'active';
    await this.rewriteJournal();

    return lastUndone;
  }

  /**
   * Alias for undoLast() to match API naming in issue
   */
  async undoLastOperation(): Promise<Operation | null> {
    return this.undoLast();
  }

  private async rewriteJournal(): Promise<void> {
    const content = this.operations.map(op => JSON.stringify(op)).join('\n') + '\n';
    await fsPromises.writeFile(JOURNAL_FILE, content);
  }

  /**
   * Get recent operations
   */
  getRecentOperations(limit: number = 20): Operation[] {
    return this.operations.slice(-limit);
  }

  /**
   * Get active (not undone) operations
   */
  getActiveOperations(): Operation[] {
    return this.operations.filter(o => o.status === 'active');
  }

  /**
   * List all operations with proper naming (alias for getRecentOperations)
   */
  listOperations(limit: number = 20): Operation[] {
    return this.getRecentOperations(limit);
  }

  /**
   * Get diff from a checkpoint to current state
   */
  async getDiff(checkpointId: string): Promise<string> {
    const checkpoints = await this.listCheckpoints();
    const checkpoint = checkpoints.find(c => c.id === checkpointId || c.id.startsWith(checkpointId));

    if (!checkpoint) {
      throw new Error(`Checkpoint not found: ${checkpointId}`);
    }

    try {
      // Get current HEAD
      const commits = await git.log({ fs, dir: this.workingDir, depth: 1 });
      const currentSha = commits[0]?.oid || 'HEAD';

      // Get the diff between checkpoint and current state
      const statusMatrix = await git.statusMatrix({
        fs,
        dir: this.workingDir,
        ref: checkpoint.sha,
      });

      let diff = '';
      for (const [filepath, headStatus, workdirStatus] of statusMatrix) {
        // headStatus: 0=absent, 1=present, 2=modified
        // workdirStatus: 0=absent, 1=present, 2=modified
        if (headStatus !== workdirStatus) {
          if (headStatus === 0 && workdirStatus === 1) {
            diff += `+ ${filepath} (added)\n`;
          } else if (headStatus === 1 && workdirStatus === 0) {
            diff += `- ${filepath} (deleted)\n`;
          } else if (headStatus === 1 && workdirStatus === 2) {
            diff += `~ ${filepath} (modified)\n`;
          }
        }
      }

      return diff || 'No changes since checkpoint';
    } catch (error) {
      return `Error getting diff: ${error}`;
    }
  }

  /**
   * Clean up old checkpoints based on retention policy
   */
  async cleanupOldCheckpoints(): Promise<number> {
    const checkpoints = await this.listCheckpoints();
    const cutoff = Date.now() - MAX_CHECKPOINT_AGE_DAYS * 24 * 60 * 60 * 1000;
    let deleted = 0;

    for (const checkpoint of checkpoints) {
      if (checkpoint.timestamp < cutoff) {
        const file = path.join(CHECKPOINTS_DIR, `${checkpoint.id}.json`);
        try {
          await fsPromises.unlink(file);
          deleted++;
        } catch {
          // Ignore errors
        }
      }
    }

    const remaining = checkpoints
      .filter(c => c.timestamp >= cutoff)
      .sort((a, b) => b.timestamp - a.timestamp);

    for (const checkpoint of remaining.slice(MAX_CHECKPOINTS)) {
      const file = path.join(CHECKPOINTS_DIR, `${checkpoint.id}.json`);
      try {
        await fsPromises.unlink(file);
        deleted++;
      } catch {
        // Ignore errors
      }
    }

    return deleted;
  }

  /**
   * Clear all operations (for testing or reset)
   */
  async clearOperations(): Promise<void> {
    this.operations = [];
    if (fs.existsSync(JOURNAL_FILE)) {
      await fsPromises.unlink(JOURNAL_FILE);
    }
  }
}

// Singleton instance
let defaultManager: CheckpointManager | null = null;

export function getCheckpointManager(workingDir?: string): CheckpointManager {
  if (!defaultManager || (workingDir && workingDir !== defaultManager['workingDir'])) {
    defaultManager = new CheckpointManager(workingDir);
  }
  return defaultManager;
}
