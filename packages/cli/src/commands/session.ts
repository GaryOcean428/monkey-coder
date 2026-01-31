/**
 * Session management commands
 * Provides CLI interface for persistent conversation sessions
 */

import * as fs from 'fs';

import { Command } from 'commander';
import chalk from 'chalk';
import Table from 'cli-table3';
import inquirer from 'inquirer';

import { getSessionManager, Session } from '../session-manager.js';
import { formatError } from '../utils.js';

// Display constants
const SESSION_ID_DISPLAY_LENGTH = 8;
const SESSION_NAME_DISPLAY_LENGTH = 30;
const SESSION_DIR_DISPLAY_LENGTH = 30;
const MESSAGE_PREVIEW_LENGTH = 200;

/**
 * Format session ID for display (truncate to fixed length)
 */
function formatSessionId(sessionId: string): string {
  return sessionId.slice(0, SESSION_ID_DISPLAY_LENGTH);
}

/**
 * Create the session command group
 */
export function createSessionCommand(): Command {
  const session = new Command('session')
    .description('Manage conversation sessions')
    .alias('sessions');

  // List sessions
  session
    .command('list')
    .description('List all sessions')
    .alias('ls')
    .option('-n, --limit <n>', 'Number of sessions to show', '20')
    .addHelpText('after', `
Examples:
  $ monkey session list
    List the 20 most recent sessions

  $ monkey session list -n 50
    List the 50 most recent sessions
`)
    .action(async (options) => {
      try {
        const manager = getSessionManager();
        const sessions = manager.listSessions({ limit: parseInt(options.limit) });
        
        if (sessions.length === 0) {
          console.log(chalk.yellow('No sessions found.'));
          console.log(chalk.gray('\nRun "monkey session start" to create a new session'));
          return;
        }

        const table = new Table({
          head: ['ID', 'Name', 'Directory', 'Updated', 'Messages'],
          style: { head: ['cyan'] }
        });

        for (const s of sessions) {
          const messages = manager.getMessages(s.id);
          table.push([
            formatSessionId(s.id),
            s.name.slice(0, SESSION_NAME_DISPLAY_LENGTH),
            s.workingDirectory.slice(-SESSION_DIR_DISPLAY_LENGTH),
            new Date(s.updatedAt * 1000).toLocaleDateString(),
            messages.length.toString()
          ]);
        }

        console.log('\n' + table.toString());
        console.log(chalk.gray(`\nShowing ${sessions.length} session(s)`));
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to list sessions'));
        process.exit(1);
      }
    });

  // Start new session
  session
    .command('start')
    .description('Start a new session')
    .option('-n, --name <name>', 'Session name')
    .addHelpText('after', `
Examples:
  $ monkey session start
    Start a new session with auto-generated name

  $ monkey session start --name "Feature X"
    Start a new session with custom name
`)
    .action(async (options) => {
      try {
        const manager = getSessionManager();
        const newSession = manager.createSession({
          name: options.name,
          workingDirectory: process.cwd(),
        });
        
        console.log(chalk.green(`✓ Started session: ${formatSessionId(newSession.id)}`));
        console.log(`  Name: ${newSession.name}`);
        console.log(`  Directory: ${newSession.workingDirectory}`);
        console.log(chalk.gray('\nUse "monkey chat --continue" to continue this session'));
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to start session'));
        process.exit(1);
      }
    });

  // Resume session
  session
    .command('resume [id]')
    .description('Resume a session (uses last session if no ID provided)')
    .addHelpText('after', `
Examples:
  $ monkey session resume
    Resume the last active session

  $ monkey session resume abc123
    Resume session with ID starting with "abc123"
`)
    .action(async (id) => {
      try {
        const manager = getSessionManager();
        
        let targetSession: Session | null;
        if (id) {
          // Find session by partial ID match
          const sessions = manager.listSessions({ limit: 100 });
          targetSession = sessions.find(s => s.id.startsWith(id)) || null;
        } else {
          const currentId = manager.getCurrentSessionId();
          targetSession = currentId ? manager.getSession(currentId) : null;
        }

        if (!targetSession) {
          console.log(chalk.red('Session not found.'));
          console.log(chalk.gray('\nRun "monkey session list" to see available sessions'));
          process.exit(1);
        }

        manager.setCurrentSessionId(targetSession.id);
        const context = manager.getSessionContext(targetSession.id);
        
        console.log(chalk.green(`✓ Resumed session: ${formatSessionId(targetSession.id)}`));
        console.log(`  Name: ${targetSession.name}`);
        console.log(`  Messages: ${context?.messages.length || 0}`);
        console.log(`  Tokens: ${context?.totalTokens || 0}`);
        console.log(chalk.gray('\nUse "monkey chat --continue" to continue this session'));
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to resume session'));
        process.exit(1);
      }
    });

  // Show session details
  session
    .command('show [id]')
    .description('Show session details and recent messages')
    .option('-m, --messages <n>', 'Number of messages to show', '10')
    .addHelpText('after', `
Examples:
  $ monkey session show
    Show details of current session

  $ monkey session show abc123
    Show details of session with ID starting with "abc123"

  $ monkey session show abc123 --messages 20
    Show details with 20 most recent messages
`)
    .action(async (id, options) => {
      try {
        const manager = getSessionManager();
        
        const targetId = id || manager.getCurrentSessionId();
        if (!targetId) {
          console.log(chalk.red('No session specified and no current session.'));
          console.log(chalk.gray('\nRun "monkey session list" to see available sessions'));
          process.exit(1);
        }

        // If partial ID provided, find the full ID
        let fullId = targetId;
        if (id) {
          const sessions = manager.listSessions({ limit: 100 });
          const match = sessions.find(s => s.id.startsWith(id));
          if (!match) {
            console.log(chalk.red('Session not found.'));
            console.log(chalk.gray('\nRun "monkey session list" to see available sessions'));
            process.exit(1);
          }
          fullId = match.id;
        }

        const context = manager.getSessionContext(fullId);
        if (!context) {
          console.log(chalk.red('Session not found.'));
          console.log(chalk.gray('\nRun "monkey session list" to see available sessions'));
          process.exit(1);
        }

        console.log(chalk.cyan.bold(`\nSession: ${context.session.name}`));
        console.log(`ID: ${context.session.id}`);
        console.log(`Directory: ${context.session.workingDirectory}`);
        console.log(`Created: ${new Date(context.session.createdAt * 1000).toLocaleString()}`);
        console.log(`Updated: ${new Date(context.session.updatedAt * 1000).toLocaleString()}`);
        console.log(`Total Tokens: ${context.totalTokens}`);
        console.log('');

        const limit = parseInt(options.messages);
        const messages = context.messages.slice(-limit);
        
        if (messages.length === 0) {
          console.log(chalk.gray('No messages in this session yet'));
        } else {
          console.log(chalk.cyan.bold(`Recent Messages (${messages.length} of ${context.messages.length}):\n`));
          
          for (const msg of messages) {
            const roleColor = {
              system: chalk.gray,
              user: chalk.green,
              assistant: chalk.cyan,
              tool: chalk.yellow,
            }[msg.role] || chalk.white;
            
            console.log(roleColor(`[${msg.role}] (${msg.tokenCount} tokens)`));
            const content = msg.content.slice(0, MESSAGE_PREVIEW_LENGTH);
            console.log(content + (msg.content.length > MESSAGE_PREVIEW_LENGTH ? '...' : ''));
            console.log('');
          }
        }
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to show session'));
        process.exit(1);
      }
    });

  // Delete session
  session
    .command('delete <id>')
    .description('Delete a session')
    .option('-f, --force', 'Skip confirmation')
    .addHelpText('after', `
Examples:
  $ monkey session delete abc123
    Delete session with confirmation prompt

  $ monkey session delete abc123 --force
    Delete session without confirmation
`)
    .action(async (id, options) => {
      try {
        const manager = getSessionManager();
        
        // Find session by partial ID
        const sessions = manager.listSessions({ limit: 100 });
        const targetSession = sessions.find(s => s.id.startsWith(id));
        
        if (!targetSession) {
          console.log(chalk.red('Session not found.'));
          console.log(chalk.gray('\nRun "monkey session list" to see available sessions'));
          process.exit(1);
        }

        if (!options.force) {
          const { confirm } = await inquirer.prompt([{
            type: 'confirm',
            name: 'confirm',
            message: `Delete session "${targetSession.name}"?`,
            default: false
          }]);
          
          if (!confirm) {
            console.log('Cancelled.');
            return;
          }
        }

        manager.deleteSession(targetSession.id);
        console.log(chalk.green(`✓ Deleted session: ${formatSessionId(targetSession.id)}`));
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to delete session'));
        process.exit(1);
      }
    });

  // Export session
  session
    .command('export <id>')
    .description('Export session to JSON or Markdown file')
    .option('-f, --format <format>', 'Output format (json or markdown)', 'json')
    .option('-o, --output <file>', 'Output file path')
    .addHelpText('after', `
Examples:
  $ monkey session export abc123
    Export session to JSON file (session-abc123.json)

  $ monkey session export abc123 --format markdown
    Export session to Markdown file (session-abc123.md)

  $ monkey session export abc123 --output my-session.json
    Export session to specific file
`)
    .action(async (id, options) => {
      try {
        const manager = getSessionManager();
        
        // Find session by partial ID
        const sessions = manager.listSessions({ limit: 100 });
        const match = sessions.find(s => s.id.startsWith(id));
        
        if (!match) {
          console.error(chalk.red(`Session not found: ${id}`));
          console.log(chalk.gray('\nRun "monkey session list" to see available sessions'));
          process.exit(1);
        }

        const context = manager.getSessionContext(match.id);
        if (!context) {
          console.error(chalk.red('Failed to load session context'));
          process.exit(1);
        }

        let output: string;
        let ext: string;

        if (options.format === 'markdown') {
          ext = 'md';
          output = `# Session: ${context.session.name}\n\n`;
          output += `- ID: ${context.session.id}\n`;
          output += `- Created: ${new Date(context.session.createdAt * 1000).toISOString()}\n`;
          output += `- Updated: ${new Date(context.session.updatedAt * 1000).toISOString()}\n`;
          output += `- Working Directory: ${context.session.workingDirectory}\n`;
          if (context.session.gitBranch) {
            output += `- Git Branch: ${context.session.gitBranch}\n`;
          }
          output += `- Total Tokens: ${context.totalTokens}\n`;
          output += `\n## Messages (${context.messages.length})\n\n`;
          
          for (const msg of context.messages) {
            output += `### ${msg.role.charAt(0).toUpperCase() + msg.role.slice(1)}\n\n`;
            output += `*Tokens: ${msg.tokenCount}, Time: ${new Date(msg.createdAt * 1000).toISOString()}*\n\n`;
            output += `${msg.content}\n\n`;
            if (msg.toolCallId) {
              output += `*Tool Call ID: ${msg.toolCallId}*\n\n`;
            }
            output += '---\n\n';
          }
        } else {
          ext = 'json';
          output = JSON.stringify(context, null, 2);
        }

        const outFile = options.output || `session-${formatSessionId(match.id)}.${ext}`;
        fs.writeFileSync(outFile, output);
        console.log(chalk.green(`✓ Exported to: ${outFile}`));
        console.log(chalk.gray(`  Format: ${options.format}`));
        console.log(chalk.gray(`  Messages: ${context.messages.length}`));
        console.log(chalk.gray(`  Total Tokens: ${context.totalTokens}`));
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to export session'));
        process.exit(1);
      }
    });

  // Cleanup old sessions
  session
    .command('cleanup')
    .description('Remove old sessions based on retention policy')
    .option('--days <n>', 'Max age in days', '30')
    .option('--max <n>', 'Max sessions to keep', '100')
    .addHelpText('after', `
Examples:
  $ monkey session cleanup
    Remove sessions older than 30 days, keeping max 100

  $ monkey session cleanup --days 60 --max 200
    Remove sessions older than 60 days, keeping max 200
`)
    .action(async (options) => {
      try {
        const manager = getSessionManager();
        const removed = manager.cleanupOldSessions(
          parseInt(options.days),
          parseInt(options.max)
        );
        
        if (removed === 0) {
          console.log(chalk.green('✓ No old sessions to remove'));
        } else {
          console.log(chalk.green(`✓ Removed ${removed} old session${removed > 1 ? 's' : ''}`));
        }
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to cleanup sessions'));
        process.exit(1);
      }
    });

  return session;
}
