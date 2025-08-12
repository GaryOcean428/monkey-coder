// Retry once in CI to reduce flakiness
if (process.env.CI) {
  // @ts-ignore
  jest.retryTimes(1);
}
