import '@testing-library/jest-dom';

// Mock global Response for Node.js test environment
if (typeof global.Response === 'undefined') {
  global.Response = class Response {
    status: number;
    statusText: string;
    
    constructor(body?: BodyInit | null, init?: ResponseInit) {
      this.status = init?.status || 200;
      this.statusText = init?.statusText || 'OK';
    }
  } as any;
}

// Jest retry configuration handled in jest.config
