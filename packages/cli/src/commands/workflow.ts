/**
 * Workflow commands for Monkey Coder CLI
 * Manage GitHub Actions workflows
 */

import { Command } from 'commander';
import chalk from 'chalk';
import Table from 'cli-table3';
import open from 'open';

import { ConfigManager } from '../config.js';
import { formatError } from '../utils.js';
import { getGitHubClient } from '../github-client.js';

import { CommandDefinition } from './registry.js';

/**
 * Create the workflow command group
 */
export function createWorkflowCommand(config: ConfigManager): Command {
  const workflow = new Command('workflow')
    .description('Manage GitHub Actions workflows')
    .alias('wf');

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

  // workflow list
  workflow
    .command('list')
    .description('List workflows')
    .alias('ls')
    .option('--repo <owner/repo>', 'Repository (required)')
    .option('--all', 'Show disabled workflows too')
    .addHelpText('after', `
Examples:
  $ monkey workflow list --repo owner/repo
    List all active workflows

  $ monkey workflow list --all --repo owner/repo
    List all workflows including disabled
`)
    .action(async (options: any) => {
      try {
        const { owner, repo } = parseOwnerRepo(options.repo);
        
        console.log(chalk.blue(`📋 Listing workflows for ${owner}/${repo}...`));
        
        const github = getGitHubClient();
        const result = await github.listWorkflows(owner, repo);

        const workflows = options.all 
          ? result.workflows
          : result.workflows.filter(w => w.state !== 'disabled_manually');

        if (workflows.length === 0) {
          console.log(chalk.yellow('\n No workflows found'));
          return;
        }

        console.log(chalk.green(`\n✓ Found ${workflows.length} workflows\n`));

        const table = new Table({
          head: [chalk.cyan('Name'), chalk.cyan('Path'), chalk.cyan('State')],
          colWidths: [40, 50, 15],
          wordWrap: true,
        });

        for (const wf of workflows) {
          const stateColor = wf.state === 'active' ? chalk.green : chalk.gray;
          table.push([
            chalk.bold(wf.name),
            wf.path,
            stateColor(wf.state),
          ]);
        }

        console.log(table.toString());
        
        // Show rate limit info
        const rateLimit = github.getRateLimitInfo();
        if (rateLimit) {
          console.log(chalk.gray(`\nAPI: ${rateLimit.remaining}/${rateLimit.limit} requests remaining`));
        }
      } catch (error: any) {
        console.error(formatError(error.message || 'Workflow listing failed'));
        process.exit(1);
      }
    });

  // workflow view
  workflow
    .command('view')
    .description('View workflow details')
    .argument('<workflow>', 'Workflow ID or name')
    .option('--repo <owner/repo>', 'Repository (defaults to current)')
    .option('--web', 'Open in web browser')
    .addHelpText('after', `
Examples:
  $ monkey workflow view ci.yml
    View CI workflow details

  $ monkey workflow view 12345
    View workflow by ID

  $ monkey workflow view ci.yml --web
    Open workflow in browser
`)
    .action(async (workflow: string, options: any) => {
      try {
        console.log(chalk.blue(`👀 Viewing workflow: ${workflow}`));
        
        if (options.web) {
          console.log(chalk.gray('Opening in browser...'));
        }

        console.log(chalk.yellow('\n⚠️  Workflow viewing not yet implemented'));
        console.log(chalk.gray('This will use GitHub Actions API in a future update'));
      } catch (error: any) {
        console.error(formatError(error.message || 'Workflow view failed'));
        process.exit(1);
      }
    });

  // workflow run
  workflow
    .command('run')
    .description('Trigger a workflow run')
    .argument('<workflow>', 'Workflow ID or name')
    .option('--ref <branch>', 'Git ref to run workflow on', 'main')
    .option('--input <key=value...>', 'Workflow inputs (can be specified multiple times)')
    .option('--repo <owner/repo>', 'Repository (defaults to current)')
    .addHelpText('after', `
Examples:
  $ monkey workflow run ci.yml
    Trigger CI workflow on main branch

  $ monkey workflow run deploy.yml --ref develop
    Trigger deploy workflow on develop branch

  $ monkey workflow run build.yml --input version=1.0.0 --input env=prod
    Trigger workflow with inputs
`)
    .action(async (workflow: string, options: any) => {
      try {
        console.log(chalk.blue(`▶️  Running workflow: ${workflow}`));
        console.log(chalk.gray(`Branch: ${options.ref}`));
        
        if (options.input) {
          console.log(chalk.gray(`Inputs: ${options.input}`));
        }

        console.log(chalk.yellow('\n⚠️  Workflow triggering not yet implemented'));
        console.log(chalk.gray('This will use GitHub Actions API in a future update'));
      } catch (error: any) {
        console.error(formatError(error.message || 'Workflow run failed'));
        process.exit(1);
      }
    });

  // workflow logs
  workflow
    .command('logs')
    .description('View workflow run logs')
    .argument('<run-id>', 'Workflow run ID')
    .option('--job <job>', 'Specific job name or ID')
    .option('--step <step>', 'Specific step number')
    .option('--repo <owner/repo>', 'Repository (defaults to current)')
    .option('--download', 'Download logs to file')
    .addHelpText('after', `
Examples:
  $ monkey workflow logs 12345
    View logs for workflow run

  $ monkey workflow logs 12345 --job build
    View logs for specific job

  $ monkey workflow logs 12345 --job build --step 3
    View logs for specific step

  $ monkey workflow logs 12345 --download
    Download all logs
`)
    .action(async (runId: string, options: any) => {
      try {
        console.log(chalk.blue(`📜 Viewing logs for run: ${runId}`));
        
        if (options.job) {
          console.log(chalk.gray(`Job: ${options.job}`));
        }
        if (options.step) {
          console.log(chalk.gray(`Step: ${options.step}`));
        }

        console.log(chalk.yellow('\n⚠️  Workflow logs viewing not yet implemented'));
        console.log(chalk.gray('This will use GitHub Actions API in a future update'));
      } catch (error: any) {
        console.error(formatError(error.message || 'Workflow logs failed'));
        process.exit(1);
      }
    });

  // workflow runs
  workflow
    .command('runs')
    .description('List workflow runs')
    .argument('[workflow]', 'Workflow ID or name (optional)')
    .option('--status <status>', 'Filter by status (completed, in_progress, queued)')
    .option('--branch <branch>', 'Filter by branch')
    .option('--limit <limit>', 'Number of runs to show', parseInt, 30)
    .option('--repo <owner/repo>', 'Repository (required)')
    .addHelpText('after', `
Examples:
  $ monkey workflow runs --repo owner/repo
    List recent workflow runs

  $ monkey workflow runs ci.yml --repo owner/repo
    List runs for specific workflow

  $ monkey workflow runs --status completed --limit 10 --repo owner/repo
    List last 10 completed runs

  $ monkey workflow runs --branch main --repo owner/repo
    List runs on main branch
`)
    .action(async (workflowId: string | undefined, options: any) => {
      try {
        const { owner, repo } = parseOwnerRepo(options.repo);

        if (workflowId) {
          console.log(chalk.blue(`📋 Listing runs for ${workflowId} in ${owner}/${repo}...`));
        } else {
          console.log(chalk.blue(`📋 Listing all workflow runs for ${owner}/${repo}...`));
        }

        const github = getGitHubClient();
        const result = await github.listWorkflowRuns(owner, repo, workflowId, {
          status: options.status as any,
          branch: options.branch,
          per_page: options.limit,
        });

        if (result.workflow_runs.length === 0) {
          console.log(chalk.yellow('\n No workflow runs found'));
          return;
        }

        console.log(chalk.green(`\n✓ Found ${result.total_count} runs (showing ${result.workflow_runs.length})\n`));

        const table = new Table({
          head: [chalk.cyan('Name'), chalk.cyan('Branch'), chalk.cyan('Status'), chalk.cyan('Conclusion'), chalk.cyan('Created')],
          colWidths: [30, 20, 15, 15, 20],
          wordWrap: true,
        });

        for (const run of result.workflow_runs) {
          let statusColor = chalk.gray;
          if (run.status === 'completed') {
            statusColor = run.conclusion === 'success' ? chalk.green : chalk.red;
          } else if (run.status === 'in_progress') {
            statusColor = chalk.yellow;
          }

          const conclusionText = run.conclusion || chalk.gray('-');
          const conclusionColor = run.conclusion === 'success' ? chalk.green 
            : run.conclusion === 'failure' ? chalk.red 
            : chalk.gray;

          table.push([
            chalk.bold(run.name),
            run.head_branch,
            statusColor(run.status),
            conclusionColor(conclusionText),
            new Date(run.created_at).toLocaleDateString(),
          ]);
        }

        console.log(table.toString());
        
        // Show rate limit info
        const rateLimit = github.getRateLimitInfo();
        if (rateLimit) {
          console.log(chalk.gray(`\nAPI: ${rateLimit.remaining}/${rateLimit.limit} requests remaining`));
        }
      } catch (error: any) {
        console.error(formatError(error.message || 'Workflow runs listing failed'));
        process.exit(1);
      }
    });

  // workflow disable
  workflow
    .command('disable')
    .description('Disable a workflow')
    .argument('<workflow>', 'Workflow ID or name')
    .option('--repo <owner/repo>', 'Repository (defaults to current)')
    .addHelpText('after', `
Examples:
  $ monkey workflow disable ci.yml
    Disable CI workflow
`)
    .action(async (workflow: string, options: any) => {
      try {
        console.log(chalk.red(`⏸️  Disabling workflow: ${workflow}`));

        console.log(chalk.yellow('\n⚠️  Workflow disabling not yet implemented'));
        console.log(chalk.gray('This will use GitHub Actions API in a future update'));
      } catch (error: any) {
        console.error(formatError(error.message || 'Workflow disable failed'));
        process.exit(1);
      }
    });

  // workflow enable
  workflow
    .command('enable')
    .description('Enable a workflow')
    .argument('<workflow>', 'Workflow ID or name')
    .option('--repo <owner/repo>', 'Repository (defaults to current)')
    .addHelpText('after', `
Examples:
  $ monkey workflow enable ci.yml
    Enable CI workflow
`)
    .action(async (workflow: string, options: any) => {
      try {
        console.log(chalk.green(`▶️  Enabling workflow: ${workflow}`));

        console.log(chalk.yellow('\n⚠️  Workflow enabling not yet implemented'));
        console.log(chalk.gray('This will use GitHub Actions API in a future update'));
      } catch (error: any) {
        console.error(formatError(error.message || 'Workflow enable failed'));
        process.exit(1);
      }
    });

  return workflow;
}

/**
 * Command definition for registry
 */
export const workflowCommandDefinition: CommandDefinition = {
  name: 'workflow',
  aliases: ['wf'],
  description: 'Manage GitHub Actions workflows',
  category: 'project',
  subcommands: [
    {
      name: 'list',
      aliases: ['ls'],
      description: 'List workflows',
      category: 'project',
      options: [
        { flags: '--repo <owner/repo>', description: 'Repository' },
        { flags: '--all', description: 'Show disabled workflows' }
      ]
    },
    {
      name: 'view',
      description: 'View workflow details',
      category: 'project',
      arguments: [
        { name: 'workflow', description: 'Workflow ID or name', required: true }
      ],
      options: [
        { flags: '--repo <owner/repo>', description: 'Repository' },
        { flags: '--web', description: 'Open in browser' }
      ]
    },
    {
      name: 'run',
      description: 'Trigger a workflow run',
      category: 'project',
      arguments: [
        { name: 'workflow', description: 'Workflow ID or name', required: true }
      ],
      options: [
        { flags: '--ref <branch>', description: 'Git ref', defaultValue: 'main' },
        { flags: '--input <key=value...>', description: 'Workflow inputs' },
        { flags: '--repo <owner/repo>', description: 'Repository' }
      ]
    },
    {
      name: 'logs',
      description: 'View workflow run logs',
      category: 'project',
      arguments: [
        { name: 'run-id', description: 'Workflow run ID', required: true }
      ],
      options: [
        { flags: '--job <job>', description: 'Specific job' },
        { flags: '--step <step>', description: 'Specific step' },
        { flags: '--repo <owner/repo>', description: 'Repository' },
        { flags: '--download', description: 'Download logs' }
      ]
    },
    {
      name: 'runs',
      description: 'List workflow runs',
      category: 'project',
      arguments: [
        { name: 'workflow', description: 'Workflow ID or name', required: false }
      ],
      options: [
        { flags: '--status <status>', description: 'Filter by status' },
        { flags: '--branch <branch>', description: 'Filter by branch' },
        { flags: '--limit <limit>', description: 'Number to show', defaultValue: 30 },
        { flags: '--repo <owner/repo>', description: 'Repository' }
      ]
    },
    {
      name: 'disable',
      description: 'Disable a workflow',
      category: 'project',
      arguments: [
        { name: 'workflow', description: 'Workflow ID or name', required: true }
      ],
      options: [
        { flags: '--repo <owner/repo>', description: 'Repository' }
      ]
    },
    {
      name: 'enable',
      description: 'Enable a workflow',
      category: 'project',
      arguments: [
        { name: 'workflow', description: 'Workflow ID or name', required: true }
      ],
      options: [
        { flags: '--repo <owner/repo>', description: 'Repository' }
      ]
    }
  ]
};
