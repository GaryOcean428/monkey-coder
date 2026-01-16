/**
 * Agent command - Local agent mode for autonomous coding
 */

import { Command } from 'commander';
import chalk from 'chalk';
import { AgentLoop } from '../agent/agent-loop.js';
import { AgentConfig, AgentMode, AIProvider } from '../agent/types.js';

export function createAgentCommand(): Command {
  const command = new Command('agent');

  command
    .description('Start local agent mode for autonomous coding')
    .argument('<prompt>', 'Task description for the agent to accomplish')
    .option(
      '-m, --mode <mode>',
      'Agent mode: local (offline), hybrid (local tools + cloud AI), cloud (current behavior)',
      'hybrid'
    )
    .option(
      '--model <model>',
      'AI model to use (provider-specific)',
      'claude-sonnet-4-20250514'
    )
    .option(
      '--provider <provider>',
      'AI provider: anthropic, openai, google',
      'anthropic'
    )
    .option(
      '--auto-approve',
      'Auto-approve destructive tool executions (use with caution)',
      false
    )
    .option(
      '--max-iterations <n>',
      'Maximum number of agent iterations',
      '10'
    )
    .option(
      '--temperature <temp>',
      'Model temperature (0.0-1.0)',
      '0.7'
    )
    .option(
      '--max-tokens <tokens>',
      'Maximum tokens in response',
      '8192'
    )
    .action(async (prompt: string, options) => {
      try {
        // Validate mode
        const mode = options.mode as AgentMode;
        if (!['local', 'hybrid', 'cloud'].includes(mode)) {
          console.error(chalk.red('Invalid mode. Must be: local, hybrid, or cloud'));
          process.exit(1);
        }

        // Validate provider
        const provider = options.provider as AIProvider;
        if (!['openai', 'anthropic', 'google'].includes(provider)) {
          console.error(chalk.red('Invalid provider. Must be: openai, anthropic, or google'));
          process.exit(1);
        }

        // Check API key based on provider
        const apiKeyEnvVars: Record<AIProvider, string> = {
          anthropic: 'ANTHROPIC_API_KEY',
          openai: 'OPENAI_API_KEY',
          google: 'GOOGLE_API_KEY',
        };

        const requiredEnvVar = apiKeyEnvVars[provider];
        if (!process.env[requiredEnvVar]) {
          console.error(chalk.red(`Missing ${requiredEnvVar} environment variable`));
          console.log(chalk.yellow(`\nSet it with: export ${requiredEnvVar}=your-key-here`));
          process.exit(1);
        }

        // Build config
        const config: AgentConfig = {
          mode,
          model: options.model,
          provider,
          maxIterations: parseInt(options.maxIterations, 10),
          autoApprove: options.autoApprove,
          temperature: parseFloat(options.temperature),
          maxTokens: parseInt(options.maxTokens, 10),
        };

        // Display configuration
        console.log(chalk.bold('\n🐵 Monkey Coder Agent Mode\n'));
        console.log(chalk.gray('Configuration:'));
        console.log(chalk.gray(`  Mode: ${config.mode}`));
        console.log(chalk.gray(`  Provider: ${config.provider}`));
        console.log(chalk.gray(`  Model: ${config.model}`));
        console.log(chalk.gray(`  Max Iterations: ${config.maxIterations}`));
        console.log(chalk.gray(`  Auto-approve: ${config.autoApprove}`));
        console.log(chalk.gray(`  Working Directory: ${process.cwd()}\n`));

        // Warn about auto-approve
        if (config.autoApprove) {
          console.log(chalk.yellow('⚠️  Auto-approve is enabled. Agent will execute destructive operations without confirmation.\n'));
        }

        // Initialize and run agent
        const agent = new AgentLoop();
        await agent.initialize(config);

        console.log(chalk.cyan('📋 Task:'), prompt);
        console.log(chalk.gray('─'.repeat(60)));

        await agent.run(prompt, config);

        console.log(chalk.gray('\n' + '─'.repeat(60)));
        console.log(chalk.green('✅ Agent execution completed'));

        await agent.cleanup();

      } catch (error) {
        console.error(chalk.red('\n❌ Agent error:'), error);
        process.exit(1);
      }
    });

  return command;
}
