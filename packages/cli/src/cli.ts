#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import * as dotenv from 'dotenv';
import fs from 'fs-extra';
import * as path from 'path';
import * as Sentry from '@sentry/node';
import * as readline from 'readline';

import { MonkeyCoderAPIClient } from './api-client.js';
import { ConfigManager } from './config.js';
import {
  readFileContent,
  writeFileContent,
  detectLanguage,
  formatResponse,
  formatError,
  formatProgress,
  validateFilePath,
  generateUUID,
} from './utils.js';
import { ExecuteRequest, CommandOptions, StreamEvent } from './types.js';
import { createAuthCommand, requireAuth } from './commands/auth.js';
import { createUsageCommand, createBillingCommand } from './commands/usage.js';
import { createMCPCommand } from './commands/mcp.js';

// Initialize Sentry for error tracking
if (process.env.SENTRY_DSN) {
  Sentry.init({
    dsn: process.env.SENTRY_DSN,
    tracesSampleRate: 1.0,
  });
  Sentry.setTag('context', 'CLI');
}

// Load environment variables
dotenv.config();

const program = new Command();
const config = new ConfigManager();

program
  .name('monkey-coder')
  .description('Monkey Coder CLI - AI-powered code generation and analysis')
  .version('1.0.0')
  .option('--api-key <key>', 'API key for authentication')
  .option('--base-url <url>', 'Base URL for the API', 'http://localhost:8000')
  .option('--config <path>', 'Path to configuration file')
  .option('--verbose', 'Enable verbose output')
  .hook('preAction', async thisCommand => {
    // Load custom config if specified
    const options = thisCommand.opts();
    if (options.config) {
      try {
        const customConfig = await fs.readJson(options.config);
        await config.update(customConfig);
      } catch (error) {
        console.error(
          chalk.red(`Warning: Could not load config file: ${error}`)
        );
      }
    }
  });

/**
 * Create API client with current configuration
 */
function createAPIClient(options: CommandOptions): MonkeyCoderAPIClient {
  const apiKey = options.apiKey || config.getApiKey() || '';
  const baseUrl = options.baseUrl || config.getBaseUrl();

  if (!apiKey) {
    console.warn(
      chalk.yellow('Warning: No API key provided. Some features may not work.')
    );
  }

  return new MonkeyCoderAPIClient(baseUrl, apiKey);
}

/**
 * Build execution request from options
 */
async function buildExecuteRequest(
  taskType: string,
  prompt: string,
  files: string[],
  options: CommandOptions
): Promise<ExecuteRequest> {
  const fileData = [];

  // Read file contents if provided
  for (const filePath of files) {
    try {
      await validateFilePath(filePath);
      const content = await readFileContent(filePath);
      const language = detectLanguage(filePath);
      fileData.push({
        path: filePath,
        content,
        type: language,
      });
    } catch (error) {
      throw new Error(`Failed to read file ${filePath}: ${error}`);
    }
  }

  return {
    task_id: generateUUID(),
    task_type: taskType as any,
    prompt,
    files: fileData.length > 0 ? fileData : undefined,
    context: {
      user_id: 'cli-user',
      session_id: generateUUID(),
      environment: 'cli',
      timeout: options.timeout || config.getDefaultTimeout(),
      max_tokens: 4096,
      temperature: options.temperature || config.getDefaultTemperature(),
    },
    superclause_config: {
      persona: (options.persona || config.getDefaultPersona()) as any,
      slash_commands: [],
      context_window: 32768,
      use_markdown_spec: true,
    },
    preferred_providers: options.provider
      ? [options.provider]
      : [config.getDefaultProvider()],
    model_preferences: options.model
      ? { [options.provider || config.getDefaultProvider()]: options.model }
      : {},
  };
}

// Command: implement
program
  .command('implement')
  .description('Generate code implementation based on requirements')
  .argument('<prompt>', 'Implementation requirements or description')
  .argument('[files...]', 'Input files to analyze (optional)')
  .option('-o, --output <file>', 'Output file path')
  .option('-l, --language <lang>', 'Target programming language')
  .option('-p, --persona <persona>', 'AI persona to use', 'developer')
  .option('--model <model>', 'AI model to use')
  .option('--provider <provider>', 'AI provider to use')
  .option('-t, --temperature <temp>', 'Model temperature (0.0-2.0)', parseFloat)
  .option('--timeout <seconds>', 'Request timeout in seconds', parseInt)
  .option('--stream', 'Enable streaming output')
  .action(async (prompt: string, files: string[], options: CommandOptions) => {
    try {
      const client = createAPIClient(options);
      const request = await buildExecuteRequest(
        'code_generation',
        prompt,
        files,
        options
      );

      if (options.stream) {
        const spinner = ora('Starting implementation...').start();

        const response = await client.executeStream(
          request,
          (event: StreamEvent) => {
            switch (event.type) {
              case 'start':
                spinner.text = 'Implementation started';
                break;
              case 'progress':
                if (event.progress) {
                  spinner.text = formatProgress(
                    event.progress.step,
                    event.progress.percentage,
                    event.progress.metadata
                  );
                }
                break;
              case 'result':
                spinner.succeed('Implementation completed');
                break;
              case 'error':
                spinner.fail('Implementation failed');
                console.error(
                  formatError(event.error?.message || 'Unknown error')
                );
                break;
            }
          }
        );

        console.log(formatResponse(response));

        // Save output if specified
        if (options.output && response.result?.result) {
          await writeFileContent(options.output, response.result.result);
          console.log(chalk.green(`✓ Output saved to ${options.output}`));
        }
      } else {
        const spinner = ora('Generating implementation...').start();
        const response = await client.execute(request);
        spinner.stop();

        console.log(formatResponse(response));

        // Save output if specified
        if (options.output && response.result?.result) {
          await writeFileContent(options.output, response.result.result);
          console.log(chalk.green(`✓ Output saved to ${options.output}`));
        }
      }
    } catch (error: any) {
      console.error(formatError(error));
      process.exit(1);
    }
  });

// Command: analyze
program
  .command('analyze')
  .description('Analyze code for quality, security, and performance issues')
  .argument('<files...>', 'Files to analyze')
  .option(
    '-t, --type <type>',
    'Analysis type (quality, security, performance)',
    'quality'
  )
  .option('-p, --persona <persona>', 'AI persona to use', 'reviewer')
  .option('-o, --output <file>', 'Output file path for analysis report')
  .option('--model <model>', 'AI model to use')
  .option('--provider <provider>', 'AI provider to use')
  .option('--stream', 'Enable streaming output')
  .action(async (files: string[], options: CommandOptions) => {
    try {
      const client = createAPIClient(options);
      const prompt = `Perform a ${options.type} analysis of the provided code files. Provide detailed feedback, suggestions for improvement, and highlight any issues found.`;
      const request = await buildExecuteRequest(
        'code_analysis',
        prompt,
        files,
        options
      );

      // Override persona for analysis
      request.superclause_config.persona =
        (options.persona as any) || 'reviewer';

      if (options.stream) {
        const spinner = ora('Starting code analysis...').start();

        const response = await client.executeStream(
          request,
          (event: StreamEvent) => {
            switch (event.type) {
              case 'start':
                spinner.text = 'Analysis started';
                break;
              case 'progress':
                if (event.progress) {
                  spinner.text = formatProgress(
                    event.progress.step,
                    event.progress.percentage
                  );
                }
                break;
              case 'result':
                spinner.succeed('Analysis completed');
                break;
              case 'error':
                spinner.fail('Analysis failed');
                console.error(
                  formatError(event.error?.message || 'Unknown error')
                );
                break;
            }
          }
        );

        console.log(formatResponse(response));

        // Save output if specified
        if (options.output && response.result?.result) {
          await writeFileContent(options.output, response.result.result);
          console.log(
            chalk.green(`✓ Analysis report saved to ${options.output}`)
          );
        }
      } else {
        const spinner = ora('Analyzing code...').start();
        const response = await client.execute(request);
        spinner.stop();

        console.log(formatResponse(response));

        // Save output if specified
        if (options.output && response.result?.result) {
          await writeFileContent(options.output, response.result.result);
          console.log(
            chalk.green(`✓ Analysis report saved to ${options.output}`)
          );
        }
      }
    } catch (error: any) {
      console.error(formatError(error));
      process.exit(1);
    }
  });

// Command: build
program
  .command('build')
  .description('Build and optimize code architecture')
  .argument('<prompt>', 'Build requirements or architecture description')
  .argument('[files...]', 'Input files to build upon (optional)')
  .option('-o, --output <dir>', 'Output directory for built files')
  .option('-p, --persona <persona>', 'AI persona to use', 'architect')
  .option('--model <model>', 'AI model to use')
  .option('--provider <provider>', 'AI provider to use')
  .option('--stream', 'Enable streaming output')
  .action(async (prompt: string, files: string[], options: CommandOptions) => {
    try {
      const client = createAPIClient(options);
      const request = await buildExecuteRequest(
        'custom',
        prompt,
        files,
        options
      );

      // Override persona for building
      request.superclause_config.persona = 'architect';
      request.superclause_config.custom_instructions =
        'Focus on building robust, scalable, and maintainable code architecture.';

      if (options.stream) {
        const spinner = ora('Starting build...').start();

        const response = await client.executeStream(
          request,
          (event: StreamEvent) => {
            switch (event.type) {
              case 'start':
                spinner.text = 'Build started';
                break;
              case 'progress':
                if (event.progress) {
                  spinner.text = formatProgress(
                    event.progress.step,
                    event.progress.percentage
                  );
                }
                break;
              case 'result':
                spinner.succeed('Build completed');
                break;
              case 'error':
                spinner.fail('Build failed');
                console.error(
                  formatError(event.error?.message || 'Unknown error')
                );
                break;
            }
          }
        );

        console.log(formatResponse(response));

        // Handle multiple output files if artifacts are generated
        if (options.output && response.result?.artifacts) {
          await fs.ensureDir(options.output);
          for (const artifact of response.result.artifacts) {
            if (artifact.content && artifact.filename) {
              const filePath = path.join(options.output, artifact.filename);
              await writeFileContent(filePath, artifact.content);
              console.log(chalk.green(`✓ Created ${filePath}`));
            }
          }
        }
      } else {
        const spinner = ora('Building...').start();
        const response = await client.execute(request);
        spinner.stop();

        console.log(formatResponse(response));

        // Handle multiple output files if artifacts are generated
        if (options.output && response.result?.artifacts) {
          await fs.ensureDir(options.output);
          for (const artifact of response.result.artifacts) {
            if (artifact.content && artifact.filename) {
              const filePath = path.join(options.output, artifact.filename);
              await writeFileContent(filePath, artifact.content);
              console.log(chalk.green(`✓ Created ${filePath}`));
            }
          }
        }
      }
    } catch (error: any) {
      console.error(formatError(error));
      process.exit(1);
    }
  });

// Command: test
program
  .command('test')
  .description('Generate tests for code files')
  .argument('<files...>', 'Files to generate tests for')
  .option('-o, --output <dir>', 'Output directory for test files')
  .option('-f, --framework <framework>', 'Testing framework to use')
  .option('-p, --persona <persona>', 'AI persona to use', 'tester')
  .option('--model <model>', 'AI model to use')
  .option('--provider <provider>', 'AI provider to use')
  .option('--stream', 'Enable streaming output')
  .action(async (files: string[], options: CommandOptions) => {
    try {
      const client = createAPIClient(options);
      const frameworkInstruction = options.framework
        ? ` using ${options.framework}`
        : '';
      const prompt = `Generate comprehensive unit tests for the provided code files${frameworkInstruction}. Include edge cases, error handling, and mock dependencies where appropriate.`;
      const request = await buildExecuteRequest(
        'testing',
        prompt,
        files,
        options
      );

      // Override persona for testing
      request.superclause_config.persona = 'tester';

      if (options.stream) {
        const spinner = ora('Generating tests...').start();

        const response = await client.executeStream(
          request,
          (event: StreamEvent) => {
            switch (event.type) {
              case 'start':
                spinner.text = 'Test generation started';
                break;
              case 'progress':
                if (event.progress) {
                  spinner.text = formatProgress(
                    event.progress.step,
                    event.progress.percentage
                  );
                }
                break;
              case 'result':
                spinner.succeed('Test generation completed');
                break;
              case 'error':
                spinner.fail('Test generation failed');
                console.error(
                  formatError(event.error?.message || 'Unknown error')
                );
                break;
            }
          }
        );

        console.log(formatResponse(response));

        // Save test files if specified
        if (options.output && response.result?.artifacts) {
          await fs.ensureDir(options.output);
          for (const artifact of response.result.artifacts) {
            if (artifact.content && artifact.filename) {
              const filePath = path.join(options.output, artifact.filename);
              await writeFileContent(filePath, artifact.content);
              console.log(chalk.green(`✓ Generated test file ${filePath}`));
            }
          }
        }
      } else {
        const spinner = ora('Generating tests...').start();
        const response = await client.execute(request);
        spinner.stop();

        console.log(formatResponse(response));

        // Save test files if specified
        if (options.output && response.result?.artifacts) {
          await fs.ensureDir(options.output);
          for (const artifact of response.result.artifacts) {
            if (artifact.content && artifact.filename) {
              const filePath = path.join(options.output, artifact.filename);
              await writeFileContent(filePath, artifact.content);
              console.log(chalk.green(`✓ Generated test file ${filePath}`));
            }
          }
        }
      }
    } catch (error: any) {
      console.error(formatError(error));
      process.exit(1);
    }
  });

// Command: config
program
  .command('config')
  .description('Manage CLI configuration')
  .addCommand(
    new Command('set')
      .description('Set configuration value')
      .argument('<key>', 'Configuration key')
      .argument('<value>', 'Configuration value')
      .action(async (key: string, value: string) => {
        try {
          config.set(key as any, value);
          await config.saveConfig();
          console.log(chalk.green(`✓ Set ${key} = ${value}`));
        } catch (error: any) {
          console.error(formatError(error));
          process.exit(1);
        }
      })
  )
  .addCommand(
    new Command('get')
      .description('Get configuration value')
      .argument('<key>', 'Configuration key')
      .action((key: string) => {
        try {
          const value = config.get(key as any);
          console.log(value !== undefined ? value : chalk.gray('(not set)'));
        } catch (error: any) {
          console.error(formatError(error));
          process.exit(1);
        }
      })
  )
  .addCommand(
    new Command('list')
      .description('List all configuration values')
      .action(() => {
        try {
          const allConfig = config.getAll();
          console.log(chalk.cyan('Current configuration:'));
          Object.entries(allConfig).forEach(([key, value]) => {
            console.log(`  ${key}: ${value}`);
          });
        } catch (error: any) {
          console.error(formatError(error));
          process.exit(1);
        }
      })
  )
  .addCommand(
    new Command('reset')
      .description('Reset configuration to defaults')
      .action(async () => {
        try {
          await config.reset();
          console.log(chalk.green('✓ Configuration reset to defaults'));
        } catch (error: any) {
          console.error(formatError(error));
          process.exit(1);
        }
      })
  );

// Command: health
program
  .command('health')
  .description('Check API server health')
  .action(async (options: CommandOptions) => {
    try {
      const client = createAPIClient(options);
      const spinner = ora('Checking server health...').start();

      const health = await client.healthCheck();
      spinner.stop();

      console.log(chalk.green('✓ Server is healthy'));
      console.log(`Status: ${health.status}`);
      console.log(`Version: ${health.version}`);
      console.log('Components:');
      Object.entries(health.components).forEach(([name, status]) => {
        const statusColor = status === 'active' ? chalk.green : chalk.red;
        console.log(`  ${name}: ${statusColor(status)}`);
      });
    } catch (error: any) {
      console.error(formatError(error));
      process.exit(1);
    }
  });

// Error handling
process.on('uncaughtException', error => {
  console.error(formatError(`Uncaught exception: ${error.message}`));
  process.exit(1);
});

process.on('unhandledRejection', reason => {
  console.error(formatError(`Unhandled rejection: ${reason}`));
  process.exit(1);
});

// Command: chat
program
  .command('chat')
  .description('Start an interactive chat with the AI')
  .option('-p, --persona <persona>', 'AI persona to use', 'assistant')
  .option('--model <model>', 'AI model to use')
  .option('--provider <provider>', 'AI provider to use')
  .option('-t, --temperature <temp>', 'Model temperature (0.0-2.0)', parseFloat)
  .option('--stream', 'Enable streaming responses')
  .action(async (options: CommandOptions) => {
    try {
      const client = createAPIClient(options);
      const sessionId = generateUUID();

      console.log(chalk.green('🐒 Monkey Coder Chat'));
      console.log(
        chalk.gray(
          'Type your message and press Enter. Type "exit" or "quit" to leave.'
        )
      );
      console.log(chalk.gray('Use Ctrl+C to exit at any time.'));
      console.log(chalk.gray(`Persona: ${options.persona || 'assistant'}`));
      console.log('');

      const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
        prompt: chalk.blue('You: '),
      });

      rl.prompt();

      rl.on('line', async line => {
        const input = line.trim();

        if (!input) {
          rl.prompt();
          return;
        }

        if (input.toLowerCase() === 'exit' || input.toLowerCase() === 'quit') {
          rl.close();
          return;
        }

        try {
          const spinner = ora('AI is thinking...').start();

          const request = await buildExecuteRequest('chat', input, [], {
            ...options,
            persona: options.persona || 'assistant',
          });

          // Use the same session ID for conversation continuity
          request.context.session_id = sessionId;

          let response;
          if (options.stream) {
            response = await client.executeStream(
              request,
              (event: StreamEvent) => {
                if (event.type === 'progress' && event.data) {
                  spinner.text = `AI is responding: ${event.data.slice(0, 50)}...`;
                }
              }
            );
          } else {
            response = await client.execute(request);
          }

          spinner.stop();
          console.log(
            chalk.cyan('🤖 AI:'),
            response.result?.result || 'No response received'
          );
        } catch (error: any) {
          console.error(chalk.red('Error:'), error.message);
        }

        console.log('');
        rl.prompt();
      }).on('close', () => {
        console.log('');
        console.log(chalk.green('Thanks for chatting! Goodbye! 👋'));
        process.exit(0);
      });

      // Handle Ctrl+C gracefully
      rl.on('SIGINT', () => {
        console.log('');
        console.log(chalk.yellow('Chat interrupted. Goodbye! 👋'));
        process.exit(0);
      });
    } catch (error: any) {
      console.error(formatError(error));
      process.exit(1);
    }
  });

// Add authentication commands
program.addCommand(createAuthCommand(config));

// Add usage command
program.addCommand(createUsageCommand(config));

// Add billing command  
program.addCommand(createBillingCommand(config));

// Add MCP command
program.addCommand(createMCPCommand(config));

// Require authentication for main commands
const authRequiredCommands = ['implement', 'analyze', 'build', 'test', 'chat'];

program.hook('preSubcommand', async (thisCommand, actionCommand) => {
  if (authRequiredCommands.includes(actionCommand.name()) && !actionCommand.opts().apiKey) {
    await requireAuth(config);
  }
});

// Parse command line arguments
program.parse();
