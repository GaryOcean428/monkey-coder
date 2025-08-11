
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  transform: {
    '^.+\\.tsx?$': [
      'ts-jest',
      {
        tsconfig: {
          module: 'es2022',
        },
      },
    ],
  },
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
