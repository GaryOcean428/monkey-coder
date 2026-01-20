/**
 * MessageComponent - Display individual chat messages with role-based styling
 */
import React from 'react';
import { Box, Text } from 'ink';
import { Message } from '../types.js';
import { CodeBlock } from './CodeBlock.js';
import { StreamingText } from './StreamingText.js';

interface MessageComponentProps {
  message: Message;
}

const roleColors = {
  user: 'green',
  assistant: 'cyan',
  tool: 'yellow',
  system: 'gray',
} as const;

const roleLabels = {
  user: 'You',
  assistant: 'Monkey',
  tool: 'Tool',
  system: 'System',
} as const;

export const MessageComponent: React.FC<MessageComponentProps> = ({ message }) => {
  const color = roleColors[message.role];
  const label = roleLabels[message.role];

  return (
    <Box flexDirection="column" marginBottom={1}>
      <Box>
        <Text color={color} bold>
          {label}
        </Text>
        {message.timestamp && (
          <Text color="gray" dimColor>
            {' '}· {new Date(message.timestamp).toLocaleTimeString()}
          </Text>
        )}
      </Box>
      <Box marginLeft={2} flexDirection="column">
        {message.isCode && message.language ? (
          <CodeBlock code={message.content} language={message.language} />
        ) : message.isStreaming ? (
          <StreamingText 
            chunks={[message.content]} 
            isComplete={false}
            showCursor={true}
          />
        ) : (
          <Text>{message.content}</Text>
        )}
      </Box>
    </Box>
  );
};
