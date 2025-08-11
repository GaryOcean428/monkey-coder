// Flat ESLint config (v9+) for SDK workspace
// Uses @typescript-eslint for TypeScript sources; minimal rules to avoid noise.

const tsParser = require('@typescript-eslint/parser');
const tsPlugin = require('@typescript-eslint/eslint-plugin');

module.exports = [
  {
    ignores: [
      'dist/**',
      'node_modules/**',
      '**/*.tsbuildinfo',
      'coverage/**',
      // Python build artifacts inside SDK
      'src/python/build/**',
      'src/python/dist/**',
      'src/python/**/*.egg-info/**',
    ],
  },
  {
    files: ['src/**/*.{ts,tsx}', 'examples/**/*.ts'],
    languageOptions: {
      parser: tsParser,
      ecmaVersion: 2022,
      sourceType: 'module',
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
    },
    rules: {
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'off',
      'no-undef': 'off',
    },
  },
];
