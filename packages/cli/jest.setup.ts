// Setup for Jest tests
if (process.env.CI) {
  // Note: jest.retryTimes is not available with --experimental-vm-modules
  // Tests will run once without retries in CI environment
  console.log('Running in CI environment');
}
