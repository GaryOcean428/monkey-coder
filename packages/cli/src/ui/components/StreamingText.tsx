/**
 * StreamingText - Display streaming text with animated cursor
 */
import React, { useState, useEffect } from 'react';
import { Box, Text } from 'ink';
import { Spinner } from '@inkjs/ui';

interface StreamingTextProps {
  chunks: string[];
  isComplete: boolean;
  showCursor?: boolean;
}

export const StreamingText: React.FC<StreamingTextProps> = ({ 
  chunks, 
  isComplete,
  showCursor = true 
}) => {
  const [cursorVisible, setCursorVisible] = useState(true);
  const text = chunks.join('');

  // Blinking cursor effect when streaming
  useEffect(() => {
    if (isComplete || !showCursor) return;

    const interval = setInterval(() => {
      setCursorVisible((prev) => !prev);
    }, 500);

    return () => clearInterval(interval);
  }, [isComplete, showCursor]);

  return (
    <Box flexDirection="row">
      <Text>{text}</Text>
      {!isComplete && showCursor && (
        <Text color="gray">{cursorVisible ? '▊' : ' '}</Text>
      )}
      {!isComplete && !showCursor && (
        <Box marginLeft={1}>
          <Spinner />
        </Box>
      )}
    </Box>
  );
};
