/**
 * Authentication utilities for secure cookie-based authentication
 * Replaces localStorage with httpOnly cookies for better security
 */

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  username?: string;
  credits: number;
  subscription_tier: string;
  is_developer: boolean;
  roles: string[];
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: AuthUser;
}

/**
 * Login user with email and password
 * Uses httpOnly cookies for token storage (server-side)
 */
export async function login(email: string, password: string): Promise<AuthResponse> {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include', // Important for httpOnly cookies
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  const result = await response.json();

  // Store user info in memory/state only (no sensitive tokens)
  // The actual tokens are stored in httpOnly cookies by the server
  return result;
}

/**
 * Register new user
 */
export async function signup(data: {
  username: string;
  name: string;
  email: string;
  password: string;
  plan?: string;
}): Promise<AuthResponse> {
  const response = await fetch('/api/v1/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include', // Important for httpOnly cookies
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Signup failed');
  }

  const result = await response.json();
  return result;
}

/**
 * Logout user
 * Clears httpOnly cookies on server-side
 */
export async function logout(): Promise<void> {
  const response = await fetch('/api/v1/auth/logout', {
    method: 'POST',
    credentials: 'include', // Important for httpOnly cookies
  });

  if (!response.ok) {
    console.error('Logout failed');
  }
}

/**
 * Get current user authentication status
 * Relies on httpOnly cookies for authentication
 */
export async function getUserStatus(): Promise<{
  authenticated: boolean;
  user?: AuthUser;
  session_expires?: string;
}> {
  try {
    const response = await fetch('/api/v1/auth/status', {
      credentials: 'include', // Important for httpOnly cookies
    });

    if (!response.ok) {
      return { authenticated: false };
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Failed to get user status:', error);
    return { authenticated: false };
  }
}

/**
 * Refresh access token using refresh token stored in httpOnly cookie
 */
export async function refreshToken(): Promise<AuthResponse | null> {
  try {
    const response = await fetch('/api/v1/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include', // Important for httpOnly cookies
    });

    if (!response.ok) {
      return null;
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Token refresh failed:', error);
    return null;
  }
}

/**
 * Check if user is authenticated
 * This is a client-side check, actual authentication is done via httpOnly cookies
 */
export function isAuthenticated(): boolean {
  // We can't directly check httpOnly cookies from JavaScript
  // This is a feature, not a bug - it prevents XSS attacks
  // We rely on the server to validate authentication
  return false; // Default to not authenticated, let server confirm
}

/**
 * Clear any remaining localStorage tokens (migration cleanup)
 */
export function clearLegacyTokens(): void {
  try {
    localStorage.removeItem('authToken');
    console.log('Cleared legacy localStorage tokens');
  } catch (error) {
    console.error('Failed to clear legacy tokens:', error);
  }
}
