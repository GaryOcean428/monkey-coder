const baseConfig = require('../../jest.config.js');

module.exports = {
  ...baseConfig,
  displayName: '@monkey-coder/sdk',
  setupFilesAfterEnv: ['<rootDir>/../../jest.setup.js'],
};
