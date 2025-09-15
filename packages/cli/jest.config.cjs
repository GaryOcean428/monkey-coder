
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  extensionsToTreatAsEsm: ['.ts'],
  transform: {
    '^.+\\.tsx?$': [
      'ts-jest',
      {
        useESM: true,
        tsconfig: {
          module: 'es2022',
          target: 'es2022',
        },
      },
    ],
  },
  transformIgnorePatterns: [
    'node_modules/(?!(chalk|ansi-styles|supports-color|strip-ansi|ansi-regex|#ansi-styles)/)'
  ],
  moduleNameMapper: {
    '^chalk$': '<rootDir>/__mocks__/chalk.js'
  },
  setupFilesAfterEnv: ["<rootDir>/jest.setup.ts"],
  collectCoverageFrom: [
    '<rootDir>/src/**/*.{ts,tsx,js,jsx}',
    '!<rootDir>/src/**/__tests__/**',
    '!<rootDir>/**/index.{ts,tsx,js,jsx}'
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
