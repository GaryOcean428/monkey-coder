// Flat ESLint config (v9+) for CLI workspace
// Uses @typescript-eslint with minimal, sane defaults for TS sources.

const tsParser = require('@typescript-eslint/parser');
const tsPlugin = require('@typescript-eslint/eslint-plugin');

module.exports = [
  {
    ignores: [
      'dist/**',
      'node_modules/**',
      '**/*.tsbuildinfo',
      'coverage/**',
    ],
  },
  {
    files: ['src/**/*.{ts,tsx}', 'scripts/**/*.cjs'],
    languageOptions: {
      parser: tsParser,
      ecmaVersion: 2022,
      sourceType: 'module',
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
    },
    rules: {
      // General TS hygiene
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'off', // relax for CLI plumbing
      // Avoid false positives in mixed TS/JS monorepos
      'no-undef': 'off',
    },
  },
];
