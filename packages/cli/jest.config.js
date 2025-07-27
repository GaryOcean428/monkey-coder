const baseConfig = require('../../jest.config.js');

module.exports = {
  ...baseConfig,
  displayName: '@monkey-coder/cli',
  setupFilesAfterEnv: ['<rootDir>/../../jest.setup.js'],
};
