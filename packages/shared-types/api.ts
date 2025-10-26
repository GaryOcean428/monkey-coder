/**
 * API-related shared types
 */

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  page: number;
  pageSize: number;
  total: number;
  hasMore: boolean;
}

export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  services?: Record<string, {
    status: 'up' | 'down';
    latency?: number;
  }>;
}
