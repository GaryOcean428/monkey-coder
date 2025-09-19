/**
 * API Client for Monkey Coder Core
 * Handles REST API calls and Server-Sent Events streaming
 */

import { createParser } from 'eventsource-parser';

import { ExecuteRequest, ExecuteResponse, StreamEvent } from './types.js';


export class MonkeyCoderAPIClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(baseUrl: string = process.env.MONKEY_CODER_BASE_URL || 'http://localhost:8000', apiKey: string = '') {
    this.baseUrl = baseUrl.replace(/\/$/, ''); // Remove trailing slash
    this.apiKey = apiKey;
  }

  private async makeRequest(url: string, options: RequestInit = {}): Promise<Response> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'User-Agent': 'monkey-coder-cli/1.0.0',
      ...options.headers as Record<string, string>,
    };

    if (this.apiKey) {
      headers.Authorization = `Bearer ${this.apiKey}`;
    }

    console.log('DEBUG: Request headers:', JSON.stringify(headers, null, 2));
    console.log('DEBUG: Request options:', JSON.stringify({
      ...options,
      headers,
    }, null, 2));

    const response = await fetch(`${this.baseUrl}${url}`, {
      ...options,
      headers,
    });

    console.log('DEBUG: Response status:', response.status);
    const responseHeaders: Record<string, string> = {};
    response.headers.forEach((value, key) => {
      responseHeaders[key] = value;
    });
    console.log('DEBUG: Response headers:', JSON.stringify(responseHeaders, null, 2));

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
        console.log('DEBUG: Error response data:', JSON.stringify(errorData, null, 2));
      } catch (_e) {
        console.log('DEBUG: Could not parse error response as JSON');
        errorData = {};
      }
      const message = errorData.detail || errorData.message || `HTTP ${response.status}`;
      throw new Error(`API Error (${response.status}): ${message}`);
    }

    return response;
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<{ status: string; version: string; components: Record<string, string> }> {
    const response = await this.makeRequest('/health');
    return response.json();
  }

  /**
   * Execute a task (non-streaming)
   */
  async execute(request: ExecuteRequest): Promise<ExecuteResponse> {
    console.log('DEBUG: Sending request:', JSON.stringify(request, null, 2));
    const response = await this.makeRequest('/api/v1/execute', {
      method: 'POST',
      body: JSON.stringify(request),
    });
    return response.json();
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
      fetch(`${this.baseUrl}/api/v1/execute/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Authorization': `Bearer ${this.apiKey}`,
        },
        body: JSON.stringify(request),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
          }

          if (!response.body) {
            throw new Error('No response body');
          }

          const reader = response.body.getReader();
          const decoder = new TextDecoder();

          function readStream(): Promise<void> {
            return reader.read().then(({ done, value }) => {
              if (done) {
                // Process any remaining data in buffer
                if (buffer.trim()) {
                  parser.feed(buffer + '\n');
                }

                if (!finalResponse) {
                  reject(new Error('Stream ended without completion event'));
                }
                return;
              }

              buffer += decoder.decode(value, { stream: true });
              // Process complete lines
              const lines = buffer.split('\n');
              buffer = lines.pop() || ''; // Keep incomplete line in buffer

              for (const line of lines) {
                parser.feed(line + '\n');
              }

              return readStream();
            });
          }

          return readStream();
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
    const queryString = params ? '?' + new URLSearchParams(params).toString() : '';
    const response = await this.makeRequest(`/api/v1/billing/usage${queryString}`);
    return response.json();
  }

  /**
   * Set API key for authentication
   */
  setApiKey(apiKey: string): void {
    this.apiKey = apiKey;
  }

  /**
   * Set base URL for the API
   */
  setBaseUrl(baseUrl: string): void {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  /**
   * Authenticate user with email and password
   */
  async authenticate(credentials: { email: string; password: string }): Promise<any> {
    const response = await this.makeRequest('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    return response.json();
  }

  /**
   * Logout current user
   */
  async logout(): Promise<void> {
    await this.makeRequest('/api/v1/auth/logout', {
      method: 'POST',
    });
  }

  /**
   * Get current user status
   */
  async getUserStatus(): Promise<any> {
    const response = await this.makeRequest('/api/v1/auth/status');
    return response.json();
  }

  /**
   * Refresh authentication token
   */
  async refreshToken(refreshToken: string): Promise<any> {
    const response = await this.makeRequest('/api/v1/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    return response.json();
  }

  /**
   * Create billing portal session
   */
  async createBillingPortalSession(data: { return_url: string }): Promise<any> {
    const response = await this.makeRequest('/api/v1/billing/portal', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return response.json();
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
    const response = await this.makeRequest('/api/v1/billing/payment', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return response.json();
  }

  /**
   * Generic HTTP methods for MCP endpoints
   */
  async get(url: string, config?: any): Promise<any> {
    const response = await this.makeRequest(url, {
      method: 'GET',
      ...config,
    });
    return response.json();
  }

  async post(url: string, data?: any, config?: any): Promise<any> {
    const response = await this.makeRequest(url, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
      ...config,
    });
    return response.json();
  }

  async put(url: string, data?: any, config?: any): Promise<any> {
    const response = await this.makeRequest(url, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
      ...config,
    });
    return response.json();
  }

  async delete(url: string, config?: any): Promise<any> {
    const response = await this.makeRequest(url, {
      method: 'DELETE',
      ...config,
    });
    return response.json();
  }

  async patch(url: string, data?: any, config?: any): Promise<any> {
    const response = await this.makeRequest(url, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
      ...config,
    });
    return response.json();
  }
}
