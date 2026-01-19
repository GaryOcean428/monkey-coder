/**
 * Agent command with Ink UI
 */
import { Command } from 'commander';
import chalk from 'chalk';
import { renderApp } from '../ui/index.js';
import { MonkeyCoderAPIClient } from '../api-client.js';
import { ConfigManager } from '../config.js';
import { buildExecuteRequest, generateUUID } from '../utils.js';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

interface AgentOptions {
  persona?: string;
  model?: string;
  provider?: string;
  temperature?: number;
  stream?: boolean;
  apiKey?: string;
  baseUrl?: string;
  mcpConfig?: string;
  sandbox?: 'none' | 'basic' | 'docker';
}

interface MCPServerConfig {
  name: string;
  type: 'stdio' | 'sse' | 'http';
  command?: string;
  args?: string[];
  url?: string;
}

function loadMCPConfig(configPath?: string): MCPServerConfig[] {
  const defaultPath = path.join(os.homedir(), '.monkey-coder', 'mcp-servers.json');
  const finalPath = configPath || defaultPath;

  if (!fs.existsSync(finalPath)) {
    return [];
  }

  try {
    const content = fs.readFileSync(finalPath, 'utf-8');
    const config = JSON.parse(content);
    return config.servers || [];
  } catch (error) {
    console.error(`Failed to load MCP config from ${finalPath}:`, error);
    return [];
  }
}

export function createInkAgentCommand(config: ConfigManager): Command {
  return new Command('agent-ink')
    .description('Start local agent mode with rich Ink UI and tool execution')
    .option('-p, --persona <persona>', 'AI persona to use', 'agent')
    .option('--model <model>', 'AI model to use')
    .option('--provider <provider>', 'AI provider to use')
    .option('-t, --temperature <temp>', 'Model temperature (0.0-2.0)', parseFloat)
    .option('--stream', 'Enable streaming responses', true)
    .option('--mcp-config <path>', 'Path to MCP servers configuration file')
    .option('--sandbox <mode>', 'Sandbox mode: none, basic, docker', 'basic')
    .action(async (options: AgentOptions) => {
      const apiKey = options.apiKey || config.getApiKey() || '';
      const baseUrl = options.baseUrl || config.getBaseUrl();

      if (!apiKey) {
        console.warn('Warning: No API key provided. Some features may not work.');
      }

      // Check Docker availability if docker mode is requested
      if (options.sandbox === 'docker') {
        const { getSandbox } = await import('../sandbox/docker-executor.js');
        const sandbox = await getSandbox();
        if (!sandbox) {
          console.error(chalk.red('✗ Docker not available for sandbox mode'));
          console.error(chalk.yellow('→ Falling back to basic sandbox mode'));
          options.sandbox = 'basic';
        } else {
          console.log(chalk.green('✓ Docker sandbox enabled'));
        }
      }

      const client = new MonkeyCoderAPIClient(baseUrl, apiKey);
      const mcpServers = loadMCPConfig(options.mcpConfig);
      const sessionId = generateUUID();

      const { waitUntilExit } = renderApp({
        mode: 'agent',
        workingDirectory: process.cwd(),
        mcpServers,
        onMessage: async (content: string) => {
          // Build the request
          const request = await buildExecuteRequest('custom', content, [], {
            persona: options.persona || 'agent',
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
