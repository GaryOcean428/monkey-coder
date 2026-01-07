/**
 * Search commands for Monkey Coder CLI
 * Search repositories, code, and issues
 */

import { Command } from 'commander';
import chalk from 'chalk';
import { ConfigManager } from '../config.js';
import { formatError } from '../utils.js';
import { CommandDefinition } from './registry.js';

/**
 * Create the search command group
 */
export function createSearchCommand(config: ConfigManager): Command {
  const search = new Command('search')
    .description('Search repositories, code, and issues');

  // search repos
  search
    .command('repos')
    .description('Search repositories')
    .argument('<query>', 'Search query')
    .option('--language <lang>', 'Filter by programming language')
    .option('--stars <count>', 'Filter by minimum stars')
    .option('--topic <topic>', 'Filter by topic')
    .option('--limit <limit>', 'Number of results to show', parseInt, 30)
    .addHelpText('after', `
Examples:
  $ monkey search repos "machine learning"
    Search for repositories about machine learning

  $ monkey search repos "react" --language javascript --stars 1000
    Search for React repos with 1000+ stars

  $ monkey search repos "cli tools" --topic cli --limit 10
    Search for CLI tools repositories (max 10 results)
`)
    .action(async (query: string, options: any) => {
      try {
        console.log(chalk.blue(`🔍 Searching repositories for: "${query}"`));
        if (options.language) {
          console.log(chalk.gray(`Language: ${options.language}`));
        }
        if (options.stars) {
          console.log(chalk.gray(`Min stars: ${options.stars}`));
        }
        if (options.topic) {
          console.log(chalk.gray(`Topic: ${options.topic}`));
        }

        console.log(chalk.yellow('\n⚠️  Repository search not yet implemented'));
        console.log(chalk.gray('This will use GitHub Search API in a future update'));
      } catch (error: any) {
        console.error(formatError(error.message || 'Search failed'));
        process.exit(1);
      }
    });

  // search code
  search
    .command('code')
    .description('Search code across repositories')
    .argument('<query>', 'Code search query')
    .option('--repo <owner/repo>', 'Limit search to specific repository')
    .option('--language <lang>', 'Filter by programming language')
    .option('--path <path>', 'Filter by file path')
    .option('--extension <ext>', 'Filter by file extension')
    .option('--limit <limit>', 'Number of results to show', parseInt, 30)
    .addHelpText('after', `
Examples:
  $ monkey search code "function handleSubmit"
    Search for code containing that function

  $ monkey search code "import React" --language javascript
    Search for React imports in JavaScript

  $ monkey search code "async def" --repo owner/repo --language python
    Search for async functions in specific repository

  $ monkey search code "class.*Component" --extension tsx
    Search for class components in TypeScript files
`)
    .action(async (query: string, options: any) => {
      try {
        console.log(chalk.blue(`🔍 Searching code for: "${query}"`));
        if (options.repo) {
          console.log(chalk.gray(`Repository: ${options.repo}`));
        }
        if (options.language) {
          console.log(chalk.gray(`Language: ${options.language}`));
        }
        if (options.path) {
          console.log(chalk.gray(`Path: ${options.path}`));
        }
        if (options.extension) {
          console.log(chalk.gray(`Extension: ${options.extension}`));
        }

        console.log(chalk.yellow('\n⚠️  Code search not yet implemented'));
        console.log(chalk.gray('This will use GitHub Code Search API in a future update'));
      } catch (error: any) {
        console.error(formatError(error.message || 'Search failed'));
        process.exit(1);
      }
    });

  // search issues
  search
    .command('issues')
    .description('Search issues and pull requests')
    .argument('<query>', 'Issue search query')
    .option('--repo <owner/repo>', 'Limit search to specific repository')
    .option('--state <state>', 'Filter by state (open, closed, all)', 'open')
    .option('--label <labels>', 'Filter by labels (comma-separated)')
    .option('--author <username>', 'Filter by author')
    .option('--assignee <username>', 'Filter by assignee')
    .option('--is <type>', 'Filter by type (issue, pr)')
    .option('--limit <limit>', 'Number of results to show', parseInt, 30)
    .addHelpText('after', `
Examples:
  $ monkey search issues "bug in login"
    Search for issues about login bugs

  $ monkey search issues "typescript" --repo owner/repo --state all
    Search all issues in specific repository

  $ monkey search issues "memory leak" --label bug --is issue
    Search for bug-labeled issues about memory leaks

  $ monkey search issues "feature request" --author username
    Search for feature requests by specific author
`)
    .action(async (query: string, options: any) => {
      try {
        console.log(chalk.blue(`🔍 Searching issues for: "${query}"`));
        if (options.repo) {
          console.log(chalk.gray(`Repository: ${options.repo}`));
        }
        if (options.state) {
          console.log(chalk.gray(`State: ${options.state}`));
        }
        if (options.label) {
          console.log(chalk.gray(`Labels: ${options.label}`));
        }
        if (options.author) {
          console.log(chalk.gray(`Author: ${options.author}`));
        }
        if (options.assignee) {
          console.log(chalk.gray(`Assignee: ${options.assignee}`));
        }
        if (options.is) {
          console.log(chalk.gray(`Type: ${options.is}`));
        }

        console.log(chalk.yellow('\n⚠️  Issue search not yet implemented'));
        console.log(chalk.gray('This will use GitHub Issues Search API in a future update'));
      } catch (error: any) {
        console.error(formatError(error.message || 'Search failed'));
        process.exit(1);
      }
    });

  return search;
}

/**
 * Command definition for registry
 */
export const searchCommandDefinition: CommandDefinition = {
  name: 'search',
  description: 'Search repositories, code, and issues',
  category: 'project',
  subcommands: [
    {
      name: 'repos',
      description: 'Search repositories',
      category: 'project',
      arguments: [
        { name: 'query', description: 'Search query', required: true }
      ],
      options: [
        { flags: '--language <lang>', description: 'Filter by language' },
        { flags: '--stars <count>', description: 'Min stars' },
        { flags: '--topic <topic>', description: 'Filter by topic' },
        { flags: '--limit <limit>', description: 'Number of results', defaultValue: 30 }
      ]
    },
    {
      name: 'code',
      description: 'Search code across repositories',
      category: 'project',
      arguments: [
        { name: 'query', description: 'Code search query', required: true }
      ],
      options: [
        { flags: '--repo <owner/repo>', description: 'Limit to repository' },
        { flags: '--language <lang>', description: 'Filter by language' },
        { flags: '--path <path>', description: 'Filter by path' },
        { flags: '--extension <ext>', description: 'Filter by extension' },
        { flags: '--limit <limit>', description: 'Number of results', defaultValue: 30 }
      ]
    },
    {
      name: 'issues',
      description: 'Search issues and pull requests',
      category: 'project',
      arguments: [
        { name: 'query', description: 'Issue search query', required: true }
      ],
      options: [
        { flags: '--repo <owner/repo>', description: 'Limit to repository' },
        { flags: '--state <state>', description: 'Filter by state', defaultValue: 'open' },
        { flags: '--label <labels>', description: 'Filter by labels' },
        { flags: '--author <username>', description: 'Filter by author' },
        { flags: '--assignee <username>', description: 'Filter by assignee' },
        { flags: '--is <type>', description: 'Filter by type' },
        { flags: '--limit <limit>', description: 'Number of results', defaultValue: 30 }
      ]
    }
  ]
};
