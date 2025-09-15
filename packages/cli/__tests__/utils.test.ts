import { describe, it, expect, jest, beforeEach } from '@jest/globals';
import * as fs from 'fs-extra';
import * as path from 'path';
import {
  formatError,
  formatResponse,
  formatProgress,
  createProgressBar,
  detectLanguage,
  truncateText,
  formatFileSize,
  isValidJSON,
  parseFileArguments,
  generateUUID,
  sleep
} from '../src/utils';
import { ExecuteResponse } from '../src/types';

// Mock fs-extra
jest.mock('fs-extra');

describe('Utils Module', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('formatError', () => {
    it('formats Error objects correctly', () => {
      const error = new Error('Test error message');
      const result = formatError(error);
      expect(result).toContain('Test error message');
      expect(result).toContain('Error');
    });

    it('formats string errors correctly', () => {
      const result = formatError('Simple error string');
      expect(result).toContain('Simple error string');
      expect(result).toContain('Error');
    });
  });

  describe('formatResponse', () => {
    it('formats successful response with basic info', () => {
      const response: ExecuteResponse = {
        task_id: 'test-123',
        execution_id: 'exec-123',
        status: 'completed',
        created_at: new Date().toISOString(),
        persona_routing: {},
        monkey1_orchestration: {},
        orchestration_execution: {}
      };
      const result = formatResponse(response);
      expect(result).toContain('Task completed successfully');
      expect(result).toContain('test-123');
      expect(result).toContain('completed');
    });

    it('includes usage statistics when available', () => {
      const response: ExecuteResponse = {
        task_id: 'test-456',
        execution_id: 'exec-456',
        status: 'completed',
        created_at: new Date().toISOString(),
        persona_routing: {},
        monkey1_orchestration: {},
        orchestration_execution: {},
        usage: {
          tokens_used: 1000,
          tokens_input: 600,
          tokens_output: 400,
          provider_breakdown: { openai: 800, anthropic: 200 },
          execution_time: 2.5,
          cost_estimate: 0.0025
        }
      };
      const result = formatResponse(response);
      expect(result).toContain('Usage Statistics');
      expect(result).toContain('1000');
      expect(result).toContain('600');
      expect(result).toContain('400');
      expect(result).toContain('2.50s');
      expect(result).toContain('$0.0025');
    });

    it('includes result and artifacts when available', () => {
      const response: ExecuteResponse = {
        task_id: 'test-789',
        execution_id: 'exec-789',
        status: 'completed',
        created_at: new Date().toISOString(),
        persona_routing: {},
        monkey1_orchestration: {},
        orchestration_execution: {},
        result: {
          result: 'Task output here',
          metadata: { key: 'value' },
          artifacts: [
            { name: 'output.txt', type: 'file' },
            { name: 'report.pdf', type: 'document' }
          ],
          confidence_score: 0.95,
          quantum_collapse_info: {}
        }
      };
      const result = formatResponse(response);
      expect(result).toContain('Task output here');
      expect(result).toContain('95.0%');
      expect(result).toContain('output.txt');
      expect(result).toContain('report.pdf');
    });
  });

  describe('formatProgress', () => {
    it('formats progress with percentage', () => {
      const result = formatProgress('Processing files', 75);
      expect(result).toContain('Processing files');
      expect(result).toContain('75.0%');
      expect(result).toContain('[');
      expect(result).toContain(']');
    });

    it('formats progress without percentage', () => {
      const result = formatProgress('Initializing');
      expect(result).toContain('Initializing');
      expect(result).not.toContain('%');
    });

    it('includes metadata when provided', () => {
      const result = formatProgress('Analyzing', 50, {
        files: 10,
        errors: 0
      });
      expect(result).toContain('Analyzing');
      expect(result).toContain('50.0%');
      expect(result).toContain('files: 10');
      expect(result).toContain('errors: 0');
    });
  });

  describe('createProgressBar', () => {
    it('creates correct progress bar for 0%', () => {
      const bar = createProgressBar(0);
      expect(bar).toBe('[░░░░░░░░░░░░░░░░░░░░]');
    });

    it('creates correct progress bar for 50%', () => {
      const bar = createProgressBar(50);
      expect(bar).toBe('[██████████░░░░░░░░░░]');
    });

    it('creates correct progress bar for 100%', () => {
      const bar = createProgressBar(100);
      expect(bar).toBe('[████████████████████]');
    });

    it('respects custom width', () => {
      const bar = createProgressBar(50, 10);
      expect(bar).toBe('[█████░░░░░]');
    });
  });

  describe('detectLanguage', () => {
    it('detects JavaScript files', () => {
      expect(detectLanguage('test.js')).toBe('javascript');
      expect(detectLanguage('component.jsx')).toBe('javascript');
    });

    it('detects TypeScript files', () => {
      expect(detectLanguage('test.ts')).toBe('typescript');
      expect(detectLanguage('component.tsx')).toBe('typescript');
    });

    it('detects Python files', () => {
      expect(detectLanguage('script.py')).toBe('python');
    });

    it('detects various languages', () => {
      expect(detectLanguage('Main.java')).toBe('java');
      expect(detectLanguage('app.cpp')).toBe('cpp');
      expect(detectLanguage('main.go')).toBe('go');
      expect(detectLanguage('lib.rs')).toBe('rust');
      expect(detectLanguage('style.css')).toBe('css');
      expect(detectLanguage('index.html')).toBe('html');
      expect(detectLanguage('config.json')).toBe('json');
      expect(detectLanguage('docker-compose.yml')).toBe('yaml');
    });

    it('returns text for unknown extensions', () => {
      expect(detectLanguage('file.xyz')).toBe('text');
      expect(detectLanguage('noextension')).toBe('text');
    });
  });

  describe('truncateText', () => {
    it('returns short text unchanged', () => {
      const text = 'Short text';
      expect(truncateText(text, 20)).toBe(text);
    });

    it('truncates long text with ellipsis', () => {
      const text = 'This is a very long text that needs to be truncated';
      const result = truncateText(text, 20);
      expect(result).toBe('This is a very lo...');
      expect(result.length).toBe(20);
    });

    it('uses default max length of 100', () => {
      const text = 'a'.repeat(150);
      const result = truncateText(text);
      expect(result.length).toBe(100);
      expect(result.endsWith('...')).toBe(true);
    });
  });

  describe('formatFileSize', () => {
    it('formats bytes correctly', () => {
      expect(formatFileSize(500)).toBe('500.0 B');
      expect(formatFileSize(1023)).toBe('1023.0 B');
    });

    it('formats kilobytes correctly', () => {
      expect(formatFileSize(1024)).toBe('1.0 KB');
      expect(formatFileSize(2048)).toBe('2.0 KB');
      expect(formatFileSize(1536)).toBe('1.5 KB');
    });

    it('formats megabytes correctly', () => {
      expect(formatFileSize(1024 * 1024)).toBe('1.0 MB');
      expect(formatFileSize(1024 * 1024 * 5.5)).toBe('5.5 MB');
    });

    it('formats gigabytes correctly', () => {
      expect(formatFileSize(1024 * 1024 * 1024)).toBe('1.0 GB');
      expect(formatFileSize(1024 * 1024 * 1024 * 2.7)).toBe('2.7 GB');
    });
  });

  describe('isValidJSON', () => {
    it('validates correct JSON', () => {
      expect(isValidJSON('{"key": "value"}')).toBe(true);
      expect(isValidJSON('[1, 2, 3]')).toBe(true);
      expect(isValidJSON('"string"')).toBe(true);
      expect(isValidJSON('123')).toBe(true);
      expect(isValidJSON('true')).toBe(true);
      expect(isValidJSON('null')).toBe(true);
    });

    it('rejects invalid JSON', () => {
      expect(isValidJSON('{key: value}')).toBe(false);
      expect(isValidJSON('undefined')).toBe(false);
      expect(isValidJSON('')).toBe(false);
      expect(isValidJSON('{"unclosed": ')).toBe(false);
      expect(isValidJSON('NaN')).toBe(false);
    });
  });

  describe('parseFileArguments', () => {
    it('filters out option flags', () => {
      const args = ['file1.txt', '-v', 'file2.js', '--verbose', 'file3.py'];
      const result = parseFileArguments(args);
      expect(result).toEqual(['file1.txt', 'file2.js', 'file3.py']);
    });

    it('returns empty array when no files', () => {
      const args = ['-v', '--verbose', '--help'];
      const result = parseFileArguments(args);
      expect(result).toEqual([]);
    });

    it('handles mixed paths', () => {
      const args = ['./src/test.js', '../file.txt', '/absolute/path.py'];
      const result = parseFileArguments(args);
      expect(result).toEqual(['./src/test.js', '../file.txt', '/absolute/path.py']);
    });
  });

  describe('generateUUID', () => {
    it('generates valid UUID v4 format', () => {
      const uuid = generateUUID();
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
      expect(uuid).toMatch(uuidRegex);
    });

    it('generates unique UUIDs', () => {
      const uuid1 = generateUUID();
      const uuid2 = generateUUID();
      const uuid3 = generateUUID();
      expect(uuid1).not.toBe(uuid2);
      expect(uuid2).not.toBe(uuid3);
      expect(uuid1).not.toBe(uuid3);
    });
  });

  describe('sleep', () => {
    it('delays for specified time', async () => {
      const start = Date.now();
      await sleep(100);
      const elapsed = Date.now() - start;
      expect(elapsed).toBeGreaterThanOrEqual(90); // Allow some tolerance
      expect(elapsed).toBeLessThan(150);
    });

    it('returns a promise', () => {
      const result = sleep(10);
      expect(result).toBeInstanceOf(Promise);
    });
  });
});
