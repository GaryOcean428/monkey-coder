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
      if (process.env.NEXT_PUBLIC_API_URL) {
        this.baseUrl = process.env.NEXT_PUBLIC_API_URL;
      } else if (window.location.hostname === 'localhost') {
        this.baseUrl = 'http://localhost:8000';
      } else if (window.location.hostname.includes('railway.app')) {
        // Frontend is at monkey-coder.up.railway.app
        // Backend is at monkey-coder-backend-production.up.railway.app
        const protocol = window.location.protocol;
        const backendHost = window.location.hostname.replace(/^[^.]+/, 'monkey-coder-backend-production');
        this.baseUrl = `${protocol}//${backendHost}`;
      } else if (window.location.hostname.includes('fastmonkey.au')) {
        // Custom domain - backend is on the same domain
        this.baseUrl = window.location.origin;
      } else {
        // Fallback for other domains
        this.baseUrl = window.location.origin;
      }
    } else {
      // Server-side: use internal API URL if available
      this.baseUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
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
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } else {
          // Response is not JSON (likely HTML error page)
          const text = await response.text();
          if (text.includes('<!DOCTYPE') || text.includes('<html')) {
            errorMessage = `API endpoint not found or returned HTML instead of JSON. Check that the backend service is running and the API URL is correct. (URL: ${url})`;
          } else {
            errorMessage = `${errorMessage} (Received non-JSON response)`;
          }
        }
      } catch {
        // If parsing fails, use the status text
        errorMessage = `${errorMessage} (Failed to parse error response)`;
      }
      throw new Error(errorMessage);
    }

    // Handle empty responses
    const text = await response.text();
    if (!text) {
      return {} as T;
    }
    
    // Check if response is JSON
    try {
      return JSON.parse(text);
    } catch {
      // If it's not JSON, check if it's HTML
      if (text.includes('<!DOCTYPE') || text.includes('<html')) {
        throw new Error(`API returned HTML instead of JSON. Check that the backend service is running and the API URL is correct. (URL: ${url})`);
      }
      throw new Error(`Failed to parse API response as JSON (URL: ${url})`);
    }
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
