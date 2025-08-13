// Flat ESLint config (v9+) for SDK workspace
// Uses @typescript-eslint with minimal defaults for TS sources.

import tsParser from '@typescript-eslint/parser';
import tsPlugin from '@typescript-eslint/eslint-plugin';

export default [
  {
    ignores: [
      'dist/**',
      'node_modules/**',
      '**/*.tsbuildinfo',
      'coverage/**',
      'src/python/**', // Ignore Python parts
    ],
  },
  {
    files: ['src/**/*.{ts,tsx}', '**/*.js'],
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
