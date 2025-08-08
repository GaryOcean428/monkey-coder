/**
 * OpenAI Response Examples - TypeScript/JavaScript Implementation
 * ==============================================================
 * 
 * This module provides practical examples of OpenAI client response patterns
 * for different GPT-5 model variants. These examples can be used as templates
 * for integrating OpenAI responses in TypeScript/JavaScript applications.
 * 
 * Usage:
 *   Node.js: node openai-response-examples.js
 *   TypeScript: ts-node openai-response-examples.ts
 * 
 * Requirements:
 *   npm install openai dotenv
 */

import OpenAI from 'openai';
import { config } from 'dotenv';

// Load environment variables
config();

interface ModelConfig {
  name: string;
  temperature?: number;
  max_output_tokens?: number;
  top_p?: number;
  text_config?: Record<string, any>;
  reasoning_config?: Record<string, any>;
}

interface ResponseInput {
  role: string;
  content: Array<{
    type: string;
    text: string;
  }>;
}

interface OpenAIResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: Array<{
    index: number;
    message: {
      role: string;
      content: string;
    };
    finish_reason: string;
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

/**
 * Examples of OpenAI response patterns for different model configurations.
 * 
 * Note: GPT-5 models shown are conceptual examples for future reference.
 * Please refer to the Models Manifest for currently supported models.
 */
export class OpenAIResponseExamples {
  private client: OpenAI;
  private models: Record<string, ModelConfig>;

  constructor(apiKey?: string) {
    const key = apiKey || process.env.OPENAI_API_KEY;
    if (!key) {
      throw new Error('OpenAI API key is required. Set OPENAI_API_KEY environment variable.');
    }

    this.client = new OpenAI({ apiKey: key });

    // Model configurations
    this.models = {
      chat_latest: {
        name: 'gpt-5-chat-latest',
        temperature: 2,
        max_output_tokens: 16384,
        top_p: 1,
        text_config: {},
        reasoning_config: {},
      },
      mini: {
        name: 'gpt-5-mini',
        text_config: {
          format: { type: 'text' },
          verbosity: 'high',
        },
        reasoning_config: {
          effort: 'high',
          summary: 'auto',
        },
      },
      nano: {
        name: 'gpt-5-nano',
        text_config: {
          format: { type: 'text' },
          verbosity: 'low',
        },
        reasoning_config: {
          effort: 'minimal',
          summary: 'detailed',
        },
      },
    };
  }

  /**
   * Create a response using GPT-5 Chat Latest configuration.
   * Optimized for complex reasoning and creative tasks.
   */
  async createGpt5ChatLatestResponse(systemPrompt: string): Promise<OpenAIResponse> {
    const config = this.models.chat_latest;

    try {
      const response = await (this.client as any).responses.create({
        model: config.name,
        input: [
          {
            role: 'system',
            content: [
              {
                type: 'input_text',
                text: systemPrompt,
              },
            ],
          },
        ],
        text: config.text_config,
        reasoning: config.reasoning_config,
        tools: [],
        temperature: config.temperature,
        max_output_tokens: config.max_output_tokens,
        top_p: config.top_p,
        store: true,
      });
      return response;
    } catch (error) {
      console.log(`Note: This is a conceptual example. Current error: ${error}`);
      return this.mockResponse(config.name, systemPrompt);
    }
  }

  /**
   * Create a response using GPT-5 Mini configuration.
   * Balanced performance for general development tasks.
   */
  async createGpt5MiniResponse(systemPrompt: string): Promise<OpenAIResponse> {
    const config = this.models.mini;

    try {
      const response = await (this.client as any).responses.create({
        model: config.name,
        input: [
          {
            role: 'developer',
            content: [
              {
                type: 'input_text',
                text: systemPrompt,
              },
            ],
          },
        ],
        text: config.text_config,
        reasoning: config.reasoning_config,
        tools: [],
        store: true,
      });
      return response;
    } catch (error) {
      console.log(`Note: This is a conceptual example. Current error: ${error}`);
      return this.mockResponse(config.name, systemPrompt);
    }
  }

  /**
   * Create a response using GPT-5 Nano configuration.
   * Lightweight and efficient for simple tasks.
   */
  async createGpt5NanoResponse(systemPrompt: string): Promise<OpenAIResponse> {
    const config = this.models.nano;

    try {
      const response = await (this.client as any).responses.create({
        model: config.name,
        input: [
          {
            role: 'developer',
            content: [
              {
                type: 'input_text',
                text: systemPrompt,
              },
            ],
          },
        ],
        text: config.text_config,
        reasoning: config.reasoning_config,
        tools: [],
        store: true,
      });
      return response;
    } catch (error) {
      console.log(`Note: This is a conceptual example. Current error: ${error}`);
      return this.mockResponse(config.name, systemPrompt);
    }
  }

  /**
   * Create a response with custom configuration.
   */
  async createCustomResponse(
    modelType: keyof typeof this.models,
    systemPrompt: string,
    customConfig?: Partial<ModelConfig>
  ): Promise<OpenAIResponse> {
    if (!this.models[modelType]) {
      throw new Error(`Unknown model type: ${modelType}`);
    }

    const config = { ...this.models[modelType], ...customConfig };

    try {
      const requestConfig: any = {
        model: config.name,
        input: [
          {
            role: modelType === 'chat_latest' ? 'system' : 'developer',
            content: [
              {
                type: 'input_text',
                text: systemPrompt,
              },
            ],
          },
        ],
        text: config.text_config || {},
        reasoning: config.reasoning_config || {},
        tools: [],
        store: true,
      };

      // Add optional parameters if they exist
      if (config.temperature !== undefined) {
        requestConfig.temperature = config.temperature;
      }
      if (config.max_output_tokens !== undefined) {
        requestConfig.max_output_tokens = config.max_output_tokens;
      }
      if (config.top_p !== undefined) {
        requestConfig.top_p = config.top_p;
      }

      const response = await (this.client as any).responses.create(requestConfig);
      return response;
    } catch (error) {
      console.log(`Note: This is a conceptual example. Current error: ${error}`);
      return this.mockResponse(config.name, systemPrompt);
    }
  }

  /**
   * Batch process multiple prompts with different models.
   */
  async batchProcess(
    prompts: Array<{ prompt: string; model: keyof typeof this.models }>
  ): Promise<OpenAIResponse[]> {
    const promises = prompts.map(({ prompt, model }) =>
      this.createCustomResponse(model, prompt)
    );

    return Promise.all(promises);
  }

  /**
   * Stream responses for real-time applications.
   * Note: This is a conceptual implementation for streaming responses.
   */
  async streamResponse(
    modelType: keyof typeof this.models,
    systemPrompt: string,
    onChunk: (chunk: string) => void
  ): Promise<void> {
    const config = this.models[modelType];

    try {
      // Note: Actual streaming implementation would use OpenAI's streaming API
      const mockChunks = [
        'This is a ',
        'streamed response ',
        'from ',
        config.name,
        ' for demonstration purposes.',
      ];

      for (const chunk of mockChunks) {
        await new Promise((resolve) => setTimeout(resolve, 100));
        onChunk(chunk);
      }
    } catch (error) {
      console.error('Streaming error:', error);
      onChunk(`Error: ${error}`);
    }
  }

  /**
   * Create a mock response for demonstration purposes.
   */
  private mockResponse(model: string, prompt: string): OpenAIResponse {
    return {
      id: 'example-response',
      object: 'response',
      created: Math.floor(Date.now() / 1000),
      model,
      choices: [
        {
          index: 0,
          message: {
            role: 'assistant',
            content: `This is a conceptual example response from ${model} for prompt: '${prompt.substring(0, 50)}...'`,
          },
          finish_reason: 'stop',
        },
      ],
      usage: {
        prompt_tokens: 20,
        completion_tokens: 30,
        total_tokens: 50,
      },
    };
  }

  /**
   * Demonstrate all three model configurations.
   */
  async demonstrateAllModels(): Promise<void> {
    console.log('OpenAI Response Examples - TypeScript/JavaScript Implementation');
    console.log('='.repeat(70));
    console.log();

    const systemPrompt = 'You are a helpful AI assistant for code generation and analysis.';

    // GPT-5 Chat Latest
    console.log('1. GPT-5 Chat Latest (High Performance)');
    console.log('-'.repeat(40));
    const chatLatestResponse = await this.createGpt5ChatLatestResponse(systemPrompt);
    console.log(`Model: ${chatLatestResponse.model}`);
    console.log(`Response: ${chatLatestResponse.choices[0]?.message?.content || 'N/A'}`);
    console.log();

    // GPT-5 Mini
    console.log('2. GPT-5 Mini (Balanced Performance)');
    console.log('-'.repeat(40));
    const miniResponse = await this.createGpt5MiniResponse(systemPrompt);
    console.log(`Model: ${miniResponse.model}`);
    console.log(`Response: ${miniResponse.choices[0]?.message?.content || 'N/A'}`);
    console.log();

    // GPT-5 Nano
    console.log('3. GPT-5 Nano (Lightweight Performance)');
    console.log('-'.repeat(40));
    const nanoResponse = await this.createGpt5NanoResponse(systemPrompt);
    console.log(`Model: ${nanoResponse.model}`);
    console.log(`Response: ${nanoResponse.choices[0]?.message?.content || 'N/A'}`);
    console.log();

    console.log('Note: These are conceptual examples for future OpenAI models.');
    console.log('Please refer to the Models Manifest for currently supported models.');
  }
}

/**
 * React Hook for OpenAI integration (Frontend use case).
 */
export function useOpenAIResponses() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateResponse = async (
    modelType: 'chat_latest' | 'mini' | 'nano',
    prompt: string
  ): Promise<string | null> => {
    setLoading(true);
    setError(null);

    try {
      // Note: In a real React app, you'd call your backend API
      // This is just a conceptual example
      const examples = new OpenAIResponseExamples();
      const response = await examples.createCustomResponse(modelType, prompt);
      return response.choices[0]?.message?.content || null;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return null;
    } finally {
      setLoading(false);
    }
  };

  return {
    generateResponse,
    loading,
    error,
  };
}

/**
 * Express.js middleware for OpenAI integration (Backend use case).
 */
export function createOpenAIMiddleware() {
  const examples = new OpenAIResponseExamples();

  return {
    async generateResponse(req: any, res: any, next: any) {
      try {
        const { model = 'mini', prompt } = req.body;

        if (!prompt) {
          return res.status(400).json({
            error: 'Prompt is required',
          });
        }

        const response = await examples.createCustomResponse(model as any, prompt);

        res.json({
          success: true,
          data: {
            model: response.model,
            content: response.choices[0]?.message?.content,
            usage: response.usage,
          },
        });
      } catch (error) {
        console.error('OpenAI middleware error:', error);
        res.status(500).json({
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    },

    async streamResponse(req: any, res: any, next: any) {
      try {
        const { model = 'mini', prompt } = req.body;

        res.setHeader('Content-Type', 'text/event-stream');
        res.setHeader('Cache-Control', 'no-cache');
        res.setHeader('Connection', 'keep-alive');

        await examples.streamResponse(model as any, prompt, (chunk) => {
          res.write(`data: ${JSON.stringify({ chunk })}\n\n`);
        });

        res.write('data: [DONE]\n\n');
        res.end();
      } catch (error) {
        console.error('Streaming error:', error);
        res.status(500).json({
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    },
  };
}

// React useState is needed for the hook - mock it for Node.js environments
function useState<T>(initialValue: T): [T, (value: T) => void] {
  let value = initialValue;
  const setValue = (newValue: T) => {
    value = newValue;
  };
  return [value, setValue];
}

// Main execution for Node.js
if (require.main === module) {
  async function main() {
    try {
      const examples = new OpenAIResponseExamples();
      await examples.demonstrateAllModels();

      // Demonstrate batch processing
      console.log('\nBatch Processing Example:');
      console.log('-'.repeat(30));
      const batchPrompts = [
        { prompt: 'Generate a TypeScript interface for a user object.', model: 'mini' as const },
        { prompt: 'Create a simple React component.', model: 'nano' as const },
        { prompt: 'Explain advanced JavaScript concepts.', model: 'chat_latest' as const },
      ];

      const batchResults = await examples.batchProcess(batchPrompts);
      batchResults.forEach((result, index) => {
        console.log(`Batch ${index + 1}: ${result.choices[0]?.message?.content?.substring(0, 100)}...`);
      });

      // Demonstrate streaming
      console.log('\nStreaming Example:');
      console.log('-'.repeat(20));
      await examples.streamResponse('mini', 'Write a simple function', (chunk) => {
        process.stdout.write(chunk);
      });
      console.log('\n');

    } catch (error) {
      console.error('Example error (expected for conceptual models):', error);
    }
  }

  main().catch(console.error);
}