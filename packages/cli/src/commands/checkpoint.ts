/**
 * Checkpoint management commands
 * Provides CLI interface for git-based checkpointing and operation undo/restore
 */

import { Command } from 'commander';
import { getCheckpointManager } from '../checkpoint-manager.js';
import chalk from 'chalk';
import Table from 'cli-table3';
import { confirm } from '@inquirer/prompts';

/**
 * Register all checkpoint-related commands (including top-level commands)
 */
export function registerCheckpointCommands(program: Command): void {
  const checkpoint = new Command('checkpoint')
    .alias('cp')
    .description('Manage checkpoints');

  // checkpoint create [message]
  checkpoint
    .command('create [message]')
    .description('Create a new checkpoint')
    .action(async (message) => {
      const mgr = getCheckpointManager();
      const msg = message || `Manual checkpoint at ${new Date().toISOString()}`;
      
      try {
        const cp = await mgr.createCheckpoint(msg);
        console.log(chalk.green(`✓ Created checkpoint: ${cp.id.slice(0, 8)}`));
        console.log(`  SHA: ${cp.sha.slice(0, 8)}`);
        console.log(`  Message: ${cp.message}`);
      } catch (error: unknown) {
        const errorMsg = error instanceof Error ? error.message : String(error);
        console.error(chalk.red(`Failed to create checkpoint: ${errorMsg}`));
        process.exit(1);
      }
    });

  // checkpoint list
  checkpoint
    .command('list')
    .description('List recent checkpoints')
    .option('-n, --limit <count>', 'Number of checkpoints to show', '10')
    .action(async (options) => {
      const mgr = getCheckpointManager();
      const checkpoints = await mgr.listCheckpoints();
      const limited = checkpoints.slice(0, parseInt(options.limit));

      if (limited.length === 0) {
        console.log('No checkpoints found.');
        return;
      }

      const table = new Table({
        head: ['ID', 'SHA', 'Message', 'Created', 'Ops'],
        colWidths: [10, 10, 35, 22, 6],
      });

      for (const cp of limited) {
        table.push([
          cp.id.slice(0, 8),
          cp.sha.slice(0, 8),
          cp.message.slice(0, 33),
          new Date(cp.timestamp).toLocaleString(),
          cp.operationCount.toString(),
        ]);
      }

      console.log(table.toString());
    });

  // checkpoint restore <id>
  checkpoint
    .command('restore <id>')
    .description('Restore to a checkpoint')
    .option('-f, --force', 'Skip confirmation')
    .action(async (id, options) => {
      const mgr = getCheckpointManager();
      const checkpoints = await mgr.listCheckpoints();
      const match = checkpoints.find(c => c.id.startsWith(id) || c.sha.startsWith(id));

      if (!match) {
        console.error(chalk.red(`Checkpoint not found: ${id}`));
        process.exit(1);
      }

      if (!options.force) {
        const confirmed = await confirm({
          message: `Restore to checkpoint "${match.message}"? This will discard uncommitted changes.`,
          default: false,
        });
        if (!confirmed) {
          console.log('Cancelled.');
          return;
        }
      }

      await mgr.restoreCheckpoint(match.id);
      console.log(chalk.green(`✓ Restored to checkpoint: ${match.id.slice(0, 8)}`));
    });

  // checkpoint cleanup
  checkpoint
    .command('cleanup')
    .description('Remove old checkpoints')
    .action(async () => {
      const mgr = getCheckpointManager();
      const deleted = await mgr.cleanupOldCheckpoints();
      console.log(chalk.green(`Cleaned up ${deleted} old checkpoints`));
    });

  // Add checkpoint command to program
  program.addCommand(checkpoint);

  // Top-level undo command
  program
    .command('undo')
    .description('Undo the last file operation')
    .action(async () => {
      const mgr = getCheckpointManager();
      const op = await mgr.undoLast();

      if (!op) {
        console.log('Nothing to undo.');
        return;
      }

      console.log(chalk.green(`✓ Undone: ${op.type}`));
      if (op.file) {
        console.log(`  File: ${op.file}`);
      }
    });

  // Top-level redo command
  program
    .command('redo')
    .description('Redo the last undone operation')
    .action(async () => {
      const mgr = getCheckpointManager();
      const op = await mgr.redoLast();

      if (!op) {
        console.log('Nothing to redo.');
        return;
      }

      console.log(chalk.green(`✓ Redone: ${op.type}`));
      if (op.file) {
        console.log(`  File: ${op.file}`);
      }
    });

  // Top-level history command
  program
    .command('history')
    .description('Show recent operations')
    .option('-n, --limit <count>', 'Number of operations to show', '20')
    .action(async (options) => {
      const mgr = getCheckpointManager();
      const ops = mgr.getRecentOperations(parseInt(options.limit));

      if (ops.length === 0) {
        console.log('No operations recorded.');
        return;
      }

      const table = new Table({
        head: ['#', 'Type', 'File', 'Status', 'Time'],
        colWidths: [4, 14, 40, 8, 22],
      });

      ops.forEach((op, i) => {
        const statusColorFn = op.status === 'active' ? chalk.green : chalk.grey;
        table.push([
          (i + 1).toString(),
          op.type,
          (op.file || op.command || '-').slice(0, 38),
          statusColorFn(op.status),
          new Date(op.timestamp).toLocaleString(),
        ]);
      });

      console.log(table.toString());
    });
}

/**
 * Legacy function for backwards compatibility
 * @deprecated Use registerCheckpointCommands instead
 */
export function createCheckpointCommand(): Command {
  const program = new Command();
  registerCheckpointCommands(program);
  // Return just the checkpoint command
  return program.commands.find(cmd => cmd.name() === 'checkpoint') || new Command('checkpoint');
}
