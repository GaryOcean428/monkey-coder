/**
 * Yarn Constraints Configuration
 * Enforces consistency across workspace packages
 * @see https://yarnpkg.com/features/constraints
 */

module.exports = {
  async constraints({ Yarn }) {
    // Ensure all workspaces have consistent Node.js engine requirement
    for (const workspace of Yarn.workspaces()) {
      workspace.set('engines.node', '>=20.0.0');
    }

    // Ensure all TypeScript dependencies use the same version
    for (const dep of Yarn.dependencies({ ident: 'typescript' })) {
      dep.update(`^5.8.3`);
    }

    // Ensure all React dependencies use the same version
    for (const dep of Yarn.dependencies({ ident: 'react' })) {
      dep.update(`^18.2.0`);
    }
    for (const dep of Yarn.dependencies({ ident: 'react-dom' })) {
      dep.update(`^18.2.0`);
    }

    // Ensure all ESLint and related plugins use consistent versions
    for (const dep of Yarn.dependencies({ ident: '@typescript-eslint/eslint-plugin' })) {
      dep.update(`^8.38.0`);
    }
    for (const dep of Yarn.dependencies({ ident: '@typescript-eslint/parser' })) {
      dep.update(`^8.38.0`);
    }
    for (const dep of Yarn.dependencies({ ident: 'eslint' })) {
      dep.update(`^9.32.0`);
    }
    for (const dep of Yarn.dependencies({ ident: 'prettier' })) {
      dep.update(`^3.6.2`);
    }

    // Ensure all Sentry packages use the same version
    const sentryVersion = '^9.42.0';
    for (const dep of Yarn.dependencies({ ident: '@sentry/node' })) {
      dep.update(sentryVersion);
    }
    for (const dep of Yarn.dependencies({ ident: '@sentry/react' })) {
      dep.update(sentryVersion);
    }
    for (const dep of Yarn.dependencies({ ident: '@sentry/browser' })) {
      dep.update(sentryVersion);
    }
    for (const dep of Yarn.dependencies({ ident: '@sentry/profiling-node' })) {
      dep.update(sentryVersion);
    }

    // Ensure private packages are marked as such
    for (const workspace of Yarn.workspaces()) {
      if (workspace.manifest.name === 'monkey-coder' || 
          workspace.manifest.name === '@monkey-coder/web' ||
          workspace.manifest.name === 'docs') {
        workspace.set('private', true);
      }
    }

    // Ensure all workspace packages have license field
    for (const workspace of Yarn.workspaces()) {
      if (!workspace.manifest.license) {
        workspace.set('license', 'MIT');
      }
    }

    // Ensure workspace dependencies use workspace protocol
    for (const workspace of Yarn.workspaces()) {
      for (const [name, range] of Object.entries(workspace.manifest.dependencies || {})) {
        if (name.startsWith('@monkey-coder/') || name === 'monkey-coder-sdk') {
          // Check if this is a workspace package
          const isWorkspacePackage = Yarn.workspaces().some(w => w.manifest.name === name);
          if (isWorkspacePackage && !range.startsWith('workspace:')) {
            workspace.set(`dependencies.${name}`, `workspace:*`);
          }
        }
      }
    }
  }
};