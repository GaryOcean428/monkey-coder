/**
 * Chat command with Ink UI
 */
import { Command } from 'commander';
import { renderApp } from '../ui/index.js';
import { MonkeyCoderAPIClient } from '../api-client.js';
import { ConfigManager } from '../config.js';
import { buildExecuteRequest, generateUUID } from '../utils.js';

interface ChatOptions {
  persona?: string;
  model?: string;
  provider?: string;
  temperature?: number;
  stream?: boolean;
  apiKey?: string;
  baseUrl?: string;
}

export function createInkChatCommand(config: ConfigManager): Command {
  return new Command('chat-ink')
    .description('Start interactive chat with rich Ink UI')
    .option('-p, --persona <persona>', 'AI persona to use', 'developer')
    .option('--model <model>', 'AI model to use')
    .option('--provider <provider>', 'AI provider to use')
    .option('-t, --temperature <temp>', 'Model temperature (0.0-2.0)', parseFloat)
    .option('--stream', 'Enable streaming responses', true)
    .action(async (options: ChatOptions) => {
      const apiKey = options.apiKey || config.getApiKey() || '';
      const baseUrl = options.baseUrl || config.getBaseUrl();

      if (!apiKey) {
        console.warn('Warning: No API key provided. Some features may not work.');
      }

      const client = new MonkeyCoderAPIClient(baseUrl, apiKey);
      const sessionId = generateUUID();

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
