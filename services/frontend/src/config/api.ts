/**
 * API Configuration for secure connections and CORS handling
 */

/**
 * Get API base URL for the current environment
 */
export function getApiBaseUrl(): string {
  // Always prefer the explicitly set environment variable
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  
  // In browser, use environment variable or fallback to backend service
  if (typeof window !== 'undefined') {
    const { protocol, hostname } = window.location;
    
    // Production check - if we're on Railway or fastmonkey domain
    // In production, the backend is a separate service
    if (hostname.includes('railway.app')) {
      // Frontend is at monkey-coder.up.railway.app
      // Backend is at monkey-coder-backend-production.up.railway.app
      const backendHost = hostname.replace(/^[^.]+/, 'monkey-coder-backend-production');
      return `${protocol}//${backendHost}`;
    }
    
    if (hostname.includes('fastmonkey.au')) {
      // Custom domain - use the same domain (backend handles routing)
      return `${protocol}//${hostname}`;
    }
    
    // Development - use localhost backend
    return 'http://localhost:8000';
  }
  
  // Server-side fallback
  return process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
}

/**
 * Get WebSocket URL for the current environment
 */
export function getWebSocketUrl(): string {
  // Always prefer the explicitly set environment variable
  if (process.env.NEXT_PUBLIC_WS_URL) {
    return process.env.NEXT_PUBLIC_WS_URL;
  }
  
  // In browser, use environment variable or fallback to backend service
  if (typeof window !== 'undefined') {
    const { protocol, hostname } = window.location;
    const wsProtocol = protocol === 'https:' ? 'wss:' : 'ws:';
    
    // Production check - if we're on Railway or fastmonkey domain
    if (hostname.includes('railway.app')) {
      // Frontend is at monkey-coder.up.railway.app
      // Backend is at monkey-coder-backend-production.up.railway.app
      const backendHost = hostname.replace(/^[^.]+/, 'monkey-coder-backend-production');
      return `${wsProtocol}//${backendHost}`;
    }
    
    if (hostname.includes('fastmonkey.au')) {
      // Custom domain - use the same domain (backend handles routing)
      return `${wsProtocol}//${hostname}`;
    }
    
    // Development - use localhost backend
    return 'ws://localhost:8000';
  }
  
  // Server-side fallback
  return process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
}

/**
 * API configuration object
 */
export const API_CONFIG = {
  baseUrl: getApiBaseUrl(),
  wsUrl: getWebSocketUrl(),
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  credentials: 'include' as RequestCredentials, // Enable cookies
};

/**
 * Create a fetch wrapper with proper credentials and error handling
 */
export async function apiFetch(endpoint: string, options: RequestInit = {}): Promise<Response> {
  const url = `${API_CONFIG.baseUrl}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...API_CONFIG.headers,
      ...options.headers,
    },
    credentials: API_CONFIG.credentials,
  });

  return response;
}

/**
 * API error class
 */
export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public statusText: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

/**
 * Handle API response and throw errors if needed
 */
export async function handleApiResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    
    try {
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } else {
        // Response is not JSON (likely HTML error page)
        const text = await response.text();
        if (text.includes('<!DOCTYPE') || text.includes('<html')) {
          errorMessage = `API endpoint not found or returned HTML instead of JSON. Check that the backend service is running and the API URL is correct.`;
        } else {
          errorMessage = `${errorMessage} (Received non-JSON response)`;
        }
      }
    } catch {
      // If parsing fails, use the status text
    }
    
    throw new APIError(
      errorMessage,
      response.status,
      response.statusText
    );
  }

  // Parse JSON response
  const text = await response.text();
  if (!text) {
    return {} as T;
  }
  
  try {
    return JSON.parse(text);
  } catch {
    // If it's not JSON, check if it's HTML
    if (text.includes('<!DOCTYPE') || text.includes('<html')) {
      throw new APIError(
        'API returned HTML instead of JSON. Check that the backend service is running and the API URL is correct.',
        response.status,
        response.statusText
      );
    }
    throw new APIError(
      'Failed to parse API response as JSON',
      response.status,
      response.statusText
    );
  }
}