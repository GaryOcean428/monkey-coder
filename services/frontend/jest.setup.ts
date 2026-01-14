import '@testing-library/jest-dom';

// Mock global Response for Node.js test environment
// Response is a browser API not available in Node.js
if (typeof global.Response === 'undefined') {
  class MockResponse implements Partial<Response> {
    status: number;
    statusText: string;
    ok: boolean;
    
    constructor(body?: BodyInit | null, init?: ResponseInit) {
      this.status = init?.status || 200;
      this.statusText = init?.statusText || 'OK';
      this.ok = this.status >= 200 && this.status < 300;
    }
  }
  
  // @ts-expect-error - Mocking global Response for test environment
  global.Response = MockResponse;
}

// Jest retry configuration handled in jest.config
