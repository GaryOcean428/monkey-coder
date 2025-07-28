#!/usr/bin/env node
/**
 * Post-install script for @monkey-coder/cli
 * Handles safe installation with CI guards and network call prevention
 */

const fs = require('fs');
const path = require('path');

console.log('🐒 Monkey Coder CLI post-install setup...');

// CI Environment Detection
const isCI = process.env.CI === 'true' || 
             process.env.CONTINUOUS_INTEGRATION === 'true' ||
             process.env.GITHUB_ACTIONS === 'true' ||
             process.env.GITLAB_CI === 'true' ||
             process.env.JENKINS_URL ||
             process.env.BUILDKITE === 'true';

if (isCI) {
  console.log('ℹ️  CI environment detected - skipping network-dependent setup');
  process.exit(0);
}

// Check if in npm install/CI context
if (process.env.npm_config_global) {
  console.log('ℹ️  Global installation detected - skipping model downloads');
}

// Safe post-install operations only
try {
  // Create config directory if it doesn't exist
  const configDir = path.join(require('os').homedir(), '.monkey-coder');
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
    console.log('✅ Created config directory');
  }

  // Create empty config file if it doesn't exist
  const configFile = path.join(configDir, 'config.json');
  if (!fs.existsSync(configFile)) {
    const defaultConfig = {
      apiKey: '',
      baseUrl: 'https://monkey-coder.up.railway.app',
      version: '1.0.0'
    };
    fs.writeFileSync(configFile, JSON.stringify(defaultConfig, null, 2));
    console.log('✅ Created default config file');
  }

  console.log('✅ Post-install setup completed');
  console.log('');
  console.log('Next steps:');
  console.log('1. Set API key: monkey-coder config set apiKey YOUR_API_KEY');
  console.log('2. Test connection: monkey-coder health');
  console.log('3. Get started: monkey-coder --help');

} catch (error) {
  console.error('⚠️  Post-install setup failed (non-critical):', error.message);
  // Don't fail the installation for post-install issues
  process.exit(0);
}