/**
 * CodeBlock - Syntax highlighted code display component
 */
import React from 'react';
import { Box, Text } from 'ink';
import { highlight } from 'cli-highlight';

interface CodeBlockProps {
  code: string;
  language?: string;
  showLineNumbers?: boolean;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({ 
  code, 
  language = 'javascript',
  showLineNumbers = false 
}) => {
  let highlightedCode: string;
  
  try {
    highlightedCode = highlight(code, { 
      language,
      ignoreIllegals: true 
    });
  } catch (_error) {
    // Fallback to plain text if highlighting fails
    highlightedCode = code;
  }

  const lines = highlightedCode.split('\n');

  return (
    <Box flexDirection="column" borderStyle="round" borderColor="gray" paddingX={1}>
      <Box paddingX={1} marginBottom={1}>
        <Text bold color="white" inverse>{language}</Text>
      </Box>
      {lines.map((line, index) => (
        <Box key={index}>
          {showLineNumbers && (
            <Text color="gray" dimColor>
              {String(index + 1).padStart(4, ' ')} │{' '}
            </Text>
          )}
          <Text>{line}</Text>
        </Box>
      ))}
    </Box>
  );
};
