import React, { useState, useEffect, useRef } from 'react';
import { WebContainer } from '@webcontainer/api';
import styles from './styles.module.css';

interface JSReplProps {
  initialCode?: string;
  language?: 'javascript' | 'typescript';
  title?: string;
  showConsole?: boolean;
  height?: string;
}

export default function JSRepl({
  initialCode = 'console.log("Hello from Monkey Coder!");',
  language = 'javascript',
  title = 'Interactive JavaScript/TypeScript',
  showConsole = true,
  height = '400px'
}: JSReplProps) {
  const [code, setCode] = useState(initialCode);
  const [output, setOutput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [webcontainer, setWebcontainer] = useState<WebContainer | null>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    const initWebContainer = async () => {
      try {
        setIsLoading(true);
        const wc = await WebContainer.boot();
        setWebcontainer(wc);
        
        // Mount initial file structure
        await wc.mount({
          'package.json': {
            file: {
              contents: JSON.stringify({
                name: 'monkey-coder-repl',
                type: 'module',
                dependencies: {
                  ...(language === 'typescript' && { 
                    'typescript': '^5.0.0',
                    '@types/node': '^20.0.0',
                    'tsx': '^3.0.0'
                  })
                },
                scripts: {
                  start: language === 'typescript' ? 'tsx index.ts' : 'node index.js'
                }
              }, null, 2)
            }
          },
          [`index.${language === 'typescript' ? 'ts' : 'js'}`]: {
            file: {
              contents: code
            }
          }
        });

        // Install dependencies if TypeScript
        if (language === 'typescript') {
          const installProcess = await wc.spawn('npm', ['install']);
          await installProcess.exit;
        }

        setIsLoading(false);
      } catch (error) {
        console.error('Failed to initialize WebContainer:', error);
        setOutput('Error: Failed to initialize WebContainer');
        setIsLoading(false);
      }
    };

    initWebContainer();

    return () => {
      webcontainer?.teardown();
    };
  }, [language]);

  const runCode = async () => {
    if (!webcontainer) return;

    try {
      setIsLoading(true);
      setOutput('Running...');

      // Update the file with new code
      await webcontainer.fs.writeFile(
        `index.${language === 'typescript' ? 'ts' : 'js'}`,
        code
      );

      // Run the code
      const process = await webcontainer.spawn('npm', ['run', 'start'], {
        output: true
      });

      let output = '';
      process.output.pipeTo(new WritableStream({
        write(data) {
          output += data;
          setOutput(output);
        }
      }));

      await process.exit;
      setIsLoading(false);
    } catch (error) {
      setOutput(`Error: ${error.message}`);
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.replContainer} style={{ height }}>
      <div className={styles.header}>
        <h4>{title}</h4>
        <button 
          className={styles.runButton}
          onClick={runCode}
          disabled={isLoading || !webcontainer}
        >
          {isLoading ? '⏳ Running...' : '▶️ Run'}
        </button>
      </div>
      
      <div className={styles.content}>
        <div className={styles.editor}>
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className={styles.codeEditor}
            placeholder={`Enter your ${language} code here...`}
            spellCheck={false}
          />
        </div>
        
        {showConsole && (
          <div className={styles.console}>
            <div className={styles.consoleHeader}>Console Output</div>
            <pre className={styles.consoleOutput}>
              {output || 'Click "Run" to see output...'}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
