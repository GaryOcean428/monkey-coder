import baseConfig from '../../jest.config.mjs';

export default {
  ...baseConfig,
  displayName: '@monkey-coder/sdk',
  setupFilesAfterEnv: ['<rootDir>/../../jest.setup.js'],
};
