/**
 * ToolApproval - Request user approval before executing tools
 */
import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';
import { highlight } from 'cli-highlight';

interface ToolApprovalProps {
  toolName: string;
  args: Record<string, unknown>;
  onApprove: () => void;
  onReject: () => void;
}

export const ToolApproval: React.FC<ToolApprovalProps> = ({
  toolName,
  args,
  onApprove,
  onReject,
}) => {
  const [responded, setResponded] = useState(false);

  useInput((char: string, key: { return?: boolean; escape?: boolean }) => {
    if (responded) return;

    if (char === 'y' || char === 'Y' || key.return) {
      setResponded(true);
      onApprove();
    }
    if (char === 'n' || char === 'N' || key.escape) {
      setResponded(true);
      onReject();
    }
  });

  let highlightedArgs: string;
  try {
    highlightedArgs = highlight(JSON.stringify(args, null, 2), { 
      language: 'json',
      ignoreIllegals: true 
    });
  } catch (_error) {
    highlightedArgs = JSON.stringify(args, null, 2);
  }

  return (
    <Box flexDirection="column" borderStyle="round" borderColor="yellow" padding={1}>
      <Box>
        <Text color="yellow" bold>⚠️  Tool Execution Request</Text>
      </Box>
      <Box marginTop={1}>
        <Text>Tool: </Text>
        <Text color="cyan" bold>{toolName}</Text>
      </Box>
      <Box marginTop={1} flexDirection="column">
        <Text>Arguments:</Text>
        <Box marginLeft={2} flexDirection="column">
          {highlightedArgs.split('\n').map((line, i) => (
            <Text key={i} color="gray">{line}</Text>
          ))}
        </Box>
      </Box>
      <Box marginTop={1}>
        <Text color="green" bold>[Y]</Text>
        <Text>es / </Text>
        <Text color="red" bold>[N]</Text>
        <Text>o / </Text>
        <Text color="gray">[ESC]</Text>
        <Text> to cancel</Text>
      </Box>
    </Box>
  );
};
