// Flat ESLint config (v9+) for the monorepo root.
// Purpose: provide a minimal flat config to satisfy ESLint v9 migration warnings
// and establish repo-wide ignore patterns. Per-workspace configs (cli/sdk) will
// define TypeScript-specific rules.

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

  // Generic JS config (keep minimal at root)
  {
    files: ['**/*.js', '**/*.cjs', '**/*.mjs'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
    },
    rules: {
      // Keep rules minimal at the root; workspace configs can extend further.
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'no-undef': 'off', // avoid false positives in mixed TS/JS monorepo
    },
  },

  // Do not lint the web workspace from the root (Next.js handles its own lint via `next lint`)
  {
    ignores: ['packages/web/**'],
  },
];
