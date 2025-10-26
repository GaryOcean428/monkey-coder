/**
 * API Client for making requests to the backend
 * Supports both local development and production deployment
 */

interface AuthResponse {
  access_token: string;
  token_type: string;
  user?: {
    id: string;
    email: string;
    username?: string;
  };
}

class APIClient {
  private baseUrl: string;

  constructor() {
    // Determine backend URL based on environment
    if (typeof window !== 'undefined') {
      // Client-side: use environment variable or infer from current domain
      this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 
                     (window.location.hostname === 'localhost' 
                       ? 'http://localhost:8000' 
                       : '');
    } else {
      // Server-side: use internal API URL if available
      this.baseUrl = process.env.API_URL || 'http://localhost:8000';
    }
  }

  private async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    
    const response = await fetch(url, {
      ...options,
      credentials: 'include', // Important for cookies
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      let errorMessage = `Request failed: ${response.statusText}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        // If response isn't JSON, use status text
      }
      throw new Error(errorMessage);
    }

    // Handle empty responses
    const text = await response.text();
    return text ? JSON.parse(text) : {} as T;
  }

  // Auth endpoints with cookie support
  async login(email: string, password: string): Promise<AuthResponse> {
    return this.request<AuthResponse>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async logout(): Promise<void> {
    return this.request('/api/v1/auth/logout', {
      method: 'POST',
    });
  }

  async getAuthStatus(): Promise<{ authenticated: boolean; user?: any }> {
    return this.request('/api/v1/auth/status', {
      method: 'GET',
    });
  }

  async refreshToken(): Promise<AuthResponse> {
    return this.request('/api/v1/auth/refresh', {
      method: 'POST',
    });
  }

  async signup(data: {
    email: string;
    password: string;
    username?: string;
    name?: string;
  }): Promise<AuthResponse> {
    return this.request<AuthResponse>('/api/v1/auth/signup', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Execute endpoint
  async execute(prompt: string, options?: any) {
    return this.request('/api/v1/execute', {
      method: 'POST',
      body: JSON.stringify({ prompt, ...options }),
    });
  }

  // Billing endpoints
  async getUsage() {
    return this.request('/api/v1/billing/usage', {
      method: 'GET',
    });
  }

  async createBillingPortal() {
    return this.request('/api/v1/billing/portal', {
      method: 'POST',
    });
  }

  // Provider endpoints
  async getProviders() {
    return this.request('/api/v1/providers', {
      method: 'GET',
    });
  }

  async getModels() {
    return this.request('/api/v1/models', {
      method: 'GET',
    });
  }

  // API Key endpoints
  async createAPIKey(name: string, expiresIn?: number) {
    return this.request('/api/v1/auth/keys', {
      method: 'POST',
      body: JSON.stringify({ name, expires_in: expiresIn }),
    });
  }

  async getAPIKeys() {
    return this.request('/api/v1/auth/keys', {
      method: 'GET',
    });
  }

  async deleteAPIKey(keyId: string) {
    return this.request(`/api/v1/auth/keys/${keyId}`, {
      method: 'DELETE',
    });
  }

  async getAPIKeyStats() {
    return this.request('/api/v1/auth/keys/stats', {
      method: 'GET',
    });
  }
}

// Export singleton instance
export const apiClient = new APIClient();

// Export class for testing
export default APIClient;
