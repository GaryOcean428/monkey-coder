/**
 * Tests for AgentRunner class
 */

import { describe, it, expect, jest } from '@jest/globals';

// Mock ora before importing AgentRunner
jest.mock('ora', () => {
  return jest.fn(() => ({
    start: jest.fn().mockReturnThis(),
    stop: jest.fn().mockReturnThis(),
    succeed: jest.fn().mockReturnThis(),
    fail: jest.fn().mockReturnThis(),
    warn: jest.fn().mockReturnThis(),
    info: jest.fn().mockReturnThis(),
    text: '',
  }));
});

// Mock session-manager
jest.mock('../src/session-manager', () => ({
  getSessionManager: jest.fn(() => ({
    createSession: jest.fn(),
    getSession: jest.fn(),
    updateSession: jest.fn(),
    listSessions: jest.fn(),
  })),
  Session: jest.fn(),
}));

// Mock checkpoint-manager
jest.mock('../src/checkpoint-manager', () => ({
  getCheckpointManager: jest.fn(() => ({
    saveCheckpoint: jest.fn(),
    loadCheckpoint: jest.fn(),
    listCheckpoints: jest.fn(),
  })),
}));

// Mock tools
jest.mock('../src/tools/index', () => ({
  TOOL_REGISTRY: {
    file_read: {
      name: 'file_read',
      description: 'Read a file',
      inputSchema: { type: 'object', properties: {} },
      execute: jest.fn(),
    },
    file_write: {
      name: 'file_write',
      description: 'Write a file',
      inputSchema: { type: 'object', properties: {} },
      execute: jest.fn(),
    },
    shell_execute: {
      name: 'shell_execute',
      description: 'Execute a shell command',
      inputSchema: { type: 'object', properties: {} },
      execute: jest.fn(),
    },
  },
  ToolResult: jest.fn(),
}));

// Mock api-client
jest.mock('../src/api-client', () => ({
  MonkeyCoderAPIClient: jest.fn(),
}));

import { AgentRunner } from '../src/agent-runner';

describe('AgentRunner', () => {
  describe('constructor', () => {
    it('should initialize with default options', () => {
      const runner = new AgentRunner();
      expect(runner).toBeInstanceOf(AgentRunner);
    });

    it('should accept custom options', () => {
      const runner = new AgentRunner({
        localOnly: true,
        requireApproval: false,
        model: 'gpt-4',
        maxIterations: 10,
      });
      expect(runner).toBeInstanceOf(AgentRunner);
    });
  });

  describe('tool schema building', () => {
    it('should build correct tool schemas', () => {
      const runner = new AgentRunner();
      const schemas = (runner as any).buildToolSchemas();

      expect(Array.isArray(schemas)).toBe(true);
      expect(schemas.length).toBeGreaterThan(0);
      
      const firstTool = schemas[0];
      expect(firstTool).toHaveProperty('type', 'function');
      expect(firstTool).toHaveProperty('function');
      expect(firstTool.function).toHaveProperty('name');
      expect(firstTool.function).toHaveProperty('description');
      expect(firstTool.function).toHaveProperty('parameters');
    });

    it('should include all tools from registry', () => {
      const runner = new AgentRunner();
      const schemas = (runner as any).buildToolSchemas();

      const toolNames = schemas.map((s: any) => s.function.name);
      expect(toolNames).toContain('file_read');
      expect(toolNames).toContain('file_write');
      expect(toolNames).toContain('shell_execute');
    });
  });

  describe('dangerous tool detection', () => {
    it('should identify dangerous tools', () => {
      const runner = new AgentRunner();
      
      expect((runner as any).isDangerous('shell_execute')).toBe(true);
      expect((runner as any).isDangerous('file_write')).toBe(true);
      expect((runner as any).isDangerous('file_delete')).toBe(true);
      expect((runner as any).isDangerous('file_edit')).toBe(true);
      expect((runner as any).isDangerous('file_read')).toBe(false);
      expect((runner as any).isDangerous('list_directory')).toBe(false);
    });
  });
});
