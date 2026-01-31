/**
 * Issue commands for Monkey Coder CLI
 * Handles issue creation and management
 */

import { Command } from 'commander';
import chalk from 'chalk';

import { ConfigManager } from '../config.js';
import { formatError } from '../utils.js';

import { CommandDefinition } from './registry.js';

/**
 * Create the issue command group
 */
export function createIssueCommand(config: ConfigManager): Command {
  const issue = new Command('issue')
    .description('Manage issues');

  // issue create
  issue
    .command('create')
    .description('Create a new issue')
    .option('-t, --title <title>', 'Issue title')
    .option('-b, --body <body>', 'Issue description')
    .option('-l, --labels <labels>', 'Comma-separated labels')
    .option('-a, --assignee <username>', 'Assignee username')
    .option('--ai', 'Generate issue content with AI')
    .addHelpText('after', `
Examples:
  $ monkey issue create --title "Bug: X doesn't work" --body "Description..."
    Create an issue

  $ monkey issue create --ai
    Create an issue with AI-generated content

  $ monkey issue create -t "Feature request" -l "enhancement,feature"
    Create an issue with labels
`)
    .action(async (options: any) => {
      try {
        console.log(chalk.blue('🐛 Creating issue...'));
        
        if (options.ai) {
          console.log(chalk.yellow('\n⚠️  AI-assisted issue creation not yet implemented'));
        } else {
          console.log(chalk.yellow('\n⚠️  Issue creation not yet implemented'));
        }
        console.log(chalk.gray('This will be connected to GitHub API in a future update'));
      } catch (error: any) {
        console.error(formatError(error.message || 'Issue creation failed'));
        process.exit(1);
      }
    });

  // issue list
  issue
    .command('list')
    .description('List issues')
    .alias('ls')
    .option('--state <state>', 'Filter by state (open, closed, all)', 'open')
    .option('--author <username>', 'Filter by author')
    .option('--assignee <username>', 'Filter by assignee')
    .option('--label <labels>', 'Filter by labels')
    .option('--limit <limit>', 'Number of issues to show', parseInt, 30)
    .addHelpText('after', `
Examples:
  $ monkey issue list
    List open issues

  $ monkey issue list --state all
    List all issues

  $ monkey issue list --label bug --assignee me
    List bugs assigned to me
`)
    .action(async (options: any) => {
      try {
        console.log(chalk.blue('📋 Listing issues...'));
        console.log(chalk.yellow('\n⚠️  Issue listing not yet implemented'));
      } catch (error: any) {
        console.error(formatError(error.message || 'Issue listing failed'));
        process.exit(1);
      }
    });

  // issue view
  issue
    .command('view')
    .description('View an issue')
    .argument('<number>', 'Issue number')
    .option('--web', 'Open in web browser')
    .option('--comments', 'Show comments')
    .addHelpText('after', `
Examples:
  $ monkey issue view 123
    View issue #123

  $ monkey issue view 123 --web
    Open issue #123 in browser

  $ monkey issue view 123 --comments
    View issue with comments
`)
    .action(async (number: string, options: any) => {
      try {
        console.log(chalk.blue(`👀 Viewing issue #${number}...`));
        console.log(chalk.yellow('\n⚠️  Issue viewing not yet implemented'));
      } catch (error: any) {
        console.error(formatError(error.message || 'Issue view failed'));
        process.exit(1);
      }
    });

  // issue close
  issue
    .command('close')
    .description('Close an issue')
    .argument('<number>', 'Issue number')
    .option('--comment <text>', 'Add a closing comment')
    .addHelpText('after', `
Examples:
  $ monkey issue close 123
    Close issue #123

  $ monkey issue close 123 --comment "Fixed in PR #124"
    Close with comment
`)
    .action(async (number: string, options: any) => {
      try {
        console.log(chalk.blue(`✓ Closing issue #${number}...`));
        console.log(chalk.yellow('\n⚠️  Issue closing not yet implemented'));
      } catch (error: any) {
        console.error(formatError(error.message || 'Issue close failed'));
        process.exit(1);
      }
    });

  return issue;
}

/**
 * Command definition for registry
 */
export const issueCommandDefinition: CommandDefinition = {
  name: 'issue',
  description: 'Manage issues',
  category: 'project',
  subcommands: [
    {
      name: 'create',
      description: 'Create a new issue',
      category: 'project',
      options: [
        { flags: '-t, --title <title>', description: 'Issue title' },
        { flags: '-b, --body <body>', description: 'Issue description' },
        { flags: '-l, --labels <labels>', description: 'Labels' },
        { flags: '-a, --assignee <username>', description: 'Assignee' },
        { flags: '--ai', description: 'Generate with AI' }
      ]
    },
    {
      name: 'list',
      aliases: ['ls'],
      description: 'List issues',
      category: 'project',
      options: [
        { flags: '--state <state>', description: 'Filter by state', defaultValue: 'open' },
        { flags: '--author <username>', description: 'Filter by author' },
        { flags: '--assignee <username>', description: 'Filter by assignee' },
        { flags: '--label <labels>', description: 'Filter by labels' },
        { flags: '--limit <limit>', description: 'Number to show', defaultValue: 30 }
      ]
    },
    {
      name: 'view',
      description: 'View an issue',
      category: 'project',
      arguments: [
        { name: 'number', description: 'Issue number', required: true }
      ],
      options: [
        { flags: '--web', description: 'Open in browser' },
        { flags: '--comments', description: 'Show comments' }
      ]
    },
    {
      name: 'close',
      description: 'Close an issue',
      category: 'project',
      arguments: [
        { name: 'number', description: 'Issue number', required: true }
      ],
      options: [
        { flags: '--comment <text>', description: 'Closing comment' }
      ]
    }
  ]
};
