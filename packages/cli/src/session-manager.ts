/**
 * Session Manager - Persistent conversation and context management
 * 
 * Provides SQLite-backed session persistence for multi-turn conversations,
 * context window management with token counting, and checkpoint integration.
 */

import Database, { Database as DatabaseType } from 'better-sqlite3';
import { encoding_for_model, TiktokenModel } from 'tiktoken';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { randomUUID } from 'crypto';

// Types
export interface Message {
  id: string;
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
  toolCallId?: string;
  tokenCount: number;
  createdAt: number;
}

export interface Session {
  id: string;
  name: string;
  workingDirectory: string;
  gitBranch?: string;
  createdAt: number;
  updatedAt: number;
  metadata: Record<string, unknown>;
}

export interface SessionContext {
  session: Session;
  messages: Message[];
  totalTokens: number;
}

// Configuration
const CONFIG_DIR = path.join(os.homedir(), '.monkey-coder');
const DB_PATH = path.join(CONFIG_DIR, 'sessions.db');
const CURRENT_SESSION_FILE = path.join(CONFIG_DIR, 'current_session');
const DEFAULT_MAX_TOKENS = 8000;

/**
 * Initialize the database schema
 */
function initializeSchema(db: DatabaseType): void {
  db.exec(`
    CREATE TABLE IF NOT EXISTS sessions (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      working_directory TEXT NOT NULL,
      git_branch TEXT,
      created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
      updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
      metadata TEXT DEFAULT '{}'
    );

    CREATE TABLE IF NOT EXISTS messages (
      id TEXT PRIMARY KEY,
      session_id TEXT NOT NULL,
      role TEXT NOT NULL CHECK(role IN ('system', 'user', 'assistant', 'tool')),
      content TEXT NOT NULL,
      tool_call_id TEXT,
      token_count INTEGER NOT NULL DEFAULT 0,
      created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
      FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, created_at);
    CREATE INDEX IF NOT EXISTS idx_sessions_updated ON sessions(updated_at DESC);
  `);
}

/**
 * Session Manager class for persistent conversation management
 */
export class SessionManager {
  private db: DatabaseType;
  private encoder: ReturnType<typeof encoding_for_model>;
  private maxTokens: number;

  constructor(options: { maxTokens?: number; model?: TiktokenModel } = {}) {
    // Ensure config directory exists
    if (!fs.existsSync(CONFIG_DIR)) {
      fs.mkdirSync(CONFIG_DIR, { recursive: true });
    }

    // Initialize database with WAL mode for performance
    this.db = new Database(DB_PATH);
    this.db.pragma('journal_mode = WAL');
    this.db.pragma('foreign_keys = ON');
    initializeSchema(this.db);

    // Initialize tokenizer
    this.encoder = encoding_for_model(options.model || 'gpt-4');
    this.maxTokens = options.maxTokens || DEFAULT_MAX_TOKENS;
  }

  /**
   * Count tokens in a string
   */
  countTokens(text: string): number {
    return this.encoder.encode(text).length;
  }

  /**
   * Create a new session
   */
  createSession(options: {
    name?: string;
    workingDirectory?: string;
    gitBranch?: string;
    metadata?: Record<string, unknown>;
  } = {}): Session {
    const id = randomUUID();
    const name = options.name || `Session ${new Date().toISOString().slice(0, 16)}`;
    const workingDirectory = options.workingDirectory || process.cwd();
    const now = Math.floor(Date.now() / 1000);

    const stmt = this.db.prepare(`
      INSERT INTO sessions (id, name, working_directory, git_branch, created_at, updated_at, metadata)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `);

    stmt.run(
      id,
      name,
      workingDirectory,
      options.gitBranch || null,
      now,
      now,
      JSON.stringify(options.metadata || {})
    );

    // Set as current session
    this.setCurrentSessionId(id);

    return {
      id,
      name,
      workingDirectory,
      gitBranch: options.gitBranch,
      createdAt: now,
      updatedAt: now,
      metadata: options.metadata || {},
    };
  }

  /**
   * Get a session by ID
   */
  getSession(sessionId: string): Session | null {
    const stmt = this.db.prepare('SELECT * FROM sessions WHERE id = ?');
    const row = stmt.get(sessionId) as any;

    if (!row) return null;

    return {
      id: row.id,
      name: row.name,
      workingDirectory: row.working_directory,
      gitBranch: row.git_branch,
      createdAt: row.created_at,
      updatedAt: row.updated_at,
      metadata: JSON.parse(row.metadata || '{}'),
    };
  }

  /**
   * List all sessions
   */
  listSessions(options: { limit?: number; offset?: number } = {}): Session[] {
    const limit = options.limit || 20;
    const offset = options.offset || 0;

    const stmt = this.db.prepare(`
      SELECT * FROM sessions 
      ORDER BY updated_at DESC 
      LIMIT ? OFFSET ?
    `);

    const rows = stmt.all(limit, offset) as any[];

    return rows.map(row => ({
      id: row.id,
      name: row.name,
      workingDirectory: row.working_directory,
      gitBranch: row.git_branch,
      createdAt: row.created_at,
      updatedAt: row.updated_at,
      metadata: JSON.parse(row.metadata || '{}'),
    }));
  }

  /**
   * Delete a session and all its messages
   */
  deleteSession(sessionId: string): boolean {
    const stmt = this.db.prepare('DELETE FROM sessions WHERE id = ?');
    const result = stmt.run(sessionId);
    return result.changes > 0;
  }

  /**
   * Add a message to a session
   */
  addMessage(
    sessionId: string,
    message: Omit<Message, 'id' | 'tokenCount' | 'createdAt'>
  ): Message {
    const id = randomUUID();
    const tokenCount = this.countTokens(message.content);
    const now = Math.floor(Date.now() / 1000);

    const stmt = this.db.prepare(`
      INSERT INTO messages (id, session_id, role, content, tool_call_id, token_count, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `);

    stmt.run(
      id,
      sessionId,
      message.role,
      message.content,
      message.toolCallId || null,
      tokenCount,
      now
    );

    // Update session timestamp
    this.db.prepare('UPDATE sessions SET updated_at = ? WHERE id = ?').run(now, sessionId);

    return {
      id,
      role: message.role,
      content: message.content,
      toolCallId: message.toolCallId,
      tokenCount,
      createdAt: now,
    };
  }

  /**
   * Get messages for a session with sliding window context management
   */
  getMessages(sessionId: string, options: { maxTokens?: number } = {}): Message[] {
    const maxTokens = options.maxTokens || this.maxTokens;

    const stmt = this.db.prepare(`
      SELECT * FROM messages 
      WHERE session_id = ? 
      ORDER BY created_at DESC
    `);

    const rows = stmt.all(sessionId) as any[];
    const messages: Message[] = [];
    let tokenCount = 0;

    // Build context from most recent, respecting token limit
    for (const row of rows) {
      if (tokenCount + row.token_count > maxTokens) break;

      messages.unshift({
        id: row.id,
        role: row.role,
        content: row.content,
        toolCallId: row.tool_call_id,
        tokenCount: row.token_count,
        createdAt: row.created_at,
      });

      tokenCount += row.token_count;
    }

    return messages;
  }

  /**
   * Get full session context with messages
   */
  getSessionContext(sessionId: string): SessionContext | null {
    const session = this.getSession(sessionId);
    if (!session) return null;

    const messages = this.getMessages(sessionId);
    const totalTokens = messages.reduce((sum, m) => sum + m.tokenCount, 0);

    return {
      session,
      messages,
      totalTokens,
    };
  }

  /**
   * Get/set current session ID (for --continue flag)
   */
  getCurrentSessionId(): string | null {
    try {
      if (fs.existsSync(CURRENT_SESSION_FILE)) {
        return fs.readFileSync(CURRENT_SESSION_FILE, 'utf-8').trim();
      }
    } catch {
      // Ignore read errors
    }
    return null;
  }

  setCurrentSessionId(sessionId: string): void {
    fs.writeFileSync(CURRENT_SESSION_FILE, sessionId, 'utf-8');
  }

  /**
   * Get or create session for current working directory
   */
  getOrCreateSession(options: {
    name?: string;
    continueSession?: boolean;
    sessionId?: string;
  } = {}): Session {
    // If specific session ID provided
    if (options.sessionId) {
      const session = this.getSession(options.sessionId);
      if (session) {
        this.setCurrentSessionId(session.id);
        return session;
      }
      throw new Error(`Session not found: ${options.sessionId}`);
    }

    // If --continue flag, use current session
    if (options.continueSession) {
      const currentId = this.getCurrentSessionId();
      if (currentId) {
        const session = this.getSession(currentId);
        if (session) return session;
      }
    }

    // Create new session
    return this.createSession({ name: options.name });
  }

  /**
   * Clear old sessions (retention policy)
   */
  cleanupOldSessions(maxAgeDays: number = 30, maxSessions: number = 100): number {
    const cutoff = Math.floor(Date.now() / 1000) - maxAgeDays * 24 * 60 * 60;

    // Delete sessions older than cutoff
    const stmt1 = this.db.prepare('DELETE FROM sessions WHERE updated_at < ?');
    const result1 = stmt1.run(cutoff);

    // Keep only most recent maxSessions
    const stmt2 = this.db.prepare(`
      DELETE FROM sessions WHERE id NOT IN (
        SELECT id FROM sessions ORDER BY updated_at DESC LIMIT ?
      )
    `);
    const result2 = stmt2.run(maxSessions);

    return result1.changes + result2.changes;
  }

  /**
   * Close database connection
   */
  close(): void {
    this.db.close();
  }
}

// Export singleton for convenience
let defaultManager: SessionManager | null = null;

export function getSessionManager(options?: { maxTokens?: number }): SessionManager {
  if (!defaultManager) {
    defaultManager = new SessionManager(options);
  }
  return defaultManager;
}

export function closeSessionManager(): void {
  if (defaultManager) {
    defaultManager.close();
    defaultManager = null;
  }
}
