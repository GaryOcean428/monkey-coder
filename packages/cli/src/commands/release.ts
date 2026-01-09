/**
 * Release commands for Monkey Coder CLI
 * Manage GitHub releases
 */

import { Command } from 'commander';
import chalk from 'chalk';
import Table from 'cli-table3';
import open from 'open';
import { ConfigManager } from '../config.js';
import { formatError } from '../utils.js';
import { CommandDefinition } from './registry.js';
import { getGitHubClient } from '../github-client.js';

/**
 * Create the release command group
 */
export function createReleaseCommand(config: ConfigManager): Command {
  const release = new Command('release')
    .description('Manage releases');

  /**
   * Parse owner/repo from option or error
   */
  function parseOwnerRepo(repoOption?: string): { owner: string; repo: string } {
    if (!repoOption) {
      console.error(chalk.red('Error: --repo option is required (format: owner/repo)'));
      console.log(chalk.gray('Example: --repo microsoft/vscode'));
      process.exit(1);
    }

    const parts = repoOption.split('/');
    if (parts.length !== 2) {
      console.error(chalk.red('Error: Invalid repository format'));
      console.log(chalk.gray('Expected format: owner/repo'));
      console.log(chalk.gray('Example: --repo microsoft/vscode'));
      process.exit(1);
    }

    return { owner: parts[0]!, repo: parts[1]! };
  }

  // release create
  release
    .command('create')
    .description('Create a new release')
    .argument('<tag>', 'Release tag (e.g., v1.0.0)')
    .option('-t, --title <title>', 'Release title')
    .option('-b, --body <body>', 'Release description')
    .option('--draft', 'Create as draft')
    .option('--prerelease', 'Mark as pre-release')
    .option('--target <branch>', 'Target branch or commit', 'main')
    .option('--repo <owner/repo>', 'Repository (required)')
    .option('--ai', 'Generate release notes with AI (not yet implemented)')
    .addHelpText('after', `
Examples:
  $ monkey release create v1.0.0 --title "Version 1.0.0" --repo owner/repo
    Create a release for tag v1.0.0

  $ monkey release create v1.1.0-beta --prerelease --draft --repo owner/repo
    Create a draft pre-release
`)
    .action(async (tag: string, options: any) => {
      try {
        const { owner, repo } = parseOwnerRepo(options.repo);

        if (options.ai) {
          console.log(chalk.yellow('⚠️  AI-generated release notes not yet implemented'));
          console.log(chalk.gray('Please provide --body or --title manually\n'));
        }

        console.log(chalk.blue(`📦 Creating release: ${tag} for ${owner}/${repo}`));

        const github = getGitHubClient();
        const release = await github.createRelease(owner, repo, {
          tag_name: tag,
          name: options.title || tag,
          body: options.body || '',
          draft: options.draft || false,
          prerelease: options.prerelease || false,
          target_commitish: options.target,
        });

        console.log(chalk.green(`\n✓ Release created successfully!`));
        console.log(`Tag: ${chalk.bold(release.tag_name)}`);
        console.log(`URL: ${chalk.cyan(release.html_url)}`);

        if (release.draft) {
          console.log(chalk.yellow('\nNote: This is a draft release and is not visible to the public'));
        }

        // Show rate limit info
        const rateLimit = github.getRateLimitInfo();
        if (rateLimit) {
          console.log(chalk.gray(`\nAPI: ${rateLimit.remaining}/${rateLimit.limit} requests remaining`));
        }
      } catch (error: any) {
        console.error(formatError(error.message || 'Release creation failed'));
        process.exit(1);
      }
    });

  // release list
  release
    .command('list')
    .description('List releases')
    .alias('ls')
    .option('--limit <limit>', 'Number of releases to show', parseInt, 30)
    .option('--repo <owner/repo>', 'Repository (defaults to current)')
    .addHelpText('after', `
Examples:
  $ monkey release list
    List releases for current repository

  $ monkey release list --limit 10
    List last 10 releases

  $ monkey release list --repo owner/repo
    List releases for specific repository
`)
    .action(async (options: any) => {
      try {
        const { owner, repo } = parseOwnerRepo(options.repo);
        
        console.log(chalk.blue(`📋 Listing releases for ${owner}/${repo}...`));
        
        const github = getGitHubClient();
        const releases = await github.listReleases(owner, repo, {
          per_page: options.limit,
        });

        if (releases.length === 0) {
          console.log(chalk.yellow('\n No releases found'));
          return;
        }

        console.log(chalk.green(`\n✓ Found ${releases.length} releases\n`));

        const table = new Table({
          head: [chalk.cyan('Tag'), chalk.cyan('Name'), chalk.cyan('Published'), chalk.cyan('Type')],
          colWidths: [20, 40, 25, 15],
          wordWrap: true,
        });

        for (const release of releases) {
          const typeLabels = [];
          if (release.draft) typeLabels.push(chalk.yellow('draft'));
          if (release.prerelease) typeLabels.push(chalk.blue('prerelease'));
          const typeLabel = typeLabels.length > 0 ? typeLabels.join(', ') : chalk.gray('release');

          const publishedDate = release.published_at 
            ? new Date(release.published_at).toLocaleDateString()
            : chalk.gray('N/A');

          table.push([
            chalk.bold(release.tag_name),
            release.name || chalk.gray('Unnamed'),
            publishedDate,
            typeLabel,
          ]);
        }

        console.log(table.toString());
        
        // Show rate limit info
        const rateLimit = github.getRateLimitInfo();
        if (rateLimit) {
          console.log(chalk.gray(`\nAPI: ${rateLimit.remaining}/${rateLimit.limit} requests remaining`));
        }
      } catch (error: any) {
        console.error(formatError(error.message || 'Release listing failed'));
        process.exit(1);
      }
    });

  // release view
  release
    .command('view')
    .description('View release details')
    .argument('<tag>', 'Release tag to view')
    .option('--web', 'Open in web browser')
    .option('--repo <owner/repo>', 'Repository (defaults to current)')
    .addHelpText('after', `
Examples:
  $ monkey release view v1.0.0
    View release details for v1.0.0

  $ monkey release view latest
    View latest release

  $ monkey release view v1.0.0 --web
    Open release in browser
`)
    .action(async (tag: string, options: any) => {
      try {
        const { owner, repo } = parseOwnerRepo(options.repo);
        
        const github = getGitHubClient();
        const release = tag === 'latest'
          ? await github.getLatestRelease(owner, repo)
          : await github.getReleaseByTag(owner, repo, tag);

        if (options.web) {
          console.log(chalk.blue('🌐 Opening in browser...'));
          await open(release.html_url);
          return;
        }

        console.log(chalk.green(`\n✓ Release: ${release.tag_name}\n`));
        console.log(chalk.bold(`Name: ${release.name || chalk.gray('Unnamed')}`));
        console.log(`Published: ${release.published_at ? new Date(release.published_at).toLocaleString() : chalk.gray('N/A')}`);
        console.log(`Draft: ${release.draft ? chalk.yellow('Yes') : 'No'}`);
        console.log(`Prerelease: ${release.prerelease ? chalk.blue('Yes') : 'No'}`);
        console.log(`URL: ${chalk.cyan(release.html_url)}`);

        if (release.body) {
          console.log(chalk.bold('\nDescription:'));
          console.log(release.body);
        }

        if (release.assets && release.assets.length > 0) {
          console.log(chalk.bold(`\nAssets (${release.assets.length}):`));
          const table = new Table({
            head: [chalk.cyan('Name'), chalk.cyan('Size'), chalk.cyan('Downloads')],
            colWidths: [40, 15, 12],
          });

          for (const asset of release.assets) {
            const sizeInMB = (asset.size / 1024 / 1024).toFixed(2);
            table.push([
              asset.name,
              `${sizeInMB} MB`,
              asset.download_count?.toLocaleString() || '0',
            ]);
          }

          console.log(table.toString());
        }

        // Show rate limit info
        const rateLimit = github.getRateLimitInfo();
        if (rateLimit) {
          console.log(chalk.gray(`\nAPI: ${rateLimit.remaining}/${rateLimit.limit} requests remaining`));
        }
      } catch (error: any) {
        console.error(formatError(error.message || 'Release view failed'));
        process.exit(1);
      }
    });

  // release download
  release
    .command('download')
    .description('Download release assets')
    .argument('<tag>', 'Release tag')
    .option('--asset <pattern>', 'Asset name pattern (supports wildcards)')
    .option('--output <dir>', 'Output directory', '.')
    .option('--repo <owner/repo>', 'Repository (defaults to current)')
    .addHelpText('after', `
Examples:
  $ monkey release download v1.0.0
    Download all assets from v1.0.0

  $ monkey release download v1.0.0 --asset "*.tar.gz"
    Download only .tar.gz files

  $ monkey release download latest --output ./downloads
    Download latest release to ./downloads
`)
    .action(async (tag: string, options: any) => {
      try {
        console.log(chalk.blue(`⬇️  Downloading release: ${tag}`));
        if (options.asset) {
          console.log(chalk.gray(`Asset pattern: ${options.asset}`));
        }
        console.log(chalk.gray(`Output: ${options.output}`));

        console.log(chalk.yellow('\n⚠️  Release download not yet implemented'));
        console.log(chalk.gray('This will use GitHub Releases API in a future update'));
      } catch (error: any) {
        console.error(formatError(error.message || 'Release download failed'));
        process.exit(1);
      }
    });

  // release delete
  release
    .command('delete')
    .description('Delete a release')
    .argument('<tag>', 'Release tag to delete')
    .option('--force', 'Skip confirmation')
    .option('--repo <owner/repo>', 'Repository (defaults to current)')
    .addHelpText('after', `
Examples:
  $ monkey release delete v1.0.0
    Delete release v1.0.0 (with confirmation)

  $ monkey release delete v1.0.0 --force
    Delete without confirmation
`)
    .action(async (tag: string, options: any) => {
      try {
        console.log(chalk.red(`🗑️  Deleting release: ${tag}`));
        
        if (!options.force) {
          console.log(chalk.yellow('(Confirmation would be requested here)'));
        }

        console.log(chalk.yellow('\n⚠️  Release deletion not yet implemented'));
        console.log(chalk.gray('This will use GitHub Releases API in a future update'));
      } catch (error: any) {
        console.error(formatError(error.message || 'Release deletion failed'));
        process.exit(1);
      }
    });

  return release;
}

/**
 * Command definition for registry
 */
export const releaseCommandDefinition: CommandDefinition = {
  name: 'release',
  description: 'Manage releases',
  category: 'project',
  subcommands: [
    {
      name: 'create',
      description: 'Create a new release',
      category: 'project',
      arguments: [
        { name: 'tag', description: 'Release tag', required: true }
      ],
      options: [
        { flags: '-t, --title <title>', description: 'Release title' },
        { flags: '-b, --body <body>', description: 'Release description' },
        { flags: '--draft', description: 'Create as draft' },
        { flags: '--prerelease', description: 'Mark as pre-release' },
        { flags: '--target <branch>', description: 'Target branch', defaultValue: 'main' },
        { flags: '--ai', description: 'Generate with AI' }
      ]
    },
    {
      name: 'list',
      aliases: ['ls'],
      description: 'List releases',
      category: 'project',
      options: [
        { flags: '--limit <limit>', description: 'Number to show', defaultValue: 30 },
        { flags: '--repo <owner/repo>', description: 'Repository' }
      ]
    },
    {
      name: 'view',
      description: 'View release details',
      category: 'project',
      arguments: [
        { name: 'tag', description: 'Release tag', required: true }
      ],
      options: [
        { flags: '--web', description: 'Open in browser' },
        { flags: '--repo <owner/repo>', description: 'Repository' }
      ]
    },
    {
      name: 'download',
      description: 'Download release assets',
      category: 'project',
      arguments: [
        { name: 'tag', description: 'Release tag', required: true }
      ],
      options: [
        { flags: '--asset <pattern>', description: 'Asset pattern' },
        { flags: '--output <dir>', description: 'Output directory', defaultValue: '.' },
        { flags: '--repo <owner/repo>', description: 'Repository' }
      ]
    },
    {
      name: 'delete',
      description: 'Delete a release',
      category: 'project',
      arguments: [
        { name: 'tag', description: 'Release tag', required: true }
      ],
      options: [
        { flags: '--force', description: 'Skip confirmation' },
        { flags: '--repo <owner/repo>', description: 'Repository' }
      ]
    }
  ]
};
