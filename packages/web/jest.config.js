/** Jest config for Next.js app using ts-jest without next/jest to avoid Yarn 4 lockfile patching issues */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['@testing-library/jest-dom'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  testMatch: ['**/__tests__/**/*.(test|spec).(ts|tsx)']
};
