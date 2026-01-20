#!/usr/bin/env node

// Trigger CI/CD pipeline for npm publishing
import * as path from 'path';
import * as readline from 'readline';

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import * as dotenv from 'dotenv';
import fs from 'fs-extra';
import * as Sentry from '@sentry/node';


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
import { validateTaskType, validatePersona } from './type-guards.js';
import { createAuthCommand, requireAuth } from './commands/auth.js';
import { createUsageCommand, createBillingCommand } from './commands/usage.js';
import { createMCPCommand } from './commands/mcp.js';
import { createMCPToolsCommand } from './commands/mcp-tools.js';
import { createRepoCommand } from './commands/repo.js';
import { createConfigCommand } from './commands/config.js';
import { createGitCommand } from './commands/git.js';
import { createPRCommand } from './commands/pr.js';
import { createIssueCommand } from './commands/issue.js';
import { createSearchCommand } from './commands/search.js';
import { createReleaseCommand } from './commands/release.js';
import { createWorkflowCommand } from './commands/workflow.js';
import { createSessionCommand } from './commands/session.js';
import { createInkChatCommand } from './commands/chat-ink.js';
import { createInkAgentCommand } from './commands/agent-ink.js';
import { registerCheckpointCommands } from './commands/checkpoint.js';
import { createAgentCommand } from './commands/agent.js';
import { printSplashSync } from './splash.js';
import { getSessionManager } from './session-manager.js';

// Read package version
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const packageJsonPath = join(__dirname, '../package.json');
const packageJson = JSON.parse(readFileSync(packageJsonPath, 'utf-8'));
const CLI_VERSION = packageJson.version;

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

// Show splash screen unless --no-splash is passed
const noSplashIndex = process.argv.indexOf('--no-splash');
if (noSplashIndex === -1) {
  printSplashSync();
}

program
  .name('monkey-coder')
  .description('Monkey Coder CLI - AI-powered code generation and analysis')
  .version(CLI_VERSION)
  .option('--api-key <key>', 'API key for authentication')
  .option('--base-url <url>', 'Base URL for the API', process.env.MONKEY_CODER_BASE_URL || 'http://localhost:8000')
  .option('--config <path>', 'Path to configuration file')
  .option('--verbose', 'Enable verbose output')
  .option('--no-splash', 'Disable splash screen')
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
 * Format session ID for display (truncate to 8 characters)
 */
function formatSessionId(sessionId: string): string {
  return sessionId.slice(0, 8);
}

/**
 * Generate a session name with timestamp
 */
function generateSessionName(): string {
  return `Chat ${new Date().toISOString().slice(0, 16)}`;
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
    task_type: validateTaskType(taskType),
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
    persona_config: {
      persona: validatePersona(options.persona || config.getDefaultPersona()),
      slash_commands: [],
      context_window: 32768,
      use_markdown_spec: true,
    },
    preferred_providers: options.provider
      ? [options.provider]
      : [config.getDefaultProvider()],
      // TODO: If model is provided without a provider, the default provider is used.
      // This might not be the user's intent. Consider adding a validation or warning.
      // Reference: Analysis document section on request-building.
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
      request.persona_config.persona = validatePersona(options.persona) || 'reviewer';

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
      request.persona_config.persona = 'architect';
      request.persona_config.custom_instructions =
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
      request.persona_config.persona = 'tester';

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

// Enhanced configuration command (replaced with new hierarchical version)
// Note: Old inline config command removed in favor of createConfigCommand

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
  .option('-p, --persona <persona>', 'AI persona to use', 'developer')
  .option('--model <model>', 'AI model to use')
  .option('--provider <provider>', 'AI provider to use')
  .option('-t, --temperature <temp>', 'Model temperature (0.0-2.0)', parseFloat)
  .option('--stream', 'Enable streaming responses')
  .option('--continue', 'Continue last session')
  .option('--resume <id>', 'Resume specific session by ID')
  .option('--new-session', 'Force new session even if one exists')
  .action(async (options: CommandOptions) => {
    try {
      const client = createAPIClient(options);
      
      // Session management
      const manager = getSessionManager();
      let sessionId: string;
      
      if (options.newSession) {
        // Force new session
        const session = manager.createSession({
          name: generateSessionName(),
          workingDirectory: process.cwd(),
        });
        sessionId = session.id;
        console.log(chalk.gray(`Created new session: ${formatSessionId(sessionId)}`));
      } else if (options.resume) {
        // Resume specific session
        const sessions = manager.listSessions({ limit: 100 });
        const session = sessions.find(s => s.id.startsWith(options.resume as string));
        if (!session) {
          console.error(chalk.red(`Session not found: ${options.resume}`));
          console.log(chalk.gray('Run "monkey session list" to see available sessions'));
          process.exit(1);
        }
        manager.setCurrentSessionId(session.id);
        sessionId = session.id;
        console.log(chalk.gray(`Resumed session: ${formatSessionId(sessionId)} (${session.name})`));
      } else if (options.continue) {
        // Continue last session
        const currentId = manager.getCurrentSessionId();
        if (currentId) {
          const session = manager.getSession(currentId);
          if (session) {
            sessionId = session.id;
            console.log(chalk.gray(`Continuing session: ${formatSessionId(sessionId)} (${session.name})`));
          } else {
            // Current session not found, create new
            const newSession = manager.createSession({
              name: generateSessionName(),
              workingDirectory: process.cwd(),
            });
            sessionId = newSession.id;
            console.log(chalk.gray(`Created new session: ${formatSessionId(sessionId)}`));
          }
        } else {
          // No current session, create new
          const newSession = manager.createSession({
            name: generateSessionName(),
            workingDirectory: process.cwd(),
          });
          sessionId = newSession.id;
          console.log(chalk.gray(`Created new session: ${formatSessionId(sessionId)}`));
        }
      } else {
        // Default: use UUID for backward compatibility
        sessionId = generateUUID();
      }

      console.log(chalk.green('🐒 Monkey Coder Chat'));
      console.log(
        chalk.gray(
          '💬 Chat with AI about your codebase. Type your message and press Enter.'
        )
      );
      console.log(chalk.gray('Commands: "exit", "quit" to leave, Ctrl+C anytime'));
      console.log(chalk.gray(`🎭 Persona: ${options.persona || 'developer'}`));
      console.log(chalk.gray('🔍 I can analyze files, suggest improvements, and help with coding tasks'));
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

          const request = await buildExecuteRequest('custom', input, [], {
            ...options,
            persona: options.persona || 'developer',
            // Let the advanced router analyze and route the request
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
          console.log('');
          console.log(chalk.cyan('🤖 Monkey Coder:'));
          console.log(response.result?.result || 'No response received');
          console.log('');
        } catch (error: any) {
          console.error(chalk.red('Error:'), error.message);
        }

        console.log('');
        rl.prompt();
      }).on('close', () => {
        console.log('');
        console.log(chalk.green('Thanks for using Monkey Coder! 🐒'));
        console.log(chalk.gray('Run "monkey" anytime to start a new chat session.'));
        process.exit(0);
      });

      // Handle Ctrl+C gracefully
      rl.on('SIGINT', () => {
        console.log('');
        console.log(chalk.yellow('Chat interrupted. Thanks for using Monkey Coder! 🐒'));
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
program.addCommand(createMCPToolsCommand());

// Add new hierarchical command groups (Phase 1 implementation)
program.addCommand(createRepoCommand(config));
program.addCommand(createConfigCommand(config));
program.addCommand(createGitCommand(config));
program.addCommand(createPRCommand(config));
program.addCommand(createIssueCommand(config));
program.addCommand(createSearchCommand(config));
program.addCommand(createReleaseCommand(config));
program.addCommand(createWorkflowCommand(config));

// Add session management command
program.addCommand(createSessionCommand());
// Add checkpoint management command (and top-level undo/redo/history)
registerCheckpointCommands(program);
// Add Ink UI commands
program.addCommand(createInkChatCommand(config));
program.addCommand(createInkAgentCommand(config));
// Add agent command
program.addCommand(createAgentCommand(config));

// Require authentication for main commands
const authRequiredCommands = ['implement', 'analyze', 'build', 'test', 'chat'];

program.hook('preSubcommand', async (thisCommand, actionCommand) => {
  if (authRequiredCommands.includes(actionCommand.name()) && !actionCommand.opts().apiKey) {
    await requireAuth(config);
  }
});

// If no command was provided, start chat mode with enhanced UX
if (process.argv.length === 2) {
  console.log(chalk.cyan('🐒 Welcome to Monkey Coder!'));
  console.log(chalk.gray('Starting interactive chat mode...'));
  console.log('');
  process.argv.push('chat');
}

// Parse command line arguments
program.parse();
