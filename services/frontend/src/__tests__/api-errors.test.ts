/**
 * @jest-environment jsdom
 */

import { describe, it, expect, jest } from '@jest/globals'
import { 
  parseApiError, 
  formatErrorMessage,
  isRetriableError,
  retryWithBackoff,
  APIError 
} from '@/lib/api-errors'

describe('API Error Handling', () => {
  describe('parseApiError', () => {
    it('should parse APIError instances', () => {
      const error = new APIError('TEST_ERROR', 'Test message', 400, { detail: 'test' })
      const result = parseApiError(error)
      
      expect(result.code).toBe('TEST_ERROR')
      expect(result.message).toBe('Test message')
      expect(result.details).toEqual({ detail: 'test' })
    })

    it('should parse standard Error instances', () => {
      const error = new Error('Standard error')
      const result = parseApiError(error)
      
      expect(result.code).toBe('UNKNOWN_ERROR')
      expect(result.message).toBe('Standard error')
    })

    it('should parse error objects', () => {
      const error = { code: 'VALIDATION_ERROR', message: 'Invalid input' }
      const result = parseApiError(error)
      
      expect(result.code).toBe('VALIDATION_ERROR')
      expect(result.message).toBe('Invalid input')
    })

    it('should handle unknown error types', () => {
      const result = parseApiError('string error')
      
      expect(result.code).toBe('UNKNOWN_ERROR')
      expect(result.message).toBe('An unknown error occurred')
    })
  })

  describe('formatErrorMessage', () => {
    it('should format UNAUTHORIZED error', () => {
      const error = { code: 'UNAUTHORIZED', message: 'Auth failed' }
      const result = formatErrorMessage(error)
      
      expect(result).toBe('Please log in to continue')
    })

    it('should format NOT_FOUND error', () => {
      const error = { code: 'NOT_FOUND', message: 'Resource missing' }
      const result = formatErrorMessage(error)
      
      expect(result).toBe('The requested resource was not found')
    })

    it('should return original message for unknown codes', () => {
      const error = { code: 'CUSTOM_ERROR', message: 'Custom error message' }
      const result = formatErrorMessage(error)
      
      expect(result).toBe('Custom error message')
    })
  })

  describe('isRetriableError', () => {
    it('should identify retriable network errors', () => {
      expect(isRetriableError({ code: 'NETWORK_ERROR' })).toBe(true)
      expect(isRetriableError({ code: 'TIMEOUT' })).toBe(true)
      expect(isRetriableError({ code: 'HTTP_503' })).toBe(true)
    })

    it('should identify non-retriable errors', () => {
      expect(isRetriableError({ code: 'UNAUTHORIZED' })).toBe(false)
      expect(isRetriableError({ code: 'VALIDATION_ERROR' })).toBe(false)
      expect(isRetriableError({ code: 'NOT_FOUND' })).toBe(false)
    })
  })

  describe('retryWithBackoff', () => {
    it('should succeed on first try', async () => {
      const fn = jest.fn<() => Promise<string>>().mockResolvedValue('success')
      
      const result = await retryWithBackoff<string>(fn, { maxRetries: 3 })
      
      expect(result).toBe('success')
      expect(fn).toHaveBeenCalledTimes(1)
    })

    it('should retry on retriable errors', async () => {
      const fn = jest.fn<() => Promise<string>>()
        .mockRejectedValueOnce({ code: 'NETWORK_ERROR' })
        .mockRejectedValueOnce({ code: 'NETWORK_ERROR' })
        .mockResolvedValue('success')
      
      const result = await retryWithBackoff<string>(fn, { 
        maxRetries: 3,
        initialDelay: 10,
      })
      
      expect(result).toBe('success')
      expect(fn).toHaveBeenCalledTimes(3)
    })

    it('should not retry on non-retriable errors', async () => {
      const fn = jest.fn<() => Promise<string>>().mockRejectedValue({ code: 'UNAUTHORIZED' })
      
      await expect(
        retryWithBackoff<string>(fn, { maxRetries: 3 })
      ).rejects.toEqual({ code: 'UNAUTHORIZED' })
      
      expect(fn).toHaveBeenCalledTimes(1)
    })

    it('should throw after max retries', async () => {
      const fn = jest.fn<() => Promise<string>>().mockRejectedValue({ code: 'NETWORK_ERROR' })
      
      await expect(
        retryWithBackoff<string>(fn, { 
          maxRetries: 2,
          initialDelay: 10,
        })
      ).rejects.toEqual({ code: 'NETWORK_ERROR' })
      
      expect(fn).toHaveBeenCalledTimes(3) // Initial + 2 retries
    })
  })
})
