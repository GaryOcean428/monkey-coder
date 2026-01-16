/**
 * useSession - Hook for session management integration
 */
import { useState, useEffect, useCallback } from 'react';
import { SessionManager, Message as SessionMessage } from '../../session-manager.js';
import { Message } from '../types.js';

export interface UseSessionOptions {
  sessionId?: string;
  workingDirectory?: string;
  gitBranch?: string;
  maxTokens?: number;
}

export interface UseSessionReturn {
  sessionId: string | null;
  messages: Message[];
  addMessage: (role: Message['role'], content: string, isCode?: boolean, language?: string) => void;
  clearMessages: () => void;
  getTokenCount: () => number;
  loading: boolean;
  error: Error | null;
}

export function useSession(options: UseSessionOptions = {}): UseSessionReturn {
  const [sessionManager] = useState(() => new SessionManager({ maxTokens: options.maxTokens }));
  const [sessionId, setSessionId] = useState<string | null>(options.sessionId || null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Initialize or load session
  useEffect(() => {
    const initSession = async () => {
      setLoading(true);
      try {
        let currentSessionId = sessionId;
        
        if (!currentSessionId) {
          // Create new session
          const session = sessionManager.createSession({
            name: `Chat ${new Date().toISOString()}`,
            workingDirectory: options.workingDirectory || process.cwd(),
            gitBranch: options.gitBranch,
          });
          currentSessionId = session.id;
          setSessionId(currentSessionId);
        }

        // Load existing messages
        const context = sessionManager.getSessionContext(currentSessionId);
        if (context) {
          const loadedMessages: Message[] = context.messages.map((msg: SessionMessage) => ({
            id: msg.id,
            role: msg.role,
            content: msg.content,
            toolCallId: msg.toolCallId,
            timestamp: msg.createdAt,
          }));
          setMessages(loadedMessages);
        }
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    initSession();
  }, [sessionId, options.workingDirectory, options.gitBranch, sessionManager]);

  const addMessage = useCallback(
    (role: Message['role'], content: string, isCode?: boolean, language?: string) => {
      if (!sessionId) return;

      try {
        const message = sessionManager.addMessage(sessionId, {
          role,
          content,
          toolCallId: undefined,
        });
        
        const newMessage: Message = {
          id: message.id,
          role,
          content,
          isCode,
          language,
          timestamp: Date.now(),
        };

        setMessages((prev) => [...prev, newMessage]);
      } catch (err) {
        setError(err as Error);
      }
    },
    [sessionId, sessionManager]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const getTokenCount = useCallback(() => {
    if (!sessionId) return 0;
    const context = sessionManager.getSessionContext(sessionId);
    return context?.totalTokens || 0;
  }, [sessionId, sessionManager]);

  return {
    sessionId,
    messages,
    addMessage,
    clearMessages,
    getTokenCount,
    loading,
    error,
  };
}
