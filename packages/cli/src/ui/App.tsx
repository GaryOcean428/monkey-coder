/**
 * App - Main Ink UI application component
 */
import React, { useState, useEffect, useCallback } from 'react';
import { render, Box, Text, useInput, useApp } from 'ink';
import { MessageComponent } from './components/MessageComponent.js';
import { ToolApproval } from './components/ToolApproval.js';
import { TaskList } from './components/TaskList.js';
import { useSession } from './hooks/useSession.js';
import { useAgent } from './hooks/useAgent.js';
import { AppStatus } from './types.js';

export interface AppProps {
  initialPrompt?: string;
  mode: 'chat' | 'agent';
  workingDirectory?: string;
  mcpServers?: Array<{
    name: string;
    type: 'stdio' | 'sse' | 'http';
    command?: string;
    args?: string[];
    url?: string;
  }>;
  onMessage?: (content: string) => Promise<string>;
}

export const App: React.FC<AppProps> = ({
  initialPrompt,
  mode,
  workingDirectory,
  mcpServers,
  onMessage,
}) => {
  const { exit } = useApp();
  const [status, setStatus] = useState<AppStatus>('idle');
  const [input, setInput] = useState('');
  const [inputEnabled, setInputEnabled] = useState(true);
  const [isThinking, setIsThinking] = useState(false);

  // Session management
  const { sessionId, messages, addMessage, getTokenCount } = useSession({
    workingDirectory,
  });

  // Agent management (only in agent mode)
  const {
    tasks,
    currentTool,
    pendingToolCall,
    executeTool,
    approveTool,
    rejectTool,
    isExecuting,
  } = useAgent({
    mcpServers: mode === 'agent' ? mcpServers : undefined,
    autoApprove: false,
  });

  // Handle initial prompt
  useEffect(() => {
    if (initialPrompt && sessionId) {
      handleSubmit(initialPrompt);
    }
  }, [initialPrompt, sessionId]);

  // Global keyboard shortcuts
  useInput((char: string, key: { escape?: boolean; ctrl?: boolean; return?: boolean }) => {
    if (key.escape && !pendingToolCall) {
      exit();
    }
    if (key.ctrl && char === 'c') {
      exit();
    }
    
    // Handle input submission
    if (key.return && inputEnabled && input.trim()) {
      handleSubmit(input);
    }
    
    // Handle text input (simple character append)
    if (inputEnabled && !key.return && !key.escape && !key.ctrl && char.length === 1) {
      setInput(prev => prev + char);
    }
    
    // Handle backspace
    if (inputEnabled && key.return === undefined && char === '') {
      setInput(prev => prev.slice(0, -1));
    }
  });

  const handleSubmit = useCallback(
    async (value: string) => {
      if (!value.trim() || !sessionId) return;

      const userMessage = value.trim();
      setInput('');
      setInputEnabled(false);
      setStatus('thinking');
      setIsThinking(true);

      // Add user message
      addMessage('user', userMessage);

      try {
        // Call the onMessage handler if provided
        if (onMessage) {
          const response = await onMessage(userMessage);
          addMessage('assistant', response);
        }

        setStatus('idle');
      } catch (error) {
        addMessage('system', `Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
        setStatus('error');
      } finally {
        setInputEnabled(true);
        setIsThinking(false);
      }
    },
    [sessionId, addMessage, onMessage]
  );

  const tokenCount = getTokenCount();

  return (
    <Box flexDirection="column" padding={1}>
      {/* Header */}
      <Box
        borderStyle="round"
        borderColor="cyan"
        paddingX={2}
        marginBottom={1}
      >
        <Text bold color="cyan">
          🐵 Monkey Coder
        </Text>
        <Text color="gray"> | Mode: {mode}</Text>
        {tokenCount > 0 && (
          <Text color="gray"> | Tokens: {tokenCount}</Text>
        )}
      </Box>

      {/* Messages */}
      <Box flexDirection="column" marginBottom={1}>
        {messages.length === 0 ? (
          <Box marginY={1}>
            <Text color="gray" dimColor>
              No messages yet. Start typing to chat with Monkey Coder!
            </Text>
          </Box>
        ) : (
          messages.map((msg) => <MessageComponent key={msg.id} message={msg} />)
        )}
      </Box>

      {/* Tool Approval */}
      {pendingToolCall && (
        <Box marginBottom={1}>
          <ToolApproval
            toolName={pendingToolCall.name}
            args={pendingToolCall.args}
            onApprove={approveTool}
            onReject={rejectTool}
          />
        </Box>
      )}

      {/* Task Progress */}
      {mode === 'agent' && tasks.length > 0 && (
        <Box marginBottom={1}>
          <TaskList tasks={tasks} />
        </Box>
      )}

      {/* Status */}
      {isThinking && !isExecuting && (
        <Box marginBottom={1}>
          <Text color="yellow">⏳ AI is thinking...</Text>
        </Box>
      )}

      {status === 'executing' && currentTool && (
        <Box flexDirection="column" marginBottom={1}>
          <Text color="yellow">⚡ Executing: {currentTool}</Text>
        </Box>
      )}

      {status === 'error' && (
        <Box marginBottom={1}>
          <Text color="red">⚠️ An error occurred. Please try again.</Text>
        </Box>
      )}

      {/* Input */}
      <Box borderStyle="single" borderColor="blue" paddingX={1}>
        <Text color="blue">› </Text>
        {inputEnabled ? (
          <Text>
            {input}
            <Text inverse> </Text>
          </Text>
        ) : (
          <Text color="gray" dimColor>
            Processing...
          </Text>
        )}
      </Box>

      {/* Help text */}
      <Box marginTop={1}>
        <Text color="gray" dimColor>
          Press ESC or Ctrl+C to exit | Press Enter to send
        </Text>
      </Box>
    </Box>
  );
};

/**
 * Render the Ink app
 */
export function renderApp(props: AppProps): { waitUntilExit: () => Promise<void> } {
  return render(<App {...props} />);
}
