// Jest setup for Next.js + React Testing Library
// Extends Jest's expect with DOM matchers (toBeInTheDocument, toHaveTextContent, etc.)
import '@testing-library/jest-dom';

// Retry once in CI to reduce flakiness
if (process.env.CI) {
  // @ts-ignore
  jest.retryTimes(1);
}
