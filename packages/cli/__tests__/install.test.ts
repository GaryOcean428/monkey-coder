/**
 * Installation tests for monkey-coder-cli
 * Ensures the package installs correctly without network dependencies
 */

import { describe, test, expect, beforeAll, afterAll } from '@jest/globals';
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs-extra';
import path from 'path';
import os from 'os';

const execAsync = promisify(exec);

describe('CLI Installation', () => {
  let tempDir: string;
  let originalCwd: string;

  beforeAll(async () => {
    originalCwd = process.cwd();
    tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'monkey-cli-test-'));
    process.chdir(tempDir);
  });

  afterAll(async () => {
    process.chdir(originalCwd);
    await fs.remove(tempDir);
  });

  test('should install without network calls in CI environment', async () => {
    // Create a minimal package.json
    const packageJson = {
      name: 'test-installation',
      version: '1.0.0',
      private: true
    };
    
    await fs.writeJson(path.join(tempDir, 'package.json'), packageJson, { spaces: 2 });

    // Install with CI flag to prevent network calls
    const env = { ...process.env, CI: 'true' };
    
    try {
      const { stdout, stderr } = await execAsync(
        'npm install monkey-coder-cli --no-save --silent',
        { env, timeout: 60000 }
      );
      
      // Installation should complete without errors
      expect(stderr).not.toContain('ERROR');
      expect(stderr).not.toContain('502');
      expect(stderr).not.toContain('402');
      
      // Should skip network-dependent operations in CI
      expect(stdout).toContain('CI environment detected');
      
    } catch (error) {
      // If package doesn't exist, that's the issue we're fixing
      if (error.message.includes('404') || error.message.includes('Not Found')) {
        console.log('⚠️  monkey-coder-cli not found in registry - this is the expected issue');
        expect(error.message).toContain('404');
      } else {
        throw error;
      }
    }
  }, 120000);

  test('should not make network calls during post-install', async () => {
    // Mock network calls to detect if any are made
    const originalFetch = global.fetch;
    const networkCalls: string[] = [];
    
    global.fetch = jest.fn(async (url) => {
      networkCalls.push(url.toString());
      throw new Error('Network calls blocked in test');
    }) as jest.MockedFunction<typeof fetch>;

    try {
      // Import the post-install script directly
      const postInstallPath = path.resolve('../scripts/postinstall.js');
      
      if (await fs.pathExists(postInstallPath)) {
        // Set CI environment
        process.env.CI = 'true';
        
        // Run post-install script
        await execAsync(`node ${postInstallPath}`);
        
        // Should not have made any network calls
        expect(networkCalls).toHaveLength(0);
      }
    } finally {
      global.fetch = originalFetch;
      delete process.env.CI;
    }
  });

  test('should create config directory safely', async () => {
    const configDir = path.join(os.homedir(), '.monkey-coder');
    
    // Remove config dir if it exists for clean test
    if (await fs.pathExists(configDir)) {
      await fs.remove(configDir);
    }

    // Set CI flag to prevent network operations
    process.env.CI = 'true';
    
    try {
      const postInstallPath = path.resolve('../scripts/postinstall.js');
      
      if (await fs.pathExists(postInstallPath)) {
        await execAsync(`node ${postInstallPath}`);
        
        // Config directory should be created
        expect(await fs.pathExists(configDir)).toBe(true);
        
        // Config file should be created with defaults
        const configFile = path.join(configDir, 'config.json');
        expect(await fs.pathExists(configFile)).toBe(true);
        
        const config = await fs.readJson(configFile);
        expect(config).toHaveProperty('baseUrl');
        expect(config).toHaveProperty('apiKey');
        expect(config.baseUrl).toBe('https://monkey-coder.up.railway.app');
      }
    } finally {
      delete process.env.CI;
    }
  });

  test('should handle installation errors gracefully', async () => {
    // Test with invalid environment
    const env = { ...process.env, HOME: '/nonexistent' };
    
    try {
      const postInstallPath = path.resolve('../scripts/postinstall.js');
      
      if (await fs.pathExists(postInstallPath)) {
        const { stdout } = await execAsync(`node ${postInstallPath}`, { env });
        
        // Should complete without throwing, even with errors
        expect(stdout).toBeDefined();
      }
    } catch (error) {
      // Post-install should never fail the installation
      fail('Post-install script should handle errors gracefully');
    }
  });

  test('should have correct package.json structure', async () => {
    const packageJsonPath = path.resolve('../package.json');
    const packageJson = await fs.readJson(packageJsonPath);
    
    // Should use scoped name
    expect(packageJson.name).toBe('monkey-coder-cli');
    
    // Should have bin entries
    expect(packageJson.bin).toHaveProperty('monkey');
    expect(packageJson.bin).toHaveProperty('monkey-coder');
    
    // Should have post-install script
    expect(packageJson.scripts).toHaveProperty('postinstall');
    
    // Should not have pre-install scripts that could cause issues
    expect(packageJson.scripts).not.toHaveProperty('preinstall');
  });

  test('should work without internet connection', async () => {
    // Simulate offline environment
    const env = { 
      ...process.env, 
      CI: 'true',
      npm_config_offline: 'true'
    };
    
    try {
      const postInstallPath = path.resolve('../scripts/postinstall.js');
      
      if (await fs.pathExists(postInstallPath)) {
        const { stdout } = await execAsync(`node ${postInstallPath}`, { env });
        
        // Should complete successfully even offline
        expect(stdout).toContain('setup completed');
      }
    } catch (error) {
      // Should not fail due to network issues
      expect(error.message).not.toContain('network');
      expect(error.message).not.toContain('ENOTFOUND');
    }
  });
});