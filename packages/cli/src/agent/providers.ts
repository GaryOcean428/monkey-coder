/**
 * AI Provider Abstraction - Unified interface for OpenAI, Anthropic, and Google
 */

import Anthropic from '@anthropic-ai/sdk';
import OpenAI from 'openai';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { Message, Tool, AIResponse, ToolCall } from './types.js';

export interface AIProvider {
  chat(messages: Message[], tools: Tool[], options?: ChatOptions): Promise<AIResponse>;
}

export interface ChatOptions {
  temperature?: number;
  maxTokens?: number;
  model?: string;
}

/**
 * Anthropic Claude Provider
 */
export class AnthropicProvider implements AIProvider {
  private client: Anthropic;
  private defaultModel: string;

  constructor(apiKey?: string, defaultModel = 'claude-sonnet-4-20250514') {
    this.client = new Anthropic({ 
      apiKey: apiKey || process.env.ANTHROPIC_API_KEY 
    });
    this.defaultModel = defaultModel;
  }

  async chat(messages: Message[], tools: Tool[], options: ChatOptions = {}): Promise<AIResponse> {
    const model = options.model || this.defaultModel;
    
    // Separate system messages from conversation
    const systemMessages = messages.filter(m => m.role === 'system');
    const conversationMessages = messages.filter(m => m.role !== 'system');
    
    const response = await this.client.messages.create({
      model,
      max_tokens: options.maxTokens || 8192,
      temperature: options.temperature,
      system: systemMessages.map(m => m.content).join('\n\n') || undefined,
      messages: conversationMessages.map(m => ({
        role: m.role === 'assistant' ? 'assistant' : 'user',
        content: m.content,
      })),
      tools: tools.length > 0 ? tools.map(t => ({
        name: t.name,
        description: t.description,
        input_schema: t.parameters as any, // Anthropic expects specific schema structure
      })) : undefined,
    });

    return this.parseResponse(response);
  }

  private parseResponse(response: Anthropic.Message): AIResponse {
    const content = response.content;
    const textBlocks = content.filter(b => b.type === 'text') as Anthropic.TextBlock[];
    const toolBlocks = content.filter(b => b.type === 'tool_use') as Anthropic.ToolUseBlock[];

    return {
      text: textBlocks.map(b => b.text).join('\n'),
      toolCalls: toolBlocks.map(b => ({
        id: b.id,
        name: b.name,
        arguments: b.input as Record<string, unknown>,
      })),
      stopReason: response.stop_reason || undefined,
      usage: {
        inputTokens: response.usage.input_tokens,
        outputTokens: response.usage.output_tokens,
      },
    };
  }
}

/**
 * OpenAI GPT Provider
 */
export class OpenAIProvider implements AIProvider {
  private client: OpenAI;
  private defaultModel: string;

  constructor(apiKey?: string, defaultModel = 'gpt-4.1') {
    this.client = new OpenAI({ 
      apiKey: apiKey || process.env.OPENAI_API_KEY 
    });
    this.defaultModel = defaultModel;
  }

  async chat(messages: Message[], tools: Tool[], options: ChatOptions = {}): Promise<AIResponse> {
    const model = options.model || this.defaultModel;

    const response = await this.client.chat.completions.create({
      model,
      messages: messages.map(m => ({
        role: m.role,
        content: m.content,
      })),
      tools: tools.length > 0 ? tools.map(t => ({
        type: 'function' as const,
        function: {
          name: t.name,
          description: t.description,
          parameters: t.parameters,
        },
      })) : undefined,
      temperature: options.temperature,
      max_tokens: options.maxTokens,
    });

    return this.parseResponse(response);
  }

  private parseResponse(response: OpenAI.Chat.Completions.ChatCompletion): AIResponse {
    const choice = response.choices[0];
    if (!choice) {
      return {
        text: '',
        toolCalls: [],
        stopReason: 'error',
      };
    }
    
    const message = choice.message;

    return {
      text: message.content || '',
      toolCalls: message.tool_calls?.map(tc => ({
        id: tc.id,
        name: tc.function.name,
        arguments: JSON.parse(tc.function.arguments),
      })),
      stopReason: choice.finish_reason,
      usage: response.usage ? {
        inputTokens: response.usage.prompt_tokens,
        outputTokens: response.usage.completion_tokens,
      } : undefined,
    };
  }
}

/**
 * Google Gemini Provider
 */
export class GoogleProvider implements AIProvider {
  private client: GoogleGenerativeAI;
  private defaultModel: string;

  constructor(apiKey?: string, defaultModel = 'gemini-2.0-flash-001') {
    this.client = new GoogleGenerativeAI(
      apiKey || process.env.GOOGLE_API_KEY || ''
    );
    this.defaultModel = defaultModel;
  }

  async chat(messages: Message[], tools: Tool[], options: ChatOptions = {}): Promise<AIResponse> {
    const model = options.model || this.defaultModel;
    const genModel = this.client.getGenerativeModel({
      model,
      generationConfig: {
        temperature: options.temperature,
        maxOutputTokens: options.maxTokens,
      },
    });

    // Convert messages to Gemini format
    const history = messages.slice(0, -1).map(m => ({
      role: m.role === 'assistant' ? 'model' : 'user',
      parts: [{ text: m.content }],
    }));

    const lastMessage = messages[messages.length - 1];
    if (!lastMessage) {
      throw new Error('No messages provided');
    }
    
    const chat = genModel.startChat({
      history,
      tools: tools.length > 0 ? [{
        functionDeclarations: tools.map(t => ({
          name: t.name,
          description: t.description,
          parameters: t.parameters as any, // Google expects specific schema structure
        })),
      }] : undefined,
    });

    const result = await chat.sendMessage(lastMessage.content);
    const response = result.response;

    return this.parseResponse(response);
  }

  private parseResponse(response: any): AIResponse {
    const text = response.text?.() || '';
    const functionCalls = response.functionCalls?.() || [];

    return {
      text,
      toolCalls: functionCalls.map((fc: any, index: number) => ({
        id: `call_${index}`,
        name: fc.name,
        arguments: fc.args,
      })),
      stopReason: undefined,
      usage: response.usageMetadata ? {
        inputTokens: response.usageMetadata.promptTokenCount || 0,
        outputTokens: response.usageMetadata.candidatesTokenCount || 0,
      } : undefined,
    };
  }
}

/**
 * Factory function to create provider instances
 */
export function createProvider(
  provider: 'openai' | 'anthropic' | 'google',
  apiKey?: string,
  model?: string
): AIProvider {
  switch (provider) {
    case 'anthropic':
      return new AnthropicProvider(apiKey, model);
    case 'openai':
      return new OpenAIProvider(apiKey, model);
    case 'google':
      return new GoogleProvider(apiKey, model);
    default:
      throw new Error(`Unknown provider: ${provider}`);
  }
}
