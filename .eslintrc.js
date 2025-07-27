module.exports = {
  root: true,
  extends: ['eslint:recommended'],
  env: {
    node: true,
    es2022: true,
  },
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
  },
  ignorePatterns: [
    'dist/',
    'node_modules/',
    'coverage/',
    'qwencoder-eval/',
    'finetuning/',
    '**/*.ts',
    '**/*.tsx',
  ],
};
