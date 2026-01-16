/**
 * Type definitions for local agent mode
 */

export type AgentMode = 'local' | 'hybrid' | 'cloud';
export type AIProvider = 'openai' | 'anthropic' | 'google';

export interface AgentConfig {
  mode: AgentMode;
  model: string;
  provider: AIProvider;
  maxIterations: number;
  autoApprove: boolean;
  temperature?: number;
  maxTokens?: number;
}

export interface Message {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
  toolCallId?: string;
}

export interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
}

export interface Tool {
  name: string;
  description: string;
  parameters: Record<string, unknown>;
}

export interface AIResponse {
  text: string;
  toolCalls?: ToolCall[];
  stopReason?: string;
  usage?: {
    inputTokens: number;
    outputTokens: number;
  };
}

export interface ToolExecutionResult {
  toolCallId: string;
  result: string;
  error?: string;
}
