import baseConfig from '../../jest.config.mjs';

export default {
  ...baseConfig,
  displayName: '@monkey-coder/cli',
  setupFilesAfterEnv: ['<rootDir>/../../jest.setup.js'],
};
