/**
 * Shared types for Ink UI components
 */

export type MessageRole = 'system' | 'user' | 'assistant' | 'tool';

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  isCode?: boolean;
  language?: string;
  timestamp?: number;
  toolCallId?: string;
  isStreaming?: boolean;
}

export type AppStatus = 'idle' | 'thinking' | 'executing' | 'error';

export interface DiffLine {
  type: 'add' | 'remove' | 'context';
  content: string;
  lineNumber?: number;
}

export interface Task {
  id: string;
  title: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  subtasks?: Task[];
}

export interface ToolCall {
  name: string;
  args: Record<string, unknown>;
}
