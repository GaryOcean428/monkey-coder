/**
 * Tests for API configuration
 */

import { getApiBaseUrl, getWebSocketUrl } from '@/config/api';

describe('API Configuration', () => {
  const originalEnv = process.env;
  const originalWindow = global.window;

  beforeEach(() => {
    // Reset environment variables
    process.env = { ...originalEnv };
    // Reset window
    delete (global as any).window;
  });

  afterEach(() => {
    process.env = originalEnv;
    global.window = originalWindow;
  });

  describe('getApiBaseUrl', () => {
    it('should use NEXT_PUBLIC_API_URL when set', () => {
      process.env.NEXT_PUBLIC_API_URL = 'https://api.example.com';
      const url = getApiBaseUrl();
      expect(url).toBe('https://api.example.com');
    });

    it('should fallback to localhost:8000 on server-side', () => {
      delete process.env.NEXT_PUBLIC_API_URL;
      const url = getApiBaseUrl();
      expect(url).toBe('http://localhost:8000');
    });

    it('should detect Railway backend URL in browser', () => {
      process.env.NEXT_PUBLIC_API_URL = '';
      (global as any).window = {
        location: {
          protocol: 'https:',
          hostname: 'monkey-coder.up.railway.app',
          origin: 'https://monkey-coder.up.railway.app',
        },
      };

      const url = getApiBaseUrl();
      expect(url).toBe('https://monkey-coder-backend-production.up.railway.app');
    });

    it('should use same domain for fastmonkey.au', () => {
      process.env.NEXT_PUBLIC_API_URL = '';
      (global as any).window = {
        location: {
          protocol: 'https:',
          hostname: 'coder.fastmonkey.au',
          origin: 'https://coder.fastmonkey.au',
        },
      };

      const url = getApiBaseUrl();
      expect(url).toBe('https://coder.fastmonkey.au');
    });

    it('should use localhost:8000 for localhost in browser', () => {
      process.env.NEXT_PUBLIC_API_URL = '';
      (global as any).window = {
        location: {
          protocol: 'http:',
          hostname: 'localhost',
          origin: 'http://localhost:3000',
        },
      };

      const url = getApiBaseUrl();
      expect(url).toBe('http://localhost:8000');
    });
  });

  describe('getWebSocketUrl', () => {
    it('should use NEXT_PUBLIC_WS_URL when set', () => {
      process.env.NEXT_PUBLIC_WS_URL = 'wss://ws.example.com';
      const url = getWebSocketUrl();
      expect(url).toBe('wss://ws.example.com');
    });

    it('should fallback to ws://localhost:8000 on server-side', () => {
      delete process.env.NEXT_PUBLIC_WS_URL;
      const url = getWebSocketUrl();
      expect(url).toBe('ws://localhost:8000');
    });

    it('should detect Railway backend WebSocket URL in browser', () => {
      process.env.NEXT_PUBLIC_WS_URL = '';
      (global as any).window = {
        location: {
          protocol: 'https:',
          hostname: 'monkey-coder.up.railway.app',
        },
      };

      const url = getWebSocketUrl();
      expect(url).toBe('wss://monkey-coder-backend-production.up.railway.app');
    });

    it('should use wss for https protocol', () => {
      process.env.NEXT_PUBLIC_WS_URL = '';
      (global as any).window = {
        location: {
          protocol: 'https:',
          hostname: 'coder.fastmonkey.au',
        },
      };

      const url = getWebSocketUrl();
      expect(url).toBe('wss://coder.fastmonkey.au');
    });

    it('should use ws for http protocol', () => {
      process.env.NEXT_PUBLIC_WS_URL = '';
      (global as any).window = {
        location: {
          protocol: 'http:',
          hostname: 'localhost',
        },
      };

      const url = getWebSocketUrl();
      expect(url).toBe('ws://localhost:8000');
    });
  });
});
