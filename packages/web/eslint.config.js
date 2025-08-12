// Flat ESLint config (ESLint 9+) for Next.js 15 app (web workspace)
// Keep it minimal and compatible with TS/React 19.

import js from '@eslint/js';
import tseslint from 'typescript-eslint';

export default [
  {
    ignores: [
      '.next/**',
      'out/**',
      'node_modules/**',
      'coverage/**',
    ],
  },
  // JS rules
  js.configs.recommended,
  {
    files: [ '**/*.config.js', 'jest.config.js', 'next.config.js', '**/*.config.cjs', 'jest.config.cjs', 'next.config.cjs' ],
    languageOptions: { ecmaVersion: 2022, sourceType: 'module' },
    rules: { 'no-undef': 'off' },
  },
  // TS rules
  ...tseslint.configs.recommended,
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: { ecmaVersion: 2022, sourceType: 'module' },
    rules: {
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'off',
    },
  },
  // Allow require() and CommonJS in Node config files and mocks
  {
    files: ['**/*.config.js', 'jest.config.js', 'next.config.js', '__mocks__/**/*.js'],
    languageOptions: { 
      ecmaVersion: 2022, 
      sourceType: 'script' // Use script mode for CommonJS files
    },
    rules: { 
      '@typescript-eslint/no-require-imports': 'off',
      'no-undef': 'off' // Allow module, require, etc.
    },
  },
];
