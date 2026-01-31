/**
 * DiffViewer - Display file diffs with syntax highlighting
 */
import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';

import { DiffLine } from '../types.js';

interface DiffViewerProps {
  filename: string;
  diff: DiffLine[];
  onApprove?: () => void;
  onReject?: () => void;
  showApproval?: boolean;
}

export const DiffViewer: React.FC<DiffViewerProps> = ({ 
  filename, 
  diff, 
  onApprove, 
  onReject,
  showApproval = false 
}) => {
  const [responded, setResponded] = useState(false);

  useInput((char: string, key: { return?: boolean; escape?: boolean }) => {
    if (!showApproval || responded) return;

    if ((char === 'y' || char === 'Y' || key.return) && onApprove) {
      setResponded(true);
      onApprove();
    }
    if ((char === 'n' || char === 'N' || key.escape) && onReject) {
      setResponded(true);
      onReject();
    }
  });

  const getLineColor = (type: DiffLine['type']) => {
    switch (type) {
      case 'add':
        return 'green';
      case 'remove':
        return 'red';
      case 'context':
      default:
        return 'gray';
    }
  };

  const getLinePrefix = (type: DiffLine['type']) => {
    switch (type) {
      case 'add':
        return '+ ';
      case 'remove':
        return '- ';
      case 'context':
      default:
        return '  ';
    }
  };

  return (
    <Box flexDirection="column" borderStyle="single" borderColor="gray">
      <Box paddingX={1}>
        <Text bold color="white" inverse>{filename}</Text>
      </Box>
      <Box flexDirection="column" paddingX={1} paddingY={1}>
        {diff.map((line, i) => (
          <Box key={i}>
            {line.lineNumber !== undefined && (
              <Text color="gray" dimColor>
                {String(line.lineNumber).padStart(4, ' ')}{' '}
              </Text>
            )}
            <Text color={getLineColor(line.type)}>
              {getLinePrefix(line.type)}{line.content}
            </Text>
          </Box>
        ))}
      </Box>
      {showApproval && !responded && (
        <Box borderStyle="single" borderColor="yellow" paddingX={1} marginTop={1}>
          <Text>Apply changes? </Text>
          <Text color="green" bold>[Y]</Text>
          <Text>es / </Text>
          <Text color="red" bold>[N]</Text>
          <Text>o</Text>
        </Box>
      )}
    </Box>
  );
};
