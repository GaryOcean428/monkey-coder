// Deprecated duplicate root ESLint config.
// To avoid confusion, this file simply proxies to the canonical
// CommonJS root config at `eslint.config.js`.
// Keeping this file avoids breaking any workflows that might
// reference `eslint.config.mjs`, while ensuring a single source of truth.

import config from './eslint.config.js';

export default config;
