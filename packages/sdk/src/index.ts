/**
 * Monkey Coder SDK - TypeScript/JavaScript client
 * 
 * A comprehensive client library that provides:
 * - Authentication and token management
 * - Automatic retries with exponential backoff
 * - Streaming support for real-time execution
 * - Type-safe interfaces for all API endpoints
 * - Error handling and request/response transformation
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';

// Core types based on the API models
export type TaskType = 
  | 'code_generation'
  | 'code_analysis' 
  | 'code_review'
  | 'documentation'
  | 'testing'
  | 'debugging'
  | 'refactoring'
  | 'custom';

export type PersonaType = 
  | 'developer'
  | 'architect'
  | 'reviewer'
  | 'security_analyst'
  | 'performance_expert'
  | 'tester'
  | 'technical_writer'
  | 'custom';

export type ProviderType = 'openai' | 'anthropic' | 'google' | 'qwen';
export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'failed' | 'cancelled';

// Configuration interfaces
export interface ExecutionContext {
  user_id: string;
  session_id?: string;
  workspace_id?: string;
  environment?: string;
  timeout?: number;
  max_tokens?: number;
  temperature?: number;
}

export interface PersonaConfig {
  persona: PersonaType;
  slash_commands?: string[];
  context_window?: number;
  use_markdown_spec?: boolean;
  custom_instructions?: string;
}

// Backward compatibility alias
export interface SuperClaudeConfig extends PersonaConfig {}

export interface Monkey1Config {
  agent_count?: number;
  coordination_strategy?: string;
  consensus_threshold?: number;
  enable_reflection?: boolean;
  max_iterations?: number;
}

export interface OrchestrationConfig {
  parallel_futures?: boolean;
  collapse_strategy?: string;
  quantum_coherence?: number;
  execution_branches?: number;
  uncertainty_threshold?: number;
}

// Backward compatibility alias
export interface Gary8DConfig extends OrchestrationConfig {}

// Request/Response interfaces
export interface ExecuteRequest {
  task_id?: string;
  task_type: TaskType;
  prompt: string;
  files?: Array<{
    path: string;
    content: string;
    type?: string;
  }>;
  context: ExecutionContext;
  persona_config: PersonaConfig;
  monkey1_config?: Monkey1Config;
  orchestration_config?: OrchestrationConfig;
  preferred_providers?: ProviderType[];
  model_preferences?: Record<ProviderType, string>;
}

export interface UsageMetrics {
  tokens_used: number;
  tokens_input: number;
  tokens_output: number;
  provider_breakdown: Record<string, number>;
  cost_estimate: number;
  execution_time: number;
}

export interface ExecutionResult {
  result: any;
  metadata: Record<string, any>;
  artifacts: Array<Record<string, any>>;
  confidence_score: number;
  quantum_collapse_info: Record<string, any>;
}

export interface ExecuteResponse {
  execution_id: string;
  task_id: string;
  status: TaskStatus;
  result?: ExecutionResult;
  error?: string;
  created_at: string;
  completed_at?: string;
  usage?: UsageMetrics;
  execution_time?: number;
  persona_routing: Record<string, any>;
  monkey1_orchestration: Record<string, any>;
  orchestration_execution: Record<string, any>;
}

export interface StreamEvent {
  type: 'start' | 'progress' | 'result' | 'error' | 'complete';
  data?: any;
  progress?: {
    step: string;
    percentage?: number;
    metadata?: Record<string, any>;
  };
  error?: {
    message: string;
    code?: string;
  };
}

export interface UsageRequest {
  start_date?: string;
  end_date?: string;
  granularity?: 'hourly' | 'daily' | 'weekly' | 'monthly';
  include_details?: boolean;
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
  components: Record<string, string>;
}

// Client configuration
export interface MonkeyCoderClientConfig {
  baseURL?: string;
  apiKey?: string;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  maxRetryDelay?: number;
  retryCondition?: (error: AxiosError) => boolean;
  onRetry?: (retryCount: number, error: AxiosError) => void;
}

// Retry configuration
interface RetryConfig {
  retries: number;
  retryDelay: number;
  maxRetryDelay: number;
  retryCondition: (error: AxiosError) => boolean;
  onRetry?: (retryCount: number, error: AxiosError) => void;
}

// Error types
export class MonkeyCoderError extends Error {
  constructor(
    message: string,
    public readonly code?: string,
    public readonly statusCode?: number,
    public readonly details?: any
  ) {
    super(message);
    this.name = 'MonkeyCoderError';
  }
}

export class MonkeyCoderClient {
  private client: AxiosInstance;
  private retryConfig: RetryConfig;
  private apiKey?: string;

  constructor(config: MonkeyCoderClientConfig = {}) {
    const {
      baseURL = process.env.MONKEY_CODER_BASE_URL || 'http://localhost:8000',
      apiKey,
      timeout = 300000, // 5 minutes default
      retries = 3,
      retryDelay = 1000,
      maxRetryDelay = 10000,
      retryCondition = this.defaultRetryCondition,
      onRetry
    } = config;

    this.apiKey = apiKey;
    this.retryConfig = {
      retries,
      retryDelay,
      maxRetryDelay,
      retryCondition,
      onRetry
    };

    this.client = axios.create({
      baseURL: baseURL.replace(/\/$/, ''), // Remove trailing slash
      timeout,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'monkey-coder-sdk-ts/1.0.0',
        ...(apiKey && { Authorization: `Bearer ${apiKey}` })
      }
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response) {
          const status = error.response.status;
          const message = (error.response.data as any)?.detail || 
                         (error.response.data as any)?.message || 
                         error.message;
          throw new MonkeyCoderError(
            `API Error (${status}): ${message}`,
            (error.response.data as any)?.error_code,
            status,
            error.response.data
          );
        } else if (error.request) {
          throw new MonkeyCoderError(
            'No response from server. Please check if the service is running.',
            'NO_RESPONSE'
          );
        } else {
          throw new MonkeyCoderError(`Request error: ${error.message}`, 'REQUEST_ERROR');
        }
      }
    );
  }

  /**
   * Default retry condition - retry on network errors and 5xx status codes
   */
  private defaultRetryCondition(error: AxiosError): boolean {
    return !error.response || error.response.status >= 500;
  }

  /**
   * Calculate exponential backoff delay
   */
  private getRetryDelay(retryCount: number): number {
    const delay = this.retryConfig.retryDelay * Math.pow(2, retryCount);
    return Math.min(delay, this.retryConfig.maxRetryDelay);
  }

  /**
   * Make request with retry logic
   */
  private async makeRequest<T>(config: AxiosRequestConfig): Promise<T> {
    let lastError: AxiosError;
    
    for (let attempt = 0; attempt <= this.retryConfig.retries; attempt++) {
      try {
        const response = await this.client.request(config);
        return response.data;
      } catch (error) {
        lastError = error as AxiosError;
        
        if (attempt === this.retryConfig.retries || !this.retryConfig.retryCondition(lastError)) {
          throw lastError;
        }
        
        const delay = this.getRetryDelay(attempt);
        
        if (this.retryConfig.onRetry) {
          this.retryConfig.onRetry(attempt + 1, lastError);
        }
        
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    
    throw lastError!;
  }

  /**
   * Set or update the API key
   */
  public setApiKey(apiKey: string): void {
    this.apiKey = apiKey;
    this.client.defaults.headers.Authorization = `Bearer ${apiKey}`;
  }

  /**
   * Set or update the base URL
   */
  public setBaseURL(baseURL: string): void {
    this.client.defaults.baseURL = baseURL.replace(/\/$/, '');
  }

  /**
   * Health check endpoint
   */
  public async health(): Promise<HealthResponse> {
    return this.makeRequest<HealthResponse>({
      method: 'GET',
      url: '/health'
    });
  }

  /**
   * Execute a task (non-streaming)
   */
  public async execute(request: ExecuteRequest): Promise<ExecuteResponse> {
    return this.makeRequest<ExecuteResponse>({
      method: 'POST',
      url: '/v1/execute',
      data: request
    });
  }

  /**
   * Execute a task with streaming support using SSE
   */
  public async executeStream(
    request: ExecuteRequest,
    onEvent: (event: StreamEvent) => void
  ): Promise<ExecuteResponse> {
    return new Promise((resolve, reject) => {
      let finalResponse: ExecuteResponse | null = null;
      let buffer = '';

      // Create a custom parser for SSE events
      const parseSSEEvent = (line: string): StreamEvent | null => {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.substring(6));
            return data as StreamEvent;
          } catch (error) {
            console.warn('Failed to parse SSE event:', error);
            return null;
          }
        }
        return null;
      };

      // Make streaming request with retry logic
      const makeStreamingRequest = async (attempt: number = 0): Promise<void> => {
        try {
          const response = await this.client.post('/v1/execute/stream', request, {
            responseType: 'stream',
            headers: {
              Accept: 'text/event-stream',
              'Cache-Control': 'no-cache'
            }
          });

          response.data.on('data', (chunk: Buffer) => {
            buffer += chunk.toString();
            const lines = buffer.split('\n');
            buffer = lines.pop() || ''; // Keep incomplete line in buffer

            for (const line of lines) {
              const event = parseSSEEvent(line);
              if (event) {
                onEvent(event);

                if (event.type === 'complete' && event.data) {
                  finalResponse = event.data;
                  if (finalResponse) {
                    resolve(finalResponse);
                  } else {
                    reject(new MonkeyCoderError('Invalid completion event data', 'STREAM_INVALID'));
                  }
                  return;
                } else if (event.type === 'error') {
                  reject(new MonkeyCoderError(
                    event.error?.message || 'Stream error',
                    event.error?.code
                  ));
                  return;
                }
              }
            }
          });

          response.data.on('end', () => {
            if (buffer.trim()) {
              const event = parseSSEEvent(`data: ${buffer}`);
              if (event) {
                onEvent(event);
              }
            }

            if (!finalResponse) {
              reject(new MonkeyCoderError('Stream ended without completion event', 'STREAM_INCOMPLETE'));
            }
          });

          response.data.on('error', (error: Error) => {
            const axiosError = error as AxiosError;
            if (attempt < this.retryConfig.retries && this.retryConfig.retryCondition(axiosError)) {
              const delay = this.getRetryDelay(attempt);
              if (this.retryConfig.onRetry) {
                this.retryConfig.onRetry(attempt + 1, axiosError);
              }
              setTimeout(() => makeStreamingRequest(attempt + 1), delay);
            } else {
              reject(error);
            }
          });
        } catch (error) {
          const axiosError = error as AxiosError;
          if (attempt < this.retryConfig.retries && this.retryConfig.retryCondition(axiosError)) {
            const delay = this.getRetryDelay(attempt);
            if (this.retryConfig.onRetry) {
              this.retryConfig.onRetry(attempt + 1, axiosError);
            }
            setTimeout(() => makeStreamingRequest(attempt + 1), delay);
          } else {
            reject(error);
          }
        }
      };

      makeStreamingRequest();
    });
  }

  /**
   * Get billing/usage information
   */
  public async getUsage(params?: UsageRequest): Promise<any> {
    return this.makeRequest<any>({
      method: 'GET',
      url: '/v1/billing/usage',
      params
    });
  }

  /**
   * List available providers
   */
  public async listProviders(): Promise<Record<string, any>> {
    return this.makeRequest<Record<string, any>>({
      method: 'GET',
      url: '/v1/providers'
    });
  }

  /**
   * List available models
   */
  public async listModels(provider?: ProviderType): Promise<Record<string, any>> {
    return this.makeRequest<Record<string, any>>({
      method: 'GET',
      url: '/v1/models',
      params: provider ? { provider } : undefined
    });
  }

  /**
   * Debug routing decisions for a request
   */
  public async debugRouting(request: ExecuteRequest): Promise<Record<string, any>> {
    return this.makeRequest<Record<string, any>>({
      method: 'POST',
      url: '/v1/router/debug',
      data: request
    });
  }
}

// Export the client as default
export default MonkeyCoderClient;

// Helper functions for creating common request configurations
export const createExecuteRequest = (
  taskType: TaskType,
  prompt: string,
  context: ExecutionContext,
  persona: PersonaType = 'developer',
  options: Partial<ExecuteRequest> = {}
): ExecuteRequest => ({
  task_type: taskType,
  prompt,
  context,
  persona_config: {
    persona,
    ...options.persona_config
  },
  ...options
});

// Convenience methods for common tasks
export const createCodeGenerationRequest = (
  prompt: string,
  userId: string,
  options: Partial<ExecuteRequest> = {}
): ExecuteRequest => createExecuteRequest(
  'code_generation',
  prompt,
  { user_id: userId, ...options.context },
  'developer',
  options
);

export const createCodeReviewRequest = (
  prompt: string,
  userId: string,
  files: Array<{ path: string; content: string; type?: string }>,
  options: Partial<ExecuteRequest> = {}
): ExecuteRequest => createExecuteRequest(
  'code_review',
  prompt,
  { user_id: userId, ...options.context },
  'reviewer',
  { files, ...options }
);

// Additional helper for creating file data
export const createFileData = (
  path: string,
  content: string,
  type?: string
): { path: string; content: string; type?: string } => ({ path, content, type });
