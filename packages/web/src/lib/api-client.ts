/**
 * API Client for making requests to the backend
 * Uses relative paths to work both locally and in production
 */

class APIClient {
  private baseUrl: string

  constructor() {
    // In production (static export), use relative paths
    // The backend serves the frontend, so API calls go to the same domain
    this.baseUrl = ''
  }

  private async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })

    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || `Request failed: ${response.statusText}`)
    }

    return response.json()
  }

  // Auth endpoints
  async login(email: string, password: string) {
    return this.request('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
  }

  async logout() {
    return this.request('/api/v1/auth/logout', {
      method: 'POST',
    })
  }

  async getAuthStatus() {
    return this.request('/api/v1/auth/status', {
      method: 'GET',
    })
  }

  async refreshToken() {
    return this.request('/api/v1/auth/refresh', {
      method: 'POST',
    })
  }

  // Note: Signup endpoint doesn't exist in backend yet
  // This is a placeholder for when it's implemented
  async signup(data: {
    email: string
    password: string
    username?: string
    name?: string
  }) {
    // TODO: Backend needs /api/v1/auth/signup endpoint
    throw new Error('Signup not yet implemented in backend')
  }

  // Execute endpoint
  async execute(prompt: string, options?: any) {
    return this.request('/api/v1/execute', {
      method: 'POST',
      body: JSON.stringify({ prompt, ...options }),
    })
  }

  // Billing endpoints
  async getUsage() {
    return this.request('/api/v1/billing/usage', {
      method: 'GET',
    })
  }

  async createBillingPortal() {
    return this.request('/api/v1/billing/portal', {
      method: 'POST',
    })
  }

  // Provider endpoints
  async getProviders() {
    return this.request('/api/v1/providers', {
      method: 'GET',
    })
  }

  async getModels() {
    return this.request('/api/v1/models', {
      method: 'GET',
    })
  }

  // API Key endpoints
  async createAPIKey(name: string, expiresIn?: number) {
    return this.request('/api/v1/auth/keys', {
      method: 'POST',
      body: JSON.stringify({ name, expires_in: expiresIn }),
    })
  }

  async getAPIKeys() {
    return this.request('/api/v1/auth/keys', {
      method: 'GET',
    })
  }

  async deleteAPIKey(keyId: string) {
    return this.request(`/api/v1/auth/keys/${keyId}`, {
      method: 'DELETE',
    })
  }

  async getAPIKeyStats() {
    return this.request('/api/v1/auth/keys/stats', {
      method: 'GET',
    })
  }
}

// Export singleton instance
export const apiClient = new APIClient()

// Export class for testing
export default APIClient