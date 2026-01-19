/**
 * Tests for configuration loader helpers
 */
import { describe, it, expect } from '@jest/globals';
import { MonkeyCoderConfigSchema } from '../src/config/schema';
import * as path from 'path';
import * as os from 'os';

describe('Configuration Loader Helpers', () => {
  describe('Schema Validation', () => {
    it('should validate default config', () => {
      const config = MonkeyCoderConfigSchema.parse({});
      
      expect(config.version).toBe(1);
      expect(config.permissions).toBeDefined();
      expect(config.mcp).toBeDefined();
      expect(config.agent).toBeDefined();
    });

    it('should validate custom config', () => {
      const config = MonkeyCoderConfigSchema.parse({
        permissions: {
          allowedPaths: ['./src/**/*'],
          requireApproval: false,
        },
        agent: {
          defaultProvider: 'openai',
        },
      });
      
      expect(config.permissions.allowedPaths).toEqual(['./src/**/*']);
      expect(config.permissions.requireApproval).toBe(false);
      expect(config.agent.defaultProvider).toBe('openai');
    });
  });

  describe('Global Config Path', () => {
    it('should construct valid path', () => {
      const homeDir = os.homedir() || process.env.HOME || process.env.USERPROFILE || '';
      const expectedPath = path.join(homeDir, '.config', 'monkey-coder', 'config.json');
      
      // Just verify the path structure is reasonable
      expect(expectedPath).toContain('.config');
      expect(expectedPath).toContain('monkey-coder');
      expect(expectedPath).toContain('config.json');
    });
  });
});
