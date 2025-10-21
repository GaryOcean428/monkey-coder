// ESLint flat config for the CLI package
// TypeScript-aware configuration for Node.js CLI tools
// Includes no-regex-by-default policy enforcement

module.exports = [
  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: {
      parser: require('@typescript-eslint/parser'),
      parserOptions: {
        ecmaVersion: 2022,
        sourceType: 'module',
        project: './tsconfig.json',
      },
    },
    plugins: {
      '@typescript-eslint': require('@typescript-eslint/eslint-plugin'),
      import: require('eslint-plugin-import'),
      prettier: require('eslint-plugin-prettier'),
      regexp: require('eslint-plugin-regexp'),
    },
    rules: {
      // TypeScript-specific rules
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'warn',
      
      // Import rules
      'import/order': ['warn', { 'newlines-between': 'always' }],
      
      // General rules
      'no-console': 'off', // CLI tools need console output
      'prefer-const': 'error',

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
        'error',
        {
          object: 'String',
          property: 'match',
          message: 'Avoid String.match with regex. Use typed parsing, URL, JSON, or DOM APIs.',
        },
        {
          object: 'String',
          property: 'replace',
          message:
            'Avoid String.replace with regex. Use explicit string transforms or standard libraries.',
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
  {
    files: ['**/*.js', '**/*.cjs', '**/*.mjs'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
    },
    plugins: {
      regexp: require('eslint-plugin-regexp'),
    },
    rules: {
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],

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
      ],

      'no-restricted-properties': [
        'error',
        {
          object: 'String',
          property: 'match',
          message: 'Avoid String.match with regex. Use typed parsing, URL, JSON, or DOM APIs.',
        },
        {
          object: 'String',
          property: 'replace',
          message:
            'Avoid String.replace with regex. Use explicit string transforms or standard libraries.',
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
  {
    ignores: [
      'dist/**',
      'node_modules/**',
      'coverage/**',
      '*.tsbuildinfo',
    ],
  },
];