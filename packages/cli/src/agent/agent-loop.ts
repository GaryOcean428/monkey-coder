/**
 * Agent Loop - Core orchestration for local agent mode
 */

import chalk from 'chalk';
import ora, { Ora } from 'ora';
import { getMCPManager } from '../mcp-client.js';
import { getCheckpointManager } from '../checkpoint-manager.js';
import { getSessionManager } from '../session-manager.js';
import { TOOL_REGISTRY } from '../tools/index.js';
import { createProvider, AIProvider } from './providers.js';
import { AgentConfig, Message, Tool, ToolCall, ToolExecutionResult } from './types.js';

/**
 * Agent Loop - orchestrates AI calls and tool executions
 */
export class AgentLoop {
  private provider: AIProvider | null = null;
  private mcp = getMCPManager();
  private checkpoints = getCheckpointManager();
  private sessions = getSessionManager();
  private spinner: Ora | null = null;
  private conversationHistory: Message[] = [];

  async initialize(config: AgentConfig): Promise<void> {
    // Initialize AI provider
    this.provider = createProvider(config.provider, undefined, config.model);

    // Initialize MCP connections (if in hybrid or cloud mode)
    if (config.mode !== 'local') {
      const mcpConfigs = this.mcp.getAllServerConfigs();
      for (const mcpConfig of mcpConfigs) {
        if (mcpConfig.enabled) {
          try {
            await this.mcp.connect(mcpConfig.name);
          } catch (error) {
            console.warn(chalk.yellow(`Warning: Could not connect to MCP server ${mcpConfig.name}`));
          }
        }
      }
    }
  }

  /**
   * Run the agent loop
   */
  async run(prompt: string, config: AgentConfig): Promise<void> {
    if (!this.provider) {
      throw new Error('Agent not initialized. Call initialize() first.');
    }

    // Create checkpoint before starting
    this.spinner = ora('Creating checkpoint...').start();
    await this.checkpoints.createCheckpoint(`Before: ${prompt.slice(0, 50)}...`);
    this.spinner.succeed('Checkpoint created');

    // Get or create session
    const session = this.sessions.getOrCreateSession({
      name: `Agent: ${prompt.slice(0, 30)}...`,
    });

    // Add system message
    this.conversationHistory.push({
      role: 'system',
      content: this.buildSystemPrompt(config),
    });

    // Add user message
    this.conversationHistory.push({
      role: 'user',
      content: prompt,
    });

    // Save messages to session
    this.sessions.addMessage(session.id, {
      role: 'user',
      content: prompt,
    });

    // Build tool schemas
    const tools = this.buildToolSchemas(config);

    // Main agent loop
    for (let iteration = 0; iteration < config.maxIterations; iteration++) {
      this.spinner = ora(`Thinking... (iteration ${iteration + 1}/${config.maxIterations})`).start();

      try {
        // Call AI with current conversation and tools
        const response = await this.provider.chat(
          this.conversationHistory,
          tools,
          {
            temperature: config.temperature,
            maxTokens: config.maxTokens,
          }
        );

        this.spinner.stop();

        // Display response text
        if (response.text) {
          console.log(chalk.cyan('\n🤖 Agent:'), response.text);
          
          this.conversationHistory.push({
            role: 'assistant',
            content: response.text,
          });

          this.sessions.addMessage(session.id, {
            role: 'assistant',
            content: response.text,
          });
        }

        // If no tool calls, we're done
        if (!response.toolCalls || response.toolCalls.length === 0) {
          console.log(chalk.green('\n✅ Task completed!'));
          break;
        }

        // Execute tool calls
        const toolResults = await this.executeTools(response.toolCalls, config);

        // Add tool results to conversation
        for (const result of toolResults) {
          const toolResultMessage = `Tool ${result.toolCallId} result: ${result.error || result.result}`;
          
          this.conversationHistory.push({
            role: 'user',
            content: toolResultMessage,
          });

          this.sessions.addMessage(session.id, {
            role: 'tool',
            content: toolResultMessage,
            toolCallId: result.toolCallId,
          });
        }

        // Check if we hit max iterations
        if (iteration === config.maxIterations - 1) {
          console.log(chalk.yellow('\n⚠️ Max iterations reached. Task may be incomplete.'));
        }

      } catch (error) {
        this.spinner?.fail('Error during agent execution');
        console.error(chalk.red('\n❌ Error:'), error);
        throw error;
      }
    }

    // Create final checkpoint
    this.spinner = ora('Creating final checkpoint...').start();
    await this.checkpoints.createCheckpoint(`After: ${prompt.slice(0, 50)}...`);
    this.spinner.succeed('Final checkpoint created');
  }

  /**
   * Build system prompt
   */
  private buildSystemPrompt(config: AgentConfig): string {
    return `You are a helpful AI coding assistant operating in ${config.mode} mode.

Your capabilities:
- Read and write files
- Execute shell commands (with approval)
- Search files with patterns
- List directory contents
- Use MCP tools from connected servers

Guidelines:
1. Break down complex tasks into smaller steps
2. Use appropriate tools to accomplish tasks
3. Always verify your actions succeeded
4. Be explicit about what you're doing
5. Ask for clarification if needed

Working directory: ${process.cwd()}
Mode: ${config.mode}`;
  }

  /**
   * Build tool schemas for AI
   */
  private buildToolSchemas(config: AgentConfig): Tool[] {
    const tools: Tool[] = [];

    // Add local tools
    for (const [name, tool] of Object.entries(TOOL_REGISTRY)) {
      tools.push({
        name: tool.name,
        description: tool.description,
        parameters: tool.inputSchema,
      });
    }

    // Add MCP tools (if not in local mode)
    if (config.mode !== 'local') {
      const mcpTools = this.mcp.getAllTools();
      for (const mcpTool of mcpTools) {
        tools.push({
          name: mcpTool.name,
          description: mcpTool.description || '',
          parameters: mcpTool.inputSchema,
        });
      }
    }

    return tools;
  }

  /**
   * Execute tool calls
   */
  private async executeTools(
    toolCalls: ToolCall[],
    config: AgentConfig
  ): Promise<ToolExecutionResult[]> {
    const results: ToolExecutionResult[] = [];

    for (const call of toolCalls) {
      console.log(chalk.blue(`\n🔧 Executing tool: ${call.name}`));

      // Check if it's a local tool
      const localTool = TOOL_REGISTRY[call.name as keyof typeof TOOL_REGISTRY];
      
      if (localTool) {
        try {
          // Request approval for destructive operations
          if (!config.autoApprove && this.isDestructive(call.name)) {
            const inquirer = await import('inquirer');
            const { approved } = await inquirer.default.prompt([{
              type: 'confirm',
              name: 'approved',
              message: `Approve ${call.name} with args: ${JSON.stringify(call.arguments)}?`,
              default: false,
            }]);

            if (!approved) {
              results.push({
                toolCallId: call.id,
                result: '',
                error: 'Tool execution denied by user',
              });
              continue;
            }
          }

          const result = await localTool.execute(call.arguments as any);
          
          console.log(chalk.green(`✅ ${result.success ? 'Success' : 'Failed'}: ${result.output || result.error}`));
          
          results.push({
            toolCallId: call.id,
            result: result.success ? result.output : '',
            error: result.error,
          });
        } catch (error) {
          console.log(chalk.red(`❌ Error: ${error}`));
          results.push({
            toolCallId: call.id,
            result: '',
            error: String(error),
          });
        }
      } else {
        // Try MCP tool
        try {
          const mcpResult = await this.mcp.executeTool(call.name, call.arguments);
          
          const resultText = mcpResult.content
            .map(c => c.text || c.data || '')
            .join('\n');

          console.log(chalk.green(`✅ ${mcpResult.success ? 'Success' : 'Failed'}`));
          
          results.push({
            toolCallId: call.id,
            result: mcpResult.success ? resultText : '',
            error: mcpResult.isError ? resultText : undefined,
          });
        } catch (error) {
          console.log(chalk.red(`❌ Error: ${error}`));
          results.push({
            toolCallId: call.id,
            result: '',
            error: String(error),
          });
        }
      }
    }

    return results;
  }

  /**
   * Check if a tool is destructive (requires approval)
   */
  private isDestructive(toolName: string): boolean {
    const destructiveTools = [
      'file_write',
      'file_edit',
      'file_delete',
      'shell_execute',
    ];
    return destructiveTools.includes(toolName);
  }

  /**
   * Cleanup resources
   */
  async cleanup(): Promise<void> {
    if (this.spinner) {
      this.spinner.stop();
    }
    await this.mcp.disconnectAll();
  }
}
