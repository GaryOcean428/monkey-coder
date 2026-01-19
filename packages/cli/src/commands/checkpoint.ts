/**
 * Checkpoint management commands
 * Provides CLI interface for git-based checkpointing and operation undo/restore
 */

import { Command } from 'commander';
import { getCheckpointManager } from '../checkpoint-manager.js';
import chalk from 'chalk';
import Table from 'cli-table3';
import inquirer from 'inquirer';

/**
 * Create the checkpoint command group
 */
export function createCheckpointCommand(): Command {
  const checkpoint = new Command('checkpoint')
    .alias('cp')
    .description('Manage checkpoints for undo/restore');

  // List checkpoints
  checkpoint
    .command('list')
    .description('List all checkpoints')
    .option('-n, --limit <n>', 'Number to show', '20')
    .action(async (options) => {
      try {
        const manager = getCheckpointManager();
        const allCheckpoints = await manager.listCheckpoints();
        const checkpoints = allCheckpoints.slice(0, parseInt(options.limit));
        
        if (checkpoints.length === 0) {
          console.log(chalk.yellow('No checkpoints found.'));
          return;
        }

        const table = new Table({
          head: ['ID', 'Message', 'Time', 'Files'],
          style: { head: ['cyan'] }
        });

        for (const cp of checkpoints) {
          table.push([
            cp.id.slice(0, 8),
            cp.message.slice(0, 40),
            new Date(cp.timestamp).toLocaleString(),
            cp.files.length.toString()
          ]);
        }

        console.log(table.toString());
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
        process.exit(1);
      }
    });

  // Create checkpoint
  checkpoint
    .command('create [message]')
    .description('Create a checkpoint')
    .action(async (message) => {
      try {
        const manager = getCheckpointManager();
        const cp = await manager.createCheckpoint(message || 'Manual checkpoint');
        
        console.log(chalk.green(`✓ Created checkpoint: ${cp.id.slice(0, 8)}`));
        console.log(`  Message: ${cp.message}`);
        console.log(`  Files: ${cp.files.length}`);
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
        process.exit(1);
      }
    });

  // Restore to checkpoint
  checkpoint
    .command('restore <id>')
    .description('Restore to a specific checkpoint')
    .option('-f, --force', 'Skip confirmation')
    .action(async (id, options) => {
      try {
        const manager = getCheckpointManager();
        
        // Find by partial ID
        const checkpoints = await manager.listCheckpoints();
        const cp = checkpoints.find(c => c.id.startsWith(id));
        
        if (!cp) {
          console.log(chalk.red('Checkpoint not found.'));
          process.exit(1);
        }

        if (!options.force) {
          const { confirm } = await inquirer.prompt([{
            type: 'confirm',
            name: 'confirm',
            message: `Restore to checkpoint "${cp.message}"? This will discard current changes.`,
            default: false
          }]);
          
          if (!confirm) {
            console.log('Cancelled.');
            return;
          }
        }

        await manager.restoreCheckpoint(cp.id);
        console.log(chalk.green(`✓ Restored to checkpoint: ${cp.id.slice(0, 8)}`));
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
        process.exit(1);
      }
    });

  // Undo last operation
  checkpoint
    .command('undo')
    .description('Undo the last file operation')
    .action(async () => {
      try {
        const manager = getCheckpointManager();
        const undone = await manager.undoLastOperation();
        
        if (!undone) {
          console.log(chalk.yellow('Nothing to undo.'));
          return;
        }

        console.log(chalk.green(`✓ Undone: ${undone.type} on ${undone.file || 'unknown'}`));
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
        process.exit(1);
      }
    });

  // Show diff from checkpoint
  checkpoint
    .command('diff <id>')
    .description('Show changes since checkpoint')
    .action(async (id) => {
      try {
        const manager = getCheckpointManager();
        
        const checkpoints = await manager.listCheckpoints();
        const cp = checkpoints.find(c => c.id.startsWith(id));
        
        if (!cp) {
          console.log(chalk.red('Checkpoint not found.'));
          process.exit(1);
        }

        const diff = await manager.getDiff(cp.id);
        console.log(chalk.cyan(`Changes since: ${cp.message}`));
        console.log('');
        
        for (const line of diff.split('\n')) {
          if (line.startsWith('+')) {
            console.log(chalk.green(line));
          } else if (line.startsWith('-')) {
            console.log(chalk.red(line));
          } else if (line.startsWith('~')) {
            console.log(chalk.yellow(line));
          } else {
            console.log(line);
          }
        }
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
        process.exit(1);
      }
    });

  // Show operations in current checkpoint
  checkpoint
    .command('operations')
    .description('List operations since last checkpoint')
    .action(async () => {
      try {
        const manager = getCheckpointManager();
        const operations = manager.listOperations();
        
        if (operations.length === 0) {
          console.log(chalk.yellow('No operations recorded.'));
          return;
        }

        const table = new Table({
          head: ['Type', 'File', 'Time', 'Status'],
          style: { head: ['cyan'] }
        });

        for (const op of operations) {
          const statusColor = op.status === 'active' ? chalk.green : chalk.gray;
          table.push([
            op.type,
            op.file || 'N/A',
            new Date(op.timestamp).toLocaleTimeString(),
            statusColor(op.status)
          ]);
        }

        console.log(table.toString());
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
        process.exit(1);
      }
    });

  return checkpoint;
}
