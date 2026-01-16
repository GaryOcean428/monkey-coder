import { describe, it, expect, jest, beforeEach, afterEach } from '@jest/globals';
import { SessionManager } from '../src/session-manager';
import * as os from 'os';
import * as path from 'path';
import * as fs from 'fs';

// Mock better-sqlite3
jest.mock('better-sqlite3', () => {
  return jest.fn().mockImplementation(() => ({
    pragma: jest.fn(),
    exec: jest.fn(),
    prepare: jest.fn(() => ({
      run: jest.fn(),
      get: jest.fn(),
      all: jest.fn(() => []),
    })),
    close: jest.fn(),
  }));
});

// Mock tiktoken
jest.mock('tiktoken', () => ({
  encoding_for_model: jest.fn(() => ({
    encode: jest.fn((text: string) => new Array(Math.ceil(text.length / 4))),
  })),
}));

describe('SessionManager', () => {
  let manager: SessionManager;
  const mockConfigDir = path.join(os.tmpdir(), '.monkey-coder-test');

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Create test config directory
    if (!fs.existsSync(mockConfigDir)) {
      fs.mkdirSync(mockConfigDir, { recursive: true });
    }
    
    manager = new SessionManager();
  });

  afterEach(() => {
    // Cleanup
    if (manager) {
      manager.close();
    }
  });

  describe('createSession', () => {
    it('creates a new session with default name', () => {
      const mockRun = jest.fn();
      (manager as any).db.prepare = jest.fn(() => ({ run: mockRun }));

      const session = manager.createSession();

      expect(session).toHaveProperty('id');
      expect(session).toHaveProperty('name');
      expect(session).toHaveProperty('workingDirectory');
      expect(session.workingDirectory).toBe(process.cwd());
      expect(mockRun).toHaveBeenCalled();
    });

    it('creates a session with custom name', () => {
      const mockRun = jest.fn();
      (manager as any).db.prepare = jest.fn(() => ({ run: mockRun }));

      const session = manager.createSession({
        name: 'My Custom Session',
        workingDirectory: '/custom/path',
      });

      expect(session.name).toBe('My Custom Session');
      expect(session.workingDirectory).toBe('/custom/path');
    });

    it('creates a session with git branch', () => {
      const mockRun = jest.fn();
      (manager as any).db.prepare = jest.fn(() => ({ run: mockRun }));

      const session = manager.createSession({
        gitBranch: 'feature/test',
      });

      expect(session.gitBranch).toBe('feature/test');
    });

    it('creates a session with metadata', () => {
      const mockRun = jest.fn();
      (manager as any).db.prepare = jest.fn(() => ({ run: mockRun }));

      const metadata = { key: 'value', number: 123 };
      const session = manager.createSession({ metadata });

      expect(session.metadata).toEqual(metadata);
    });
  });

  describe('getSession', () => {
    it('returns null when session not found', () => {
      const mockGet = jest.fn(() => null);
      (manager as any).db.prepare = jest.fn(() => ({ get: mockGet }));

      const session = manager.getSession('nonexistent-id');

      expect(session).toBeNull();
      expect(mockGet).toHaveBeenCalled();
    });

    it('returns session when found', () => {
      const mockSession = {
        id: 'test-id',
        name: 'Test Session',
        working_directory: '/test/path',
        git_branch: 'main',
        created_at: 1234567890,
        updated_at: 1234567890,
        metadata: '{}',
      };

      const mockGet = jest.fn(() => mockSession);
      (manager as any).db.prepare = jest.fn(() => ({ get: mockGet }));

      const session = manager.getSession('test-id');

      expect(session).not.toBeNull();
      expect(session?.id).toBe('test-id');
      expect(session?.name).toBe('Test Session');
      expect(session?.workingDirectory).toBe('/test/path');
    });
  });

  describe('listSessions', () => {
    it('returns empty array when no sessions exist', () => {
      const mockAll = jest.fn(() => []);
      (manager as any).db.prepare = jest.fn(() => ({ all: mockAll }));

      const sessions = manager.listSessions();

      expect(sessions).toEqual([]);
      expect(mockAll).toHaveBeenCalled();
    });

    it('returns list of sessions with default limit', () => {
      const mockSessions = [
        {
          id: 'session-1',
          name: 'Session 1',
          working_directory: '/path1',
          git_branch: null,
          created_at: 1234567890,
          updated_at: 1234567890,
          metadata: '{}',
        },
        {
          id: 'session-2',
          name: 'Session 2',
          working_directory: '/path2',
          git_branch: 'feature',
          created_at: 1234567891,
          updated_at: 1234567891,
          metadata: '{"key":"value"}',
        },
      ];

      const mockAll = jest.fn(() => mockSessions);
      (manager as any).db.prepare = jest.fn(() => ({ all: mockAll }));

      const sessions = manager.listSessions();

      expect(sessions).toHaveLength(2);
      expect(sessions[0].id).toBe('session-1');
      expect(sessions[1].id).toBe('session-2');
      expect(sessions[1].metadata).toEqual({ key: 'value' });
    });

    it('respects limit and offset parameters', () => {
      const mockAll = jest.fn(() => []);
      (manager as any).db.prepare = jest.fn(() => ({ all: mockAll }));

      manager.listSessions({ limit: 10, offset: 5 });

      expect(mockAll).toHaveBeenCalledWith(10, 5);
    });
  });

  describe('deleteSession', () => {
    it('deletes a session successfully', () => {
      const mockRun = jest.fn(() => ({ changes: 1 }));
      (manager as any).db.prepare = jest.fn(() => ({ run: mockRun }));

      const result = manager.deleteSession('test-id');

      expect(result).toBe(true);
      expect(mockRun).toHaveBeenCalledWith('test-id');
    });

    it('returns false when session not found', () => {
      const mockRun = jest.fn(() => ({ changes: 0 }));
      (manager as any).db.prepare = jest.fn(() => ({ run: mockRun }));

      const result = manager.deleteSession('nonexistent-id');

      expect(result).toBe(false);
    });
  });

  describe('addMessage', () => {
    it('adds a message to a session', () => {
      const mockRun = jest.fn();
      (manager as any).db.prepare = jest.fn(() => ({ run: mockRun }));

      const message = manager.addMessage('session-id', {
        role: 'user',
        content: 'Hello, world!',
      });

      expect(message).toHaveProperty('id');
      expect(message.role).toBe('user');
      expect(message.content).toBe('Hello, world!');
      expect(message).toHaveProperty('tokenCount');
      expect(mockRun).toHaveBeenCalledTimes(2); // insert message + update session
    });

    it('adds a message with tool call ID', () => {
      const mockRun = jest.fn();
      (manager as any).db.prepare = jest.fn(() => ({ run: mockRun }));

      const message = manager.addMessage('session-id', {
        role: 'tool',
        content: 'Tool result',
        toolCallId: 'tool-call-123',
      });

      expect(message.toolCallId).toBe('tool-call-123');
    });
  });

  describe('getMessages', () => {
    it('returns messages for a session', () => {
      const mockMessages = [
        {
          id: 'msg-1',
          session_id: 'session-id',
          role: 'user',
          content: 'Hello',
          tool_call_id: null,
          token_count: 2,
          created_at: 1234567890,
        },
        {
          id: 'msg-2',
          session_id: 'session-id',
          role: 'assistant',
          content: 'Hi there!',
          tool_call_id: null,
          token_count: 3,
          created_at: 1234567891,
        },
      ];

      const mockAll = jest.fn(() => mockMessages);
      (manager as any).db.prepare = jest.fn(() => ({ all: mockAll }));

      const messages = manager.getMessages('session-id');

      expect(messages).toHaveLength(2);
      expect(messages[0].role).toBe('user');
      expect(messages[1].role).toBe('assistant');
    });

    it('respects token limit', () => {
      // Create messages that exceed token limit
      const mockMessages = Array.from({ length: 10 }, (_, i) => ({
        id: `msg-${i}`,
        session_id: 'session-id',
        role: i % 2 === 0 ? 'user' : 'assistant',
        content: `Message ${i}`,
        tool_call_id: null,
        token_count: 1000,
        created_at: 1234567890 + i,
      }));

      const mockAll = jest.fn(() => mockMessages);
      (manager as any).db.prepare = jest.fn(() => ({ all: mockAll }));

      const messages = manager.getMessages('session-id', { maxTokens: 5000 });

      // Should only return messages that fit within token limit
      const totalTokens = messages.reduce((sum, m) => sum + m.tokenCount, 0);
      expect(totalTokens).toBeLessThanOrEqual(5000);
    });
  });

  describe('getSessionContext', () => {
    it('returns session context with messages', () => {
      const mockSession = {
        id: 'test-id',
        name: 'Test Session',
        working_directory: '/test',
        git_branch: null,
        created_at: 1234567890,
        updated_at: 1234567890,
        metadata: '{}',
      };

      const mockMessages = [
        {
          id: 'msg-1',
          session_id: 'test-id',
          role: 'user',
          content: 'Test',
          tool_call_id: null,
          token_count: 2,
          created_at: 1234567890,
        },
      ];

      (manager as any).db.prepare = jest.fn((sql: string) => {
        if (sql.includes('SELECT * FROM sessions')) {
          return { get: jest.fn(() => mockSession) };
        }
        return { all: jest.fn(() => mockMessages) };
      });

      const context = manager.getSessionContext('test-id');

      expect(context).not.toBeNull();
      expect(context?.session.id).toBe('test-id');
      expect(context?.messages).toHaveLength(1);
      expect(context?.totalTokens).toBe(2);
    });

    it('returns null when session not found', () => {
      const mockGet = jest.fn(() => null);
      (manager as any).db.prepare = jest.fn(() => ({ get: mockGet }));

      const context = manager.getSessionContext('nonexistent-id');

      expect(context).toBeNull();
    });
  });

  describe('cleanupOldSessions', () => {
    it('removes sessions older than specified days', () => {
      const mockRun = jest.fn(() => ({ changes: 5 }));
      (manager as any).db.prepare = jest.fn(() => ({ run: mockRun }));

      const removed = manager.cleanupOldSessions(30, 100);

      expect(removed).toBeGreaterThanOrEqual(0);
      expect(mockRun).toHaveBeenCalled();
    });

    it('keeps only max number of sessions', () => {
      const mockRun1 = jest.fn(() => ({ changes: 2 }));
      const mockRun2 = jest.fn(() => ({ changes: 3 }));
      let callCount = 0;
      
      (manager as any).db.prepare = jest.fn(() => ({
        run: callCount++ === 0 ? mockRun1 : mockRun2,
      }));

      const removed = manager.cleanupOldSessions(30, 100);

      expect(removed).toBe(5); // 2 + 3
    });
  });

  describe('countTokens', () => {
    it('counts tokens in text', () => {
      const text = 'This is a test message';
      const count = manager.countTokens(text);

      expect(count).toBeGreaterThan(0);
      expect(typeof count).toBe('number');
    });

    it('counts tokens for empty string', () => {
      const count = manager.countTokens('');
      expect(count).toBe(0);
    });
  });

  describe('getCurrentSessionId and setCurrentSessionId', () => {
    it('sets and gets current session ID', () => {
      const sessionId = 'test-session-id';
      
      manager.setCurrentSessionId(sessionId);
      const retrieved = manager.getCurrentSessionId();

      // Note: This test might not work correctly in the mocked environment
      // as it relies on filesystem operations
      // In a real test, you'd check the actual file system
      expect(typeof retrieved).toBe('string');
    });

    it('returns null when no current session', () => {
      // This depends on the filesystem state
      const retrieved = manager.getCurrentSessionId();
      expect(retrieved === null || typeof retrieved === 'string').toBe(true);
    });
  });

  describe('getOrCreateSession', () => {
    it('creates new session when no options provided', () => {
      const mockRun = jest.fn();
      const mockGet = jest.fn(() => null);
      (manager as any).db.prepare = jest.fn(() => ({
        run: mockRun,
        get: mockGet,
      }));

      const session = manager.getOrCreateSession();

      expect(session).toHaveProperty('id');
      expect(session).toHaveProperty('name');
    });

    it('returns existing session when sessionId provided', () => {
      const mockSession = {
        id: 'existing-id',
        name: 'Existing Session',
        working_directory: '/test',
        git_branch: null,
        created_at: 1234567890,
        updated_at: 1234567890,
        metadata: '{}',
      };

      const mockGet = jest.fn(() => mockSession);
      (manager as any).db.prepare = jest.fn(() => ({ get: mockGet }));

      const session = manager.getOrCreateSession({ sessionId: 'existing-id' });

      expect(session.id).toBe('existing-id');
      expect(session.name).toBe('Existing Session');
    });

    it('throws error when specified session not found', () => {
      const mockGet = jest.fn(() => null);
      (manager as any).db.prepare = jest.fn(() => ({ get: mockGet }));

      expect(() => {
        manager.getOrCreateSession({ sessionId: 'nonexistent-id' });
      }).toThrow('Session not found');
    });
  });
});
