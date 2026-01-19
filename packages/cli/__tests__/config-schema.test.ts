/**
 * Tests for configuration schema validation
 */
import { describe, it, expect } from '@jest/globals';
import {
  PermissionConfigSchema,
  MCPServerConfigSchema,
  MCPConfigSchema,
  AgentConfigSchema,
  MonkeyCoderConfigSchema,
} from '../src/config/schema';

describe('Configuration Schemas', () => {
  describe('PermissionConfigSchema', () => {
    it('should validate with defaults', () => {
      const result = PermissionConfigSchema.parse({});
      
      expect(result.allowedPaths).toEqual(['./**/*']);
      expect(result.deniedPaths).toContain('**/.env*');
      expect(result.requireApproval).toBe(true);
      expect(result.maxFileSize).toBe(10 * 1024 * 1024);
      expect(result.timeout).toBe(30000);
    });

    it('should allow custom paths', () => {
      const result = PermissionConfigSchema.parse({
        allowedPaths: ['./src/**/*', './tests/**/*'],
        deniedPaths: ['**/.git/**', '**/secrets/**'],
      });
      
      expect(result.allowedPaths).toEqual(['./src/**/*', './tests/**/*']);
      expect(result.deniedPaths).toEqual(['**/.git/**', '**/secrets/**']);
    });

    it('should allow custom commands', () => {
      const result = PermissionConfigSchema.parse({
        allowedCommands: ['git *', 'npm *', 'yarn *'],
        deniedCommands: ['rm *', 'sudo *'],
      });
      
      expect(result.allowedCommands).toEqual(['git *', 'npm *', 'yarn *']);
      expect(result.deniedCommands).toEqual(['rm *', 'sudo *']);
    });

    it('should validate requireApproval boolean', () => {
      const result1 = PermissionConfigSchema.parse({ requireApproval: true });
      expect(result1.requireApproval).toBe(true);
      
      const result2 = PermissionConfigSchema.parse({ requireApproval: false });
      expect(result2.requireApproval).toBe(false);
    });

    it('should validate numeric constraints', () => {
      const result = PermissionConfigSchema.parse({
        maxFileSize: 5000000,
        timeout: 60000,
      });
      
      expect(result.maxFileSize).toBe(5000000);
      expect(result.timeout).toBe(60000);
    });
  });

  describe('MCPServerConfigSchema', () => {
    it('should validate stdio server config', () => {
      const result = MCPServerConfigSchema.parse({
        name: 'filesystem',
        type: 'stdio',
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-filesystem', '.'],
        enabled: true,
      });
      
      expect(result.name).toBe('filesystem');
      expect(result.type).toBe('stdio');
      expect(result.command).toBe('npx');
      expect(result.args).toEqual(['-y', '@modelcontextprotocol/server-filesystem', '.']);
      expect(result.enabled).toBe(true);
    });

    it('should validate http server config', () => {
      const result = MCPServerConfigSchema.parse({
        name: 'api-server',
        type: 'http',
        url: 'https://api.example.com',
        enabled: true,
      });
      
      expect(result.name).toBe('api-server');
      expect(result.type).toBe('http');
      expect(result.url).toBe('https://api.example.com');
    });

    it('should default enabled to true', () => {
      const result = MCPServerConfigSchema.parse({
        name: 'test',
        type: 'stdio',
        command: 'test',
      });
      
      expect(result.enabled).toBe(true);
    });

    it('should reject invalid type', () => {
      expect(() => {
        MCPServerConfigSchema.parse({
          name: 'test',
          type: 'invalid',
        });
      }).toThrow();
    });
  });

  describe('MCPConfigSchema', () => {
    it('should validate with empty servers list', () => {
      const result = MCPConfigSchema.parse({});
      
      expect(result.servers).toEqual([]);
    });

    it('should validate with multiple servers', () => {
      const result = MCPConfigSchema.parse({
        servers: [
          {
            name: 'filesystem',
            type: 'stdio',
            command: 'npx',
            args: ['-y', '@modelcontextprotocol/server-filesystem', '.'],
          },
          {
            name: 'api',
            type: 'http',
            url: 'https://api.example.com',
          },
        ],
      });
      
      expect(result.servers).toHaveLength(2);
      expect(result.servers[0]?.name).toBe('filesystem');
      expect(result.servers[1]?.name).toBe('api');
    });
  });

  describe('AgentConfigSchema', () => {
    it('should validate with defaults', () => {
      const result = AgentConfigSchema.parse({});
      
      expect(result.defaultProvider).toBe('anthropic');
      expect(result.defaultModel).toBe('claude-sonnet-4-5-20250929');
      expect(result.maxIterations).toBe(10);
      expect(result.autoApprove).toBe(false);
      expect(result.sandbox).toBe('basic');
    });

    it('should allow custom values', () => {
      const result = AgentConfigSchema.parse({
        defaultProvider: 'openai',
        defaultModel: 'gpt-4',
        maxIterations: 20,
        autoApprove: true,
        sandbox: 'docker',
      });
      
      expect(result.defaultProvider).toBe('openai');
      expect(result.defaultModel).toBe('gpt-4');
      expect(result.maxIterations).toBe(20);
      expect(result.autoApprove).toBe(true);
      expect(result.sandbox).toBe('docker');
    });

    it('should reject invalid provider', () => {
      expect(() => {
        AgentConfigSchema.parse({
          defaultProvider: 'invalid',
        });
      }).toThrow();
    });

    it('should reject invalid sandbox', () => {
      expect(() => {
        AgentConfigSchema.parse({
          sandbox: 'invalid',
        });
      }).toThrow();
    });
  });

  describe('MonkeyCoderConfigSchema', () => {
    it('should validate complete config with defaults', () => {
      const result = MonkeyCoderConfigSchema.parse({});
      
      expect(result.version).toBe(1);
      expect(result.permissions).toBeDefined();
      expect(result.mcp).toBeDefined();
      expect(result.agent).toBeDefined();
    });

    it('should validate complete config with custom values', () => {
      const result = MonkeyCoderConfigSchema.parse({
        version: 1,
        permissions: {
          allowedPaths: ['./src/**/*'],
          deniedPaths: ['**/.git/**'],
          allowedCommands: ['git *'],
          deniedCommands: ['rm *'],
          requireApproval: true,
          maxFileSize: 5000000,
          timeout: 60000,
        },
        mcp: {
          servers: [
            {
              name: 'filesystem',
              type: 'stdio',
              command: 'npx',
              args: ['-y', '@modelcontextprotocol/server-filesystem', '.'],
            },
          ],
        },
        agent: {
          defaultProvider: 'openai',
          defaultModel: 'gpt-4',
          maxIterations: 15,
          autoApprove: false,
          sandbox: 'docker',
        },
      });
      
      expect(result.version).toBe(1);
      expect(result.permissions.allowedPaths).toEqual(['./src/**/*']);
      expect(result.mcp.servers).toHaveLength(1);
      expect(result.agent.defaultProvider).toBe('openai');
    });

    it('should require version 1', () => {
      expect(() => {
        MonkeyCoderConfigSchema.parse({
          version: 2,
        });
      }).toThrow();
    });

    it('should merge partial configs with defaults', () => {
      const result = MonkeyCoderConfigSchema.parse({
        permissions: {
          allowedPaths: ['./custom/**/*'],
        },
      });
      
      expect(result.permissions.allowedPaths).toEqual(['./custom/**/*']);
      expect(result.permissions.deniedPaths).toContain('**/.env*'); // Should have defaults
      expect(result.version).toBe(1); // Should have version default
      expect(result.agent.defaultProvider).toBe('anthropic'); // Should have agent defaults
    });
  });
});
