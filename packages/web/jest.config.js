const nextJest = require('next/jest');

const createJestConfig = nextJest({
  dir: './',
});

const customJestConfig = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|sass|scss)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|webp|avif|svg)$': '<rootDir>/__mocks__/fileMock.js',
  },
  testMatch: ['**/__tests__/**/*.(test|spec).(ts|tsx)'],
  transform: {},
  collectCoverageFrom: [
    '<rootDir>/src/**/*.{ts,tsx}',
    '!<rootDir>/src/**/__tests__/**',
    '!<rootDir>/**/index.{ts,tsx}'
  ],
  coverageThreshold: {
    global: {
      lines: 50,
      functions: 50,
      statements: 50,
      branches: 40
    }
  },
};

module.exports = createJestConfig(customJestConfig);
