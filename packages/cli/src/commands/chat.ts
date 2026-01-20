/**
 * Chat command - Interactive chat with Ink UI (default)
 * This is the main chat command that uses the enhanced Ink UI
 */
import { Command } from 'commander';
import chalk from 'chalk';
import { renderApp } from '../ui/index.js';
import { MonkeyCoderAPIClient } from '../api-client.js';
import { ConfigManager } from '../config.js';
import { buildExecuteRequest, generateUUID } from '../utils.js';
import { isInteractiveTerminal } from '../ui/terminal-detection.js';

interface ChatOptions {
  persona?: string;
  model?: string;
  provider?: string;
  temperature?: number;
  stream?: boolean;
  apiKey?: string;
  baseUrl?: string;
  continue?: boolean;
}

export function createChatCommand(config: ConfigManager): Command {
  return new Command('chat')
    .description('Start interactive chat with AI (uses rich Ink UI by default)')
    .option('-p, --persona <persona>', 'AI persona to use', 'developer')
    .option('--model <model>', 'AI model to use')
    .option('--provider <provider>', 'AI provider to use')
    .option('-t, --temperature <temp>', 'Model temperature (0.0-2.0)', parseFloat)
    .option('--stream', 'Enable streaming responses', true)
    .option('--continue', 'Continue previous chat session')
    .option('--no-ink', 'Disable Ink UI (use basic console output)')
    .action(async (options: ChatOptions & { ink?: boolean }) => {
      const apiKey = options.apiKey || config.getApiKey() || '';
      const baseUrl = options.baseUrl || config.getBaseUrl();

      if (!apiKey) {
        console.warn(chalk.yellow('Warning: No API key provided. Some features may not work.'));
      }

      // Check if Ink UI should be used
      const useInkUI = options.ink !== false && isInteractiveTerminal();

      if (!useInkUI) {
        console.log(chalk.yellow('⚠️  Using basic console mode (Ink UI disabled or non-interactive terminal)'));
        console.log(chalk.gray('For better experience, use an interactive terminal or remove --no-ink flag.'));
        // Fall back to basic console chat (not implemented in this minimal change set)
        console.log(chalk.red('Basic console chat not yet implemented. Please use interactive terminal.'));
        process.exit(1);
      }

      const client = new MonkeyCoderAPIClient(baseUrl, apiKey);
      const sessionId = generateUUID();

      console.log(chalk.cyan('🐵 Starting Monkey Coder Chat...'));
      console.log(chalk.gray(`Session ID: ${sessionId.slice(0, 8)}`));
      console.log('');

      const { waitUntilExit } = renderApp({
        mode: 'chat',
        workingDirectory: process.cwd(),
        onMessage: async (content: string) => {
          // Build the request
          const request = await buildExecuteRequest('custom', content, [], {
            persona: options.persona || 'developer',
            model: options.model,
            provider: options.provider,
            temperature: options.temperature,
            timeout: config.getDefaultTimeout(),
            stream: options.stream,
          }, config);

          // Use the same session ID for conversation continuity
          request.context.session_id = sessionId;

          // Execute the request
          if (options.stream) {
            let fullResponse = '';
            await client.executeStream(request, (event) => {
              if (event.type === 'progress' && event.data) {
                fullResponse += event.data;
              }
            });
            return fullResponse || 'No response received';
          } else {
            const response = await client.execute(request);
            return response.result?.result || 'No response received';
          }
        },
      });

      await waitUntilExit();
    });
}
