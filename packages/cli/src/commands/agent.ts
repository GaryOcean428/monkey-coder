/**
 * Agent command - Local-first autonomous agent mode
 * 
 * Provides CLI interface for autonomous coding tasks with local tool execution.
 */

import { Command } from 'commander';
import chalk from 'chalk';
import { AgentRunner } from '../agent-runner.js';
import { ConfigManager } from '../config.js';

export function createAgentCommand(config: ConfigManager): Command {
  return new Command('agent')
    .description('Start local AI agent for autonomous coding tasks')
    .option('-t, --task <description>', 'Task to complete')
    .option('-l, --local', 'Local-only mode (no backend API)', false)
    .option('--no-approval', 'Skip approval prompts (dangerous)')
    .option('-c, --continue', 'Continue previous session', false)
    .option('-m, --model <model>', 'AI model to use', 'claude-sonnet-4')
    .option('--base-url <url>', 'Backend API base URL')
    .option('--api-key <key>', 'API key for authentication')
    .option('--max-iterations <n>', 'Maximum agent iterations', parseInt, 20)
    .option('--sandbox <mode>', 'Sandbox mode (none|spawn|docker)', 'spawn')
    .option('--docker', 'Use Docker sandboxing (shorthand for --sandbox docker)')
    .action(async (options) => {
      try {
        // Get configuration
        const apiKey = options.apiKey || config.getApiKey() || process.env.MONKEY_CODER_API_KEY || '';
        const baseUrl = options.baseUrl || config.getBaseUrl();

        if (!apiKey && !options.local) {
          console.error(chalk.red('✗ No API key provided'));
          console.error(chalk.gray('Set MONKEY_CODER_API_KEY or use --api-key'));
          console.error(chalk.gray('Or use --local for local-only mode (limited functionality)'));
          process.exit(1);
        }

        // Determine sandbox mode
        const sandboxMode = options.docker ? 'docker' : (options.sandbox || 'spawn');

        // Create agent runner
        const agent = new AgentRunner({
          localOnly: options.local,
          requireApproval: options.approval !== false,
          continueSession: options.continue,
          model: options.model,
          baseUrl,
          apiKey,
          maxIterations: options.maxIterations,
          sandboxMode,
        });

        // Run task or start interactive mode
        if (options.task) {
          await agent.runTask(options.task);
        } else {
          await agent.startInteractive();
        }
      } catch (error: any) {
        console.error(chalk.red('✗ Agent failed:'), error.message);
        process.exit(1);
      }
    });
}
