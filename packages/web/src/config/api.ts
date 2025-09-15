/**
 * API Configuration for secure connections and CORS handling
 */

/**
 * Get API base URL for the current environment
 */
export function getApiBaseUrl(): string {
  // In browser, detect the current origin
  if (typeof window !== 'undefined') {
    const { protocol, hostname, port } = window.location;
    
    // Production check - if we're on Railway or fastmonkey domain
    if (hostname.includes('railway.app') || hostname.includes('fastmonkey.au')) {
      return `${protocol}//${hostname}`;
    }
    
    // Development - use current origin
    return window.location.origin;
  }
  
  // Server-side fallback
  return process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
}

/**
 * Get WebSocket URL for the current environment
 */
export function getWebSocketUrl(): string {
  // In browser, detect the current origin
  if (typeof window !== 'undefined') {
    const { protocol, hostname, port } = window.location;
    
    // Production check - if we're on Railway or fastmonkey domain
    if (hostname.includes('railway.app') || hostname.includes('fastmonkey.au')) {
      const wsProtocol = protocol === 'https:' ? 'wss:' : 'ws:';
      return `${wsProtocol}//${hostname}`;
    }
    
    // Development - use WebSocket protocol
    const wsProtocol = protocol === 'https:' ? 'wss:' : 'ws:';
    return `${wsProtocol}//${hostname}${port ? `:${port}` : ''}`;
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
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    throw new APIError(
      errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
      response.status,
      response.statusText
    );
  }

  return response.json();
}