import React from 'react';
import { useEffect } from 'react';
import IframeResizer from 'iframe-resizer-react'

interface PythonReplProps {
  initialCode?: string;
  title?: string;
  height?: string;
}

export default function PythonRepl({
  initialCode = "print('Hello from Monkey Coder!')",
  title = 'Interactive Python REPL',
  height = '600px'
}: PythonReplProps) {

  useEffect(() => {
    // Send initial code to the Python REPL on load
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  const handleMessage = (event: MessageEvent) => {
    if (event.isTrusted && event.data.type === 'SET_CODE') {
      if (event.source) {
        event.source.postMessage({
          type: 'INITIAL_CODE',
          payload: initialCode,
        }, event.origin);
      }
    }
  };

  return (
    <div style={{ margin: "1rem 0", border: "1px solid #ccc", borderRadius: "8px", overflow: "hidden" }}>
      <div style={{ padding: "0.75rem", backgroundColor: "#f5f5f5", borderBottom: "1px solid #ddd" }}>
        <h4 style={{ margin: 0 }}>{title}</h4>
      </div>
      <IframeResizer
        src="https://replit.com/@YourReplitAccount/your-repl?lite=true"
        style={{ width: '1px', minWidth: '100%', height }}
        frameBorder="0"
        checkOrigin={false}
      />
    </div>
  );
}

