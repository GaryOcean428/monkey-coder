// Flat ESLint config (ESLint 9+) for Next.js 15 app (web workspace)
// Keep it minimal and compatible with TS/React 19.
// Includes no-regex-by-default policy enforcement

import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import nextPlugin from '@next/eslint-plugin-next';
import regexpPlugin from 'eslint-plugin-regexp';

export default [
  {
    ignores: [
      '.next/**',
      'out/**',
      'node_modules/**',
      'coverage/**',
      'next-env.d.ts', // Next.js generated file
    ],
  },
  // JS rules
  js.configs.recommended,
  {
    files: ['**/*.config.js', '**/*.config.cjs', '**/*.config.mjs', 'jest.config.cjs', 'next.config.mjs'],
    languageOptions: { ecmaVersion: 2022, sourceType: 'module' },
    rules: { 'no-undef': 'off' },
  },
  // Next.js rules
  {
    plugins: { '@next/next': nextPlugin },
    rules: {
      ...nextPlugin.configs.recommended.rules,
      ...nextPlugin.configs['core-web-vitals'].rules,
    },
  },
  // TS rules
  ...tseslint.configs.recommended,
  {
    files: ['**/*.{ts,tsx}'],
    plugins: {
      regexp: regexpPlugin,
    },
    languageOptions: { ecmaVersion: 2022, sourceType: 'module' },
    rules: {
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'off',

      // No-Regex-by-Default Policy
      'no-new-wrappers': 'error',
      'no-eval': 'error',
      'regexp/no-super-linear-backtracking': 'error',
      'regexp/no-useless-quantifier': 'error',
      'regexp/no-empty-alternative': 'error',
      'regexp/no-dupe-characters-character-class': 'error',
      'regexp/optimal-quantifier-concatenation': 'error',
      'regexp/no-legacy-features': 'error',

      'no-restricted-syntax': [
        'error',
        {
          selector: "NewExpression[callee.name='RegExp']",
          message:
            'Regex is disallowed by default. Use a parser or approved helper. Document exceptions in CONTRIBUTING.md.',
        },
        {
          selector:
            "Literal[regex=true][value.raw=/.*\\(\\?:?\\).*|.*\\(.*\\(.*\\).*\\).*/]",
          message: 'Nested groups and catch-alls are disallowed. Use typed parsing instead.',
        },
      ],

      'no-restricted-properties': [
        'warn', // Use warn for web as it has some existing patterns that are documented as allowed
        {
          object: 'String',
          property: 'match',
          message: 'Avoid String.match with regex. Use typed parsing, URL, JSON, or DOM APIs. See CONTRIBUTING.md for allowed exceptions.',
        },
        {
          object: 'String',
          property: 'replace',
          message:
            'Avoid String.replace with regex. Use explicit string transforms or standard libraries. See CONTRIBUTING.md for allowed exceptions.',
        },
        {
          object: 'String',
          property: 'search',
          message:
            'Avoid String.search with regex. Use includes/startsWith/endsWith for simple checks.',
        },
      ],
    },
  },
  // Allow require() and CommonJS in Node config files and mocks
  {
    files: ['**/*.config.js', 'jest.config.cjs', 'next.config.mjs', '__mocks__/**/*.js'],
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
