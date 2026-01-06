/**
 * Security Middleware for API Routes
 * 
 * Provides rate limiting, CSRF protection, and input validation
 */

import { NextRequest, NextResponse } from 'next/server'

// Simple in-memory rate limiter (use Redis in production)
const rateLimitStore = new Map<string, { count: number; resetAt: number }>()

export interface RateLimitConfig {
  /**
   * Maximum requests allowed in the time window
   */
  maxRequests: number
  
  /**
   * Time window in milliseconds
   */
  windowMs: number
  
  /**
   * Custom message for rate limit exceeded
   */
  message?: string
}

/**
 * Rate limiting middleware
 * 
 * @example
 * ```ts
 * export async function POST(request: NextRequest) {
 *   const rateLimitResponse = await rateLimit(request, {
 *     maxRequests: 10,
 *     windowMs: 60 * 1000 // 1 minute
 *   })
 *   
 *   if (rateLimitResponse) return rateLimitResponse
 *   
 *   // Handle request...
 * }
 * ```
 */
export async function rateLimit(
  request: NextRequest,
  config: RateLimitConfig
): Promise<NextResponse | null> {
  const { maxRequests, windowMs, message } = config
  
  // Get client identifier (IP address)
  const identifier = 
    request.headers.get('x-forwarded-for') ||
    request.headers.get('x-real-ip') ||
    'anonymous'
  
  const now = Date.now()
  const record = rateLimitStore.get(identifier)
  
  // Clean up expired entries periodically
  if (Math.random() < 0.01) {
    cleanupRateLimitStore(now)
  }
  
  if (!record || record.resetAt < now) {
    // Create new record
    rateLimitStore.set(identifier, {
      count: 1,
      resetAt: now + windowMs,
    })
    return null
  }
  
  if (record.count >= maxRequests) {
    // Rate limit exceeded
    return NextResponse.json(
      {
        error: message || 'Too many requests. Please try again later.',
        retryAfter: Math.ceil((record.resetAt - now) / 1000),
      },
      {
        status: 429,
        headers: {
          'Retry-After': String(Math.ceil((record.resetAt - now) / 1000)),
          'X-RateLimit-Limit': String(maxRequests),
          'X-RateLimit-Remaining': '0',
          'X-RateLimit-Reset': String(record.resetAt),
        },
      }
    )
  }
  
  // Increment count
  record.count++
  
  return null
}

function cleanupRateLimitStore(now: number) {
  for (const [key, value] of rateLimitStore.entries()) {
    if (value.resetAt < now) {
      rateLimitStore.delete(key)
    }
  }
}

/**
 * CSRF token validation
 * 
 * Validates CSRF token from request headers
 */
export function validateCSRFToken(
  request: NextRequest,
  expectedToken?: string
): boolean {
  const token = request.headers.get('x-csrf-token')
  
  if (!token || !expectedToken) {
    return false
  }
  
  // Constant-time comparison to prevent timing attacks
  return timingSafeEqual(token, expectedToken)
}

/**
 * Timing-safe string comparison
 */
function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) {
    return false
  }
  
  let result = 0
  for (let i = 0; i < a.length; i++) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i)
  }
  
  return result === 0
}

/**
 * Input sanitization
 * 
 * Basic input sanitization to prevent XSS and injection attacks
 */
export function sanitizeInput(input: string): string {
  return input
    .replace(/[<>]/g, '') // Remove angle brackets
    .replace(/javascript:/gi, '') // Remove javascript: protocol
    .replace(/on\w+\s*=/gi, '') // Remove event handlers
    .trim()
}

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  // Use a simpler, more secure pattern to avoid backtracking
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  return emailRegex.test(email)
}

/**
 * Validate URL format
 */
export function isValidURL(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * Request body validation middleware
 * 
 * @example
 * ```ts
 * const validation = validateRequestBody(body, {
 *   email: { type: 'string', required: true, validator: isValidEmail },
 *   age: { type: 'number', required: false, min: 0, max: 120 }
 * })
 * 
 * if (!validation.valid) {
 *   return NextResponse.json({ errors: validation.errors }, { status: 400 })
 * }
 * ```
 */
export interface FieldValidation {
  type: 'string' | 'number' | 'boolean' | 'array' | 'object'
  required?: boolean
  min?: number
  max?: number
  validator?: (value: any) => boolean
  message?: string
}

export function validateRequestBody(
  body: any,
  schema: Record<string, FieldValidation>
): { valid: boolean; errors: Record<string, string> } {
  const errors: Record<string, string> = {}
  
  for (const [field, rules] of Object.entries(schema)) {
    const value = body[field]
    
    // Check required
    if (rules.required && (value === undefined || value === null || value === '')) {
      errors[field] = rules.message || `${field} is required`
      continue
    }
    
    // Skip validation if field is not required and not provided
    if (!rules.required && (value === undefined || value === null)) {
      continue
    }
    
    // Type validation
    if (typeof value !== rules.type) {
      errors[field] = rules.message || `${field} must be of type ${rules.type}`
      continue
    }
    
    // Min/max validation for strings and numbers
    if (rules.type === 'string' && typeof value === 'string') {
      if (rules.min !== undefined && value.length < rules.min) {
        errors[field] = rules.message || `${field} must be at least ${rules.min} characters`
        continue
      }
      if (rules.max !== undefined && value.length > rules.max) {
        errors[field] = rules.message || `${field} must be at most ${rules.max} characters`
        continue
      }
    }
    
    if (rules.type === 'number' && typeof value === 'number') {
      if (rules.min !== undefined && value < rules.min) {
        errors[field] = rules.message || `${field} must be at least ${rules.min}`
        continue
      }
      if (rules.max !== undefined && value > rules.max) {
        errors[field] = rules.message || `${field} must be at most ${rules.max}`
        continue
      }
    }
    
    // Custom validator
    if (rules.validator && !rules.validator(value)) {
      errors[field] = rules.message || `${field} is invalid`
    }
  }
  
  return {
    valid: Object.keys(errors).length === 0,
    errors,
  }
}

/**
 * Security headers middleware
 * 
 * Adds security headers to responses
 */
export function addSecurityHeaders(response: NextResponse): NextResponse {
  response.headers.set('X-Content-Type-Options', 'nosniff')
  response.headers.set('X-Frame-Options', 'DENY')
  response.headers.set('X-XSS-Protection', '1; mode=block')
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  response.headers.set(
    'Permissions-Policy',
    'camera=(), microphone=(), geolocation=()'
  )
  
  return response
}
