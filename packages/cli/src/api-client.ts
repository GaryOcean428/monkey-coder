/**
 * API Client for Monkey Coder Core
 * Handles REST API calls and Server-Sent Events streaming
 */

import axios, { AxiosInstance } from 'axios';
import { createParser } from 'eventsource-parser';
import { ExecuteRequest, ExecuteResponse, StreamEvent } from './types.js';

export class MonkeyCoderAPIClient {
  private client: AxiosInstance;
  private baseUrl: string;
  private apiKey: string;

  constructor(baseUrl: string = 'http://localhost:8000', apiKey: string = '') {
    this.baseUrl = baseUrl.replace(/\/$/, ''); // Remove trailing slash
    this.apiKey = apiKey;
    
    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: 300000, // 5 minutes default timeout
      headers: {
        'Content-Type': 'application/json',
        // TODO: The User-Agent is hardcoded. This should be dynamically managed,
        // possibly from package.json, to avoid version mismatches with the API.
        // Reference: Analysis document section on request-building.
        'User-Agent': 'monkey-coder-cli/1.0.0',
      },
    });

    // Add auth interceptor if API key is provided
    if (this.apiKey) {
      this.client.interceptors.request.use((config) => {
        config.headers.Authorization = `Bearer ${this.apiKey}`;
        return config;
      });
    }

    // Add error handling interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response) {
          // Server responded with error status
          const status = error.response.status;
          const message = error.response.data?.detail || error.response.data?.message || error.message;
          throw new Error(`API Error (${status}): ${message}`);
        } else if (error.request) {
          // Request made but no response received
          throw new Error('No response from server. Please check if the service is running.');
        } else {
          // Something else happened
          throw new Error(`Request error: ${error.message}`);
        }
      },
    );
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<{ status: string; version: string; components: Record<string, string> }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  /**
   * Execute a task (non-streaming)
   */
  async execute(request: ExecuteRequest): Promise<ExecuteResponse> {
    const response = await this.client.post('/api/v1/execute', request);
    return response.data;
  }

  /**
   * Execute a task with streaming support using SSE
   */
  async executeStream(
    request: ExecuteRequest,
    onEvent: (event: StreamEvent) => void,
  ): Promise<ExecuteResponse> {
    return new Promise((resolve, reject) => {
      let finalResponse: ExecuteResponse | null = null;
      let buffer = '';

      // Create SSE parser
      const parser = createParser({
        onEvent: (event) => {
          try {
            const data = JSON.parse(event.data || '{}');
            
            // Handle different event types
            switch (data.type) {
              case 'start':
                onEvent({
                  type: 'start',
                  data: data.data,
                });
                break;
              
              case 'progress':
                onEvent({
                  type: 'progress',
                  progress: data.progress,
                });
                break;
              
              case 'result':
                onEvent({
                  type: 'result',
                  data: data.data,
                });
                break;
              
              case 'error':
                onEvent({
                  type: 'error',
                  error: data.error,
                });
                reject(new Error(data.error.message));
                return;
              
              case 'complete':
                finalResponse = data.data;
                onEvent({
                  type: 'complete',
                  data: finalResponse,
                });
                if (finalResponse) {
                  resolve(finalResponse);
                }
                return;
            }
          } catch (error) {
            console.error('Failed to parse SSE event:', error);
          }
        }
      });

      // Make streaming request
      this.client
        .post('/api/v1/execute/stream', request, {
          responseType: 'stream',
          headers: {
            Accept: 'text/event-stream',
            'Cache-Control': 'no-cache',
          },
        })
        .then((response) => {
          response.data.on('data', (chunk: Buffer) => {
            buffer += chunk.toString();
            // Process complete lines
            const lines = buffer.split('\n');
            buffer = lines.pop() || ''; // Keep incomplete line in buffer
            
            for (const line of lines) {
              parser.feed(line + '\n');
            }
          });

          response.data.on('end', () => {
            // Process any remaining data in buffer
            if (buffer.trim()) {
              parser.feed(buffer + '\n');
            }
            
            if (!finalResponse) {
              reject(new Error('Stream ended without completion event'));
            }
          });

          response.data.on('error', (error: Error) => {
            reject(error);
          });
        })
        .catch((error) => {
          reject(error);
        });
    });
  }

  /**
   * Get billing/usage information
   */
  async getUsage(params?: {
    startDate?: string;
    endDate?: string;
    granularity?: string;
  }): Promise<any> {
    const response = await this.client.get('/api/v1/billing/usage', { params });
    return response.data;
  }

  /**
   * Set API key for authentication
   */
  setApiKey(apiKey: string): void {
    this.apiKey = apiKey;
    this.client.defaults.headers.Authorization = `Bearer ${apiKey}`;
  }

  /**
   * Set base URL for the API
   */
  setBaseUrl(baseUrl: string): void {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.client.defaults.baseURL = this.baseUrl;
  }

  /**
   * Authenticate user with email and password
   */
  async authenticate(credentials: { email: string; password: string }): Promise<any> {
    const response = await this.client.post('/api/v1/auth/login', credentials);
    return response.data;
  }

  /**
   * Logout current user
   */
  async logout(): Promise<void> {
    await this.client.post('/api/v1/auth/logout');
  }

  /**
   * Get current user status
   */
  async getUserStatus(): Promise<any> {
    const response = await this.client.get('/api/v1/auth/status');
    return response.data;
  }

  /**
   * Refresh authentication token
   */
  async refreshToken(refreshToken: string): Promise<any> {
    const response = await this.client.post('/api/v1/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  }

  /**
   * Create billing portal session
   */
  async createBillingPortalSession(data: { return_url: string }): Promise<any> {
    const response = await this.client.post('/api/v1/billing/portal', data);
    return response.data;
  }

  /**
   * Create payment session for credits
   */
  async createPaymentSession(data: {
    amount: number;
    description: string;
    success_url: string;
    cancel_url: string;
  }): Promise<any> {
    const response = await this.client.post('/api/v1/billing/payment', data);
    return response.data;
  }

  /**
   * Generic HTTP methods for MCP endpoints
   */
  async get(url: string, config?: any): Promise<any> {
    return this.client.get(url, config);
  }

  async post(url: string, data?: any, config?: any): Promise<any> {
    return this.client.post(url, data, config);
  }

  async put(url: string, data?: any, config?: any): Promise<any> {
    return this.client.put(url, data, config);
  }

  async delete(url: string, config?: any): Promise<any> {
    return this.client.delete(url, config);
  }

  async patch(url: string, data?: any, config?: any): Promise<any> {
    return this.client.patch(url, data, config);
  }
}
