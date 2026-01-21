/**
 * Agent Runner - Local-first autonomous agent implementation
 * 
 * Enables autonomous file editing and shell execution with local tool execution.
 * Backend is only used for AI inference. Session persistence with checkpointing.
 */

import chalk from 'chalk';
import ora, { Ora } from 'ora';
import { confirm } from '@inquirer/prompts';

import { getSessionManager } from './session-manager.js';
import { getCheckpointManager } from './checkpoint-manager.js';
import { TOOL_REGISTRY, ToolResult } from './tools/index.js';
import { MonkeyCoderAPIClient } from './api-client.js';
import { ExecuteRequest } from './types.js';
import { generateUUID } from './utils.js';

// Types
export interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
}

export interface AgentOptions {
  localOnly?: boolean;
  requireApproval?: boolean;
  continueSession?: boolean;
  sessionId?: string;
  model?: string;
  baseUrl?: string;
  apiKey?: string;
  maxIterations?: number;
  sandboxMode?: 'none' | 'spawn' | 'docker';
}

interface AIResponse {
  content: string;
  toolCalls?: ToolCall[];
  stopReason?: string;
}

/**
 * AgentRunner - Manages autonomous agent execution loop
 */
export class AgentRunner {
  private sessionMgr = getSessionManager();
  private checkpointMgr = getCheckpointManager();
  private options: Omit<Required<AgentOptions>, 'sessionId'> & { sessionId?: string };
  private currentSessionId: string | null = null;
  private apiClient: MonkeyCoderAPIClient;
  private spinner: Ora | null = null;

  constructor(options: AgentOptions = {}) {
    this.options = {
      localOnly: false,
      requireApproval: true,
      continueSession: false,
      sessionId: undefined,
      model: 'claude-sonnet-4',
      baseUrl: process.env.MONKEY_CODER_BASE_URL || 'http://localhost:8000',
      apiKey: process.env.MONKEY_CODER_API_KEY || '',
      maxIterations: 20,
      sandboxMode: 'spawn',
      ...options,
    };

    this.apiClient = new MonkeyCoderAPIClient(
      this.options.baseUrl,
      this.options.apiKey
    );
  }

  /**
   * Run a single task
   */
  async runTask(task: string): Promise<void> {
    try {
      // Initialize session
      const session = this.sessionMgr.getOrCreateSession({
        continueSession: this.options.continueSession,
        sessionId: this.options.sessionId,
        name: `Agent Task: ${task.slice(0, 30)}...`,
      });
      this.currentSessionId = session.id;

      console.log(chalk.green('🐒 Monkey Coder Agent'));
      console.log(chalk.gray(`Session: ${session.id.slice(0, 8)}`));
      console.log(chalk.gray(`Sandbox: ${this.options.sandboxMode}`));
      console.log(chalk.gray(`Task: ${task}`));
      console.log('');

      // Create initial checkpoint
      await this.checkpointMgr.createCheckpoint(`Agent start: ${task.slice(0, 50)}`);

      // Add user message
      this.sessionMgr.addMessage(session.id, { role: 'user', content: task });

      // Build tool schemas for AI
      const tools = this.buildToolSchemas();

      // Agent loop
      let iterations = 0;
      let continueLoop = true;

      while (continueLoop && iterations < this.options.maxIterations) {
        iterations++;
        console.log(chalk.gray(`\n--- Iteration ${iterations} ---`));

        // Get AI response with tool calls
        const response = await this.callAI(tools);

        // Add assistant message
        if (response.content) {
          this.sessionMgr.addMessage(session.id, {
            role: 'assistant',
            content: response.content,
          });
          console.log(chalk.cyan('\n🤖 Agent:'));
          console.log(response.content);
        }

        // Check if we're done
        if (!response.toolCalls || response.toolCalls.length === 0) {
          console.log(chalk.green('\n✓ Task completed!'));
          continueLoop = false;
          break;
        }

        // Execute tool calls
        for (const call of response.toolCalls) {
          const result = await this.executeTool(call);

          // Add tool result to session
          this.sessionMgr.addMessage(session.id, {
            role: 'tool',
            content: JSON.stringify(result),
            toolCallId: call.id,
          });
        }
      }

      if (iterations >= this.options.maxIterations) {
        console.log(chalk.yellow('\n⚠ Agent reached maximum iterations'));
      }

      console.log(chalk.gray(`\nSession: ${session.id.slice(0, 8)}`));
      console.log(chalk.gray(`Use 'monkey session view ${session.id.slice(0, 8)}' to review`));
    } catch (error) {
      if (this.spinner) this.spinner.fail('Agent failed');
      console.error(chalk.red('\n✗ Error:'), error);
      throw error;
    } finally {
      if (this.spinner) this.spinner.stop();
    }
  }

  /**
   * Start interactive REPL mode
   */
  async startInteractive(): Promise<void> {
    console.log(chalk.yellow('Interactive agent mode not yet implemented'));
    console.log(chalk.gray('Use: monkey agent --task "your task description"'));
  }

  /**
   * Build tool schemas for AI
   */
  private buildToolSchemas(): object[] {
    return Object.values(TOOL_REGISTRY).map(tool => ({
      type: 'function',
      function: {
        name: tool.name,
        description: tool.description,
        parameters: tool.inputSchema,
      },
    }));
  }

  /**
   * Call AI API for next action
   */
  private async callAI(tools: object[]): Promise<AIResponse> {
    if (!this.currentSessionId) {
      throw new Error('No active session');
    }

    const context = this.sessionMgr.getSessionContext(this.currentSessionId);
    if (!context) {
      throw new Error('Session not found');
    }

    this.spinner = ora('AI is thinking...').start();

    try {
      // Format messages for API
      const messages = context.messages.map(m => {
        const msg: any = {
          role: m.role === 'tool' ? 'user' : m.role,
          content: m.content,
        };
        if (m.toolCallId) {
          msg.tool_call_id = m.toolCallId;
        }
        return msg;
      });

      // Build request
      const request: ExecuteRequest = {
        task_id: generateUUID(),
        task_type: 'custom',
        prompt: messages[messages.length - 1]?.content || '',
        context: {
          user_id: 'cli-agent',
          session_id: this.currentSessionId,
          environment: 'cli-agent',
          timeout: 300,
          max_tokens: 8000,
          temperature: 0.7,
        },
        persona_config: {
          persona: 'developer',
          slash_commands: [],
          context_window: 32768,
          use_markdown_spec: true,
          custom_instructions: `You are an autonomous coding agent. Use the available tools to complete the user's task.
Available tools: ${Object.keys(TOOL_REGISTRY).join(', ')}.
Think step by step and use tools as needed. When the task is complete, provide a summary without calling more tools.`,
        },
        preferred_providers: ['anthropic'],
        model_preferences: { anthropic: this.options.model },
      };

      // Call backend API
      const response = await this.apiClient.execute(request);

      this.spinner.succeed('AI responded');

      // Parse response for tool calls
      // Note: This is a simplified implementation
      // In production, you'd parse the actual tool calls from the response
      const result = response.result?.result || '';

      // Check if response contains tool calls
      // For now, we'll return empty tool calls to indicate completion
      // Real implementation would parse tool calls from the response
      return {
        content: result,
        toolCalls: [],
        stopReason: 'end_turn',
      };
    } catch (error) {
      this.spinner.fail('AI request failed');
      throw error;
    }
  }

  /**
   * Execute a tool call
   */
  private async executeTool(call: ToolCall): Promise<ToolResult> {
    const tool = TOOL_REGISTRY[call.name as keyof typeof TOOL_REGISTRY];
    if (!tool) {
      return {
        success: false,
        output: '',
        error: `Unknown tool: ${call.name}`,
      };
    }

    console.log(chalk.blue(`\n🔧 Tool: ${call.name}`));
    console.log(chalk.gray(`   Args: ${JSON.stringify(call.arguments, null, 2)}`));

    // User approval for dangerous operations
    if (this.options.requireApproval && this.isDangerous(call.name)) {
      const approved = await confirm({
        message: `Allow ${call.name}?`,
        default: true,
      });

      if (!approved) {
        console.log(chalk.yellow('   ✗ User denied'));
        return {
          success: false,
          output: '',
          error: 'User denied execution',
        };
      }
    }

    // Create checkpoint before execution
    await this.checkpointMgr.createCheckpoint(`Before ${call.name}`);

    try {
      // Pass sandbox mode to shell_execute tool
      const toolArgs = call.arguments as any;
      if (call.name === 'shell_execute' && !toolArgs.sandboxMode) {
        toolArgs.sandboxMode = this.options.sandboxMode;
      }

      // Execute tool
      const result = await tool.execute(toolArgs);

      if (result.success) {
        console.log(chalk.green(`   ✓ ${result.output.slice(0, 100)}`));
      } else {
        console.log(chalk.red(`   ✗ ${result.error?.slice(0, 100)}`));
      }

      return result;
    } catch (error) {
      console.log(chalk.red(`   ✗ Error: ${error}`));
      return {
        success: false,
        output: '',
        error: `Tool execution failed: ${error}`,
      };
    }
  }

  /**
   * Check if tool is dangerous and requires approval
   */
  private isDangerous(toolName: string): boolean {
    const dangerousTools = ['shell_execute', 'file_write', 'file_delete', 'file_edit'];
    return dangerousTools.includes(toolName);
  }
}
