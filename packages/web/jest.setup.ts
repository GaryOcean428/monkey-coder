// Jest setup for Next.js + React Testing Library
// Extends Jest's expect with DOM matchers (toBeInTheDocument, toHaveTextContent, etc.)
import '@testing-library/jest-dom';

declare const jest: typeof import('@jest/globals').jest;

// Retry once in CI to reduce flakiness
if (process.env.CI) {
  jest.retryTimes(1);
}
