/**
 * Git commands for Monkey Coder CLI
 * Handles git operations integrated with AI capabilities
 */

import { Command } from 'commander';
import chalk from 'chalk';

import { ConfigManager } from '../config.js';
import { formatError } from '../utils.js';

import { CommandDefinition } from './registry.js';

/**
 * Create the git command group
 */
export function createGitCommand(config: ConfigManager): Command {
  const git = new Command('git')
    .description('Git operations with AI assistance')
    .alias('g');

  // git commit
  git
    .command('commit')
    .description('Create an AI-assisted commit')
    .option('-m, --message <message>', 'Commit message')
    .option('--ai', 'Generate commit message with AI')
    .option('-a, --all', 'Commit all changed files')
    .addHelpText('after', `
Examples:
  $ monkey git commit -m "feat: add new feature"
    Create a commit with a message

  $ monkey git commit --ai
    Generate commit message with AI

  $ monkey git commit --ai --all
    Stage all and create AI-assisted commit
`)
    .action(async (options: any) => {
      try {
        console.log(chalk.blue('📝 Git commit...'));
        
        if (options.ai) {
          console.log(chalk.yellow('\n⚠️  AI-assisted commits not yet implemented'));
          console.log(chalk.gray('This will analyze changes and generate commit messages'));
        } else if (options.message) {
          console.log(chalk.gray(`Message: ${options.message}`));
          console.log(chalk.yellow('\n⚠️  Git integration not yet implemented'));
        } else {
          console.log(chalk.red('Error: Either --message or --ai is required'));
        }
      } catch (error: any) {
        console.error(formatError(error.message || 'Commit failed'));
        process.exit(1);
      }
    });

  // git branch
  git
    .command('branch')
    .description('List, create, or delete branches')
    .argument('[branch-name]', 'Branch name for creation')
    .option('-d, --delete', 'Delete branch')
    .option('-l, --list', 'List all branches')
    .addHelpText('after', `
Examples:
  $ monkey git branch --list
    List all branches

  $ monkey git branch feature-x
    Create a new branch

  $ monkey git branch feature-x --delete
    Delete a branch
`)
    .action(async (branchName: string | undefined, options: any) => {
      try {
        console.log(chalk.blue('🌿 Git branch...'));
        console.log(chalk.yellow('\n⚠️  Git branch operations not yet implemented'));
      } catch (error: any) {
        console.error(formatError(error.message || 'Branch operation failed'));
        process.exit(1);
      }
    });

  // git status
  git
    .command('status')
    .description('Show the working tree status')
    .addHelpText('after', `
Examples:
  $ monkey git status
    Show git status with AI insights
`)
    .action(async () => {
      try {
        console.log(chalk.blue('📊 Git status...'));
        console.log(chalk.yellow('\n⚠️  Git status not yet implemented'));
      } catch (error: any) {
        console.error(formatError(error.message || 'Status check failed'));
        process.exit(1);
      }
    });

  return git;
}

/**
 * Command definition for registry
 */
export const gitCommandDefinition: CommandDefinition = {
  name: 'git',
  aliases: ['g'],
  description: 'Git operations with AI assistance',
  category: 'git',
  subcommands: [
    {
      name: 'commit',
      description: 'Create an AI-assisted commit',
      category: 'git',
      options: [
        { flags: '-m, --message <message>', description: 'Commit message' },
        { flags: '--ai', description: 'Generate message with AI' },
        { flags: '-a, --all', description: 'Commit all changed files' }
      ]
    },
    {
      name: 'branch',
      description: 'List, create, or delete branches',
      category: 'git',
      arguments: [
        { name: 'branch-name', description: 'Branch name', required: false }
      ],
      options: [
        { flags: '-d, --delete', description: 'Delete branch' },
        { flags: '-l, --list', description: 'List all branches' }
      ]
    },
    {
      name: 'status',
      description: 'Show working tree status',
      category: 'git'
    }
  ]
};
