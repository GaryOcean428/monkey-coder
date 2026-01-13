/**
 * @jest-environment jsdom
 */

import { describe, it, expect, beforeEach, afterEach } from '@jest/globals'
import { 
  rateLimit, 
  validateCSRFToken,
  sanitizeInput,
  isValidEmail,
  isValidURL,
  validateRequestBody 
} from '@/lib/security-middleware'
import { NextRequest, NextResponse } from 'next/server'

describe('Security Middleware', () => {
  describe('rateLimit', () => {
    beforeEach(() => {
      // Clear any existing rate limit data
      jest.clearAllMocks()
    })

    it('should allow requests within rate limit', async () => {
      const request = new NextRequest('http://localhost:3000/api/test', {
        headers: { 'x-forwarded-for': '192.168.1.1' }
      })

      const response = await rateLimit(request, {
        maxRequests: 10,
        windowMs: 60000,
      })

      expect(response).toBeNull()
    })

    it('should block requests exceeding rate limit', async () => {
      const request = new NextRequest('http://localhost:3000/api/test', {
        headers: { 'x-forwarded-for': '192.168.1.2' }
      })

      const config = {
        maxRequests: 2,
        windowMs: 60000,
      }

      // Make requests up to limit
      await rateLimit(request, config)
      await rateLimit(request, config)
      
      // This should be blocked
      const response = await rateLimit(request, config)

      expect(response).not.toBeNull()
      expect(response?.status).toBe(429)
    })
  })

  describe('validateCSRFToken', () => {
    it('should validate matching tokens', () => {
      const request = new NextRequest('http://localhost:3000/api/test', {
        headers: { 'x-csrf-token': 'test-token-123' }
      })

      const result = validateCSRFToken(request, 'test-token-123')
      expect(result).toBe(true)
    })

    it('should reject non-matching tokens', () => {
      const request = new NextRequest('http://localhost:3000/api/test', {
        headers: { 'x-csrf-token': 'wrong-token' }
      })

      const result = validateCSRFToken(request, 'correct-token')
      expect(result).toBe(false)
    })

    it('should reject missing tokens', () => {
      const request = new NextRequest('http://localhost:3000/api/test')

      const result = validateCSRFToken(request, 'expected-token')
      expect(result).toBe(false)
    })
  })

  describe('sanitizeInput', () => {
    it('should remove angle brackets', () => {
      const input = '<script>alert("xss")</script>'
      const result = sanitizeInput(input)
      
      expect(result).not.toContain('<')
      expect(result).not.toContain('>')
    })

    it('should remove javascript: protocol', () => {
      const input = 'javascript:alert("xss")'
      const result = sanitizeInput(input)
      
      expect(result.toLowerCase()).not.toContain('javascript:')
    })

    it('should remove event handlers', () => {
      const input = '<div onclick="alert()">Click me</div>'
      const result = sanitizeInput(input)
      
      expect(result.toLowerCase()).not.toContain('onclick=')
    })

    it('should trim whitespace', () => {
      const input = '  test input  '
      const result = sanitizeInput(input)
      
      expect(result).toBe('test input')
    })
  })

  describe('isValidEmail', () => {
    it('should validate correct email formats', () => {
      expect(isValidEmail('user@example.com')).toBe(true)
      expect(isValidEmail('test.user@domain.co.uk')).toBe(true)
      expect(isValidEmail('user+tag@example.com')).toBe(true)
    })

    it('should reject invalid email formats', () => {
      expect(isValidEmail('invalid')).toBe(false)
      expect(isValidEmail('@example.com')).toBe(false)
      expect(isValidEmail('user@')).toBe(false)
      expect(isValidEmail('user @example.com')).toBe(false)
    })
  })

  describe('isValidURL', () => {
    it('should validate correct URLs', () => {
      expect(isValidURL('https://example.com')).toBe(true)
      expect(isValidURL('http://localhost:3000')).toBe(true)
      expect(isValidURL('https://sub.domain.com/path')).toBe(true)
    })

    it('should reject invalid URLs', () => {
      expect(isValidURL('not a url')).toBe(false)
      expect(isValidURL('example.com')).toBe(false)
      expect(isValidURL('//example.com')).toBe(false)
    })
  })

  describe('validateRequestBody', () => {
    it('should validate required fields', () => {
      const body = { name: 'John' }
      const schema = {
        name: { type: 'string' as const, required: true },
        age: { type: 'number' as const, required: true },
      }

      const result = validateRequestBody(body, schema)

      expect(result.valid).toBe(false)
      expect(result.errors.age).toBeDefined()
    })

    it('should validate field types', () => {
      const body = { name: 123 }
      const schema = {
        name: { type: 'string' as const, required: true },
      }

      const result = validateRequestBody(body, schema)

      expect(result.valid).toBe(false)
      expect(result.errors.name).toContain('type')
    })

    it('should validate string length', () => {
      const body = { password: '123' }
      const schema = {
        password: { type: 'string' as const, required: true, min: 8 },
      }

      const result = validateRequestBody(body, schema)

      expect(result.valid).toBe(false)
      expect(result.errors.password).toContain('at least')
    })

    it('should validate number ranges', () => {
      const body = { age: 200 }
      const schema = {
        age: { type: 'number' as const, required: true, min: 0, max: 120 },
      }

      const result = validateRequestBody(body, schema)

      expect(result.valid).toBe(false)
      expect(result.errors.age).toContain('at most')
    })

    it('should use custom validators', () => {
      const body = { email: 'invalid-email' }
      const schema = {
        email: { 
          type: 'string' as const, 
          required: true, 
          validator: isValidEmail 
        },
      }

      const result = validateRequestBody(body, schema)

      expect(result.valid).toBe(false)
      expect(result.errors.email).toBeDefined()
    })

    it('should pass valid data', () => {
      const body = { 
        name: 'John Doe',
        age: 30,
        email: 'john@example.com'
      }
      const schema = {
        name: { type: 'string' as const, required: true, min: 2 },
        age: { type: 'number' as const, required: true, min: 0, max: 120 },
        email: { type: 'string' as const, required: true, validator: isValidEmail },
      }

      const result = validateRequestBody(body, schema)

      expect(result.valid).toBe(true)
      expect(Object.keys(result.errors).length).toBe(0)
    })
  })
})
