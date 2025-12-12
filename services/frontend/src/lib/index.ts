/**
 * Barrel export for lib utilities
 * Simplifies imports: import { apiClient, login, logout } from '@/lib'
 */

// API Client
export { apiClient, default as APIClient } from './api-client';

// Authentication
export {
  login,
  signup,
  logout,
  getUserStatus,
  refreshToken,
  isAuthenticated,
  clearLegacyTokens,
  type AuthUser,
  type AuthResponse,
} from './auth';

// Auth Context
export {
  AuthProvider,
  useAuth,
  withAuth,
} from './auth-context';

// Models
export {
  getAvailableModels,
  getModelsStats,
  getProviderInfo,
  type ModelInfo,
  type ProviderInfo,
  type ModelsStats,
} from './models';

// Validation
export {
  validateEmail,
  validatePassword,
  validateUsername,
  validateRequired,
  validateMinLength,
  validateMaxLength,
  validatePattern,
  type ValidationResult,
  type ValidationRule,
} from './validation';

// Utilities
export * from './utils';

// Stripe Provider
export { StripeProvider } from './stripe-provider';
