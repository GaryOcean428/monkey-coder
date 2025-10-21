// Flat ESLint config (v9+) for the monorepo root.
// Purpose: provide a minimal flat config to satisfy ESLint v9 migration warnings
// and establish repo-wide ignore patterns. Per-workspace configs (cli/sdk) will
// define TypeScript-specific rules.

const regexp = require('eslint-plugin-regexp');

module.exports = [
  // Global ignores for the repo
  {
    ignores: [
      'node_modules/**',
      '.yarn/**',
      'dist/**',
      'coverage/**',
      '.next/**',
      'out/**',
      'packages/web/.next/**',
      'packages/web/out/**',
      // Build artifacts and caches
      '**/*.tsbuildinfo',
      '**/.turbo/**',
      '**/.cache/**',
    ],
  },

  // Generic JS config with no-regex-by-default policy
  {
    files: ['**/*.js', '**/*.cjs', '**/*.mjs'],
    plugins: {
      regexp,
    },
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
    },
    rules: {
      // Keep rules minimal at the root; workspace configs can extend further.
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'no-undef': 'off', // avoid false positives in mixed TS/JS monorepo

      // No-Regex-by-Default Policy - Hard bans
      'no-new-wrappers': 'error',
      'no-eval': 'error',

      // Regexp plugin rules - prevent catastrophic backtracking and unsafe patterns
      'regexp/no-super-linear-backtracking': 'error',
      'regexp/no-useless-quantifier': 'error',
      'regexp/no-empty-alternative': 'error',
      'regexp/no-dupe-characters-character-class': 'error',
      'regexp/optimal-quantifier-concatenation': 'error',
      'regexp/no-legacy-features': 'error',

      // Discourage regex unless explicitly whitelisted
      'no-restricted-syntax': [
        'error',
        {
          selector: "NewExpression[callee.name='RegExp']",
          message:
            'Regex is disallowed by default. Use a parser or approved helper. If truly needed, document exception in CONTRIBUTING.md and keep it anchored/literal.',
        },
        {
          selector:
            "Literal[regex=true][value.raw=/.*\\(\\?:?\\).*|.*\\(.*\\(.*\\).*\\).*/]",
          message: 'Nested groups and catch-alls are disallowed. Use typed parsing instead.',
        },
      ],

      // Prefer platform APIs over regex string methods
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

  // Do not lint the web workspace from the root (Next.js handles its own lint via `next lint`)
  {
    ignores: ['packages/web/**'],
  },
];
