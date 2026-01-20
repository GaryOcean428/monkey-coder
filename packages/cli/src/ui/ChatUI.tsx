/**
 * ChatUI - Main chat interface with streaming support
 * Implementation per issue requirements
 */
import React, { useState, useCallback } from 'react';
import { render, Box, Text, useInput, useApp } from 'ink';

import { StreamingText } from './components/StreamingText.js';
import { isInteractiveTerminal } from './terminal-detection.js';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  isStreaming?: boolean;
}

export interface ChatUIProps {
  onSubmit: (message: string) => Promise<void>;
  messages: Message[];
  isProcessing: boolean;
  enableStreaming?: boolean;
}

export const ChatUI: React.FC<ChatUIProps> = ({ 
  onSubmit, 
  messages, 
  isProcessing,
  enableStreaming = true 
}) => {
  const [input, setInput] = useState('');
  const { exit } = useApp();

  useInput((char, key) => {
    if (key.escape) {
      exit();
    }
    if (key.return && input.trim() && !isProcessing) {
      handleSubmit();
    }
    // Handle typing
    if (!key.return && !key.escape && !key.ctrl && char && char.length === 1) {
      setInput(prev => prev + char);
    }
    // Handle backspace
    if (key.backspace || key.delete) {
      setInput(prev => prev.slice(0, -1));
    }
  });

  const handleSubmit = useCallback(async () => {
    if (!input.trim() || isProcessing) return;
    const msg = input;
    setInput('');
    await onSubmit(msg);
  }, [input, isProcessing, onSubmit]);

  return (
    <Box flexDirection="column" padding={1}>
      {/* Header */}
      <Box borderStyle="round" borderColor="cyan" paddingX={2} marginBottom={1}>
        <Text bold color="cyan">🐵 Monkey Coder</Text>
        <Text dimColor> | Ctrl+C or ESC to exit</Text>
      </Box>

      {/* Messages */}
      <Box flexDirection="column" flexGrow={1}>
        {messages.map((msg, i) => (
          <Box key={i} marginY={1}>
            <Text bold color={msg.role === 'user' ? 'blue' : 'green'}>
              {msg.role === 'user' ? 'You: ' : 'AI: '}
            </Text>
            {msg.isStreaming && enableStreaming ? (
              <StreamingText chunks={[msg.content]} isComplete={false} />
            ) : (
              <Text>{msg.content}</Text>
            )}
          </Box>
        ))}
      </Box>

      {/* Input */}
      <Box borderStyle="single" borderColor="gray" paddingX={1}>
        <Text color="blue">› </Text>
        {!isProcessing ? (
          <Text>
            {input}
            <Text inverse> </Text>
          </Text>
        ) : (
          <Text color="gray" dimColor>Processing...</Text>
        )}
      </Box>

      {/* Help text */}
      <Box marginTop={1}>
        <Text color="gray" dimColor>
          Press Enter to send | ESC or Ctrl+C to exit
        </Text>
      </Box>
    </Box>
  );
};

/**
 * Render the ChatUI component
 */
export function renderChatUI(props: ChatUIProps): { 
  waitUntilExit: () => Promise<void>;
  unmount: () => void;
} {
  // Check for interactive terminal support
  if (!isInteractiveTerminal()) {
    console.warn('⚠️  Non-interactive terminal detected. Using fallback mode.');
    console.warn('For best experience, use an interactive terminal (TTY).');
    // Return mock interface for non-interactive mode
    return {
      waitUntilExit: async () => {
        console.log('Running in non-interactive mode. Press Ctrl+C to exit.');
      },
      unmount: () => {},
    };
  }

  return render(<ChatUI {...props} />, { exitOnCtrlC: true });
}
