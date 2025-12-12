/**
 * Barrel export for configuration
 * Simplifies imports: import { API_CONFIG, getApiBaseUrl } from '@/config'
 */

// API Configuration
export {
  getApiBaseUrl,
  getWebSocketUrl,
  API_CONFIG,
  apiFetch,
  handleApiResponse,
  APIError,
} from './api';

// Navigation Configuration
export {
  mainNavigation,
  footerNavigation,
  docsNavigation,
  type NavItem,
  type FooterSection,
} from './navigation';

// Stripe Configuration (if exists)
export * from './stripe';
