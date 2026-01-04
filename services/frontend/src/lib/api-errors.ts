/**
 * Centralized API Error Handler
 * 
 * Provides consistent error handling across all API calls.
 */

import { ApiError, ApiResponse } from '@/types'

/**
 * Custom API Error class
 */
export class APIError extends Error {
  constructor(
    public code: string,
    message: string,
    public status: number,
    public details?: Record<string, unknown>
  ) {
    super(message)
    this.name = 'APIError'
  }
}

/**
 * Parse error from various sources
 */
export function parseApiError(error: unknown): ApiError {
  // If it's already our custom error
  if (error instanceof APIError) {
    return {
      code: error.code,
      message: error.message,
      details: error.details,
    }
  }

  // If it's a fetch Response error
  if (error instanceof Response) {
    return {
      code: `HTTP_${error.status}`,
      message: error.statusText || 'Request failed',
      details: { status: error.status },
    }
  }

  // If it's a standard Error
  if (error instanceof Error) {
    return {
      code: 'UNKNOWN_ERROR',
      message: error.message,
    }
  }

  // If it's an object with error properties
  if (typeof error === 'object' && error !== null) {
    const err = error as Record<string, unknown>
    return {
      code: (err.code as string) || 'UNKNOWN_ERROR',
      message: (err.message as string) || 'An unknown error occurred',
      details: err.details as Record<string, unknown>,
    }
  }

  // Fallback
  return {
    code: 'UNKNOWN_ERROR',
    message: 'An unknown error occurred',
  }
}

/**
 * Handle API errors consistently
 */
export function handleApiError(error: unknown): never {
  const parsed = parseApiError(error)
  
  // Log error for debugging
  if (process.env.NODE_ENV === 'development') {
    console.error('API Error:', parsed)
  }

  // Send to error tracking service (e.g., Sentry)
  if (typeof window !== 'undefined' && (window as any).Sentry) {
    (window as any).Sentry.captureException(error, {
      contexts: {
        api: parsed,
      },
    })
  }

  throw new APIError(
    parsed.code,
    parsed.message,
    getStatusFromCode(parsed.code),
    parsed.details
  )
}

/**
 * Get HTTP status code from error code
 */
function getStatusFromCode(code: string): number {
  if (code.startsWith('HTTP_')) {
    const status = parseInt(code.replace('HTTP_', ''), 10)
    if (!isNaN(status)) return status
  }

  // Map common error codes to HTTP status
  const statusMap: Record<string, number> = {
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404,
    VALIDATION_ERROR: 400,
    SERVER_ERROR: 500,
    NETWORK_ERROR: 503,
    TIMEOUT: 408,
  }

  return statusMap[code] || 500
}

/**
 * Format error message for user display
 */
export function formatErrorMessage(error: unknown): string {
  const parsed = parseApiError(error)

  // User-friendly error messages
  const friendlyMessages: Record<string, string> = {
    UNAUTHORIZED: 'Please log in to continue',
    FORBIDDEN: 'You don\'t have permission to perform this action',
    NOT_FOUND: 'The requested resource was not found',
    VALIDATION_ERROR: 'Please check your input and try again',
    SERVER_ERROR: 'Something went wrong on our end. Please try again later',
    NETWORK_ERROR: 'Network error. Please check your connection',
    TIMEOUT: 'Request timed out. Please try again',
  }

  return friendlyMessages[parsed.code] || parsed.message || 'An error occurred'
}

/**
 * Check if error is retriable
 */
export function isRetriableError(error: unknown): boolean {
  const parsed = parseApiError(error)
  
  const retriableCodes = [
    'NETWORK_ERROR',
    'TIMEOUT',
    'HTTP_408',
    'HTTP_429', // Rate limit
    'HTTP_500',
    'HTTP_502',
    'HTTP_503',
    'HTTP_504',
  ]

  return retriableCodes.includes(parsed.code)
}

/**
 * Retry an API call with exponential backoff
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: {
    maxRetries?: number
    initialDelay?: number
    maxDelay?: number
    backoffMultiplier?: number
  } = {}
): Promise<T> {
  const {
    maxRetries = 3,
    initialDelay = 1000,
    maxDelay = 10000,
    backoffMultiplier = 2,
  } = options

  let lastError: unknown
  let delay = initialDelay

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error

      // Don't retry if error is not retriable or we're out of retries
      if (!isRetriableError(error) || attempt === maxRetries) {
        throw error
      }

      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, delay))
      
      // Increase delay for next attempt
      delay = Math.min(delay * backoffMultiplier, maxDelay)
    }
  }

  throw lastError
}

/**
 * Create a standardized API response
 */
export function createApiResponse<T>(
  data?: T,
  error?: ApiError,
  status = 200,
  message?: string
): ApiResponse<T> {
  return {
    data,
    error,
    status,
    message,
  }
}
