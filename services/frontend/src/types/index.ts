/**
 * Types Barrel Export
 * 
 * Central export point for all TypeScript type definitions.
 */

// Re-export from lib/models
export type * from '../lib/models'

// Common utility types
export type Nullable<T> = T | null
export type Optional<T> = T | undefined
export type Maybe<T> = T | null | undefined

// API response types
export interface ApiResponse<T = unknown> {
  data?: T
  error?: ApiError
  status: number
  message?: string
}

export interface ApiError {
  code: string
  message: string
  details?: Record<string, unknown>
}

// Pagination types
export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  pageSize: number
  hasMore: boolean
}

// Form types
export interface FormState<T = unknown> {
  isSubmitting: boolean
  isValid: boolean
  errors: Record<string, string>
  values: T
}

// Placeholder for domain-specific types
// export type { User, Project, Task } from './domain'
