---
id: quick-start
slug: /
title: Quick Start
---

Welcome to the Quick Start guide for Monkey Coder!

In this guide, you'll learn how to quickly get up and running with Monkey Coder, an AI-powered code generation platform. Follow the steps below to start creating and analyzing code.

## Installation

1. Ensure you have Yarn installed.

   ```bash
   yarn --version
   ```

2. Clone the Monkey Coder repository:

   ```bash
   git clone https://github.com/GaryOcean428/monkey-coder.git
   ```

3. Navigate to the project directory:

   ```bash
   cd monkey-coder
   ```

4. Install dependencies:

   ```bash
   yarn install
   ```

## Generate Your First Code

With the environment set up, let's generate some code.

```bash
yarn run generate "Create a REST API endpoint for user management"
```

## Analyze Existing Code

To analyze existing code for improvements:

```bash
yarn run analyze ./src/sampleCode.ts
```

That's it! You are now ready to explore the capabilities of Monkey Coder!

## Try It Interactive

Test Monkey Coder concepts right here in your browser:

```jsx live
function MonkeyCoderExample() {
  const [code, setCode] = React.useState('console.log("Hello from Monkey Coder!");');
  const [output, setOutput] = React.useState('');
  
  const runCode = () => {
    try {
      // Simulate code execution (in real implementation, this would use WebContainer)
      const result = eval(code);
      setOutput(result || 'Code executed successfully!');
    } catch (error) {
      setOutput(`Error: ${error.message}`);
    }
  };
  
  return (
    <div style={{ border: '1px solid #ccc', borderRadius: '8px', padding: '1rem' }}>
      <h4>Interactive JavaScript Example</h4>
      <textarea 
        value={code} 
        onChange={(e) => setCode(e.target.value)}
        style={{ width: '100%', height: '100px', marginBottom: '1rem' }}
      />
      <button onClick={runCode} style={{ marginBottom: '1rem' }}>Run Code</button>
      <div style={{ background: '#f5f5f5', padding: '0.5rem', borderRadius: '4px' }}>
        <strong>Output:</strong> {output}
      </div>
    </div>
  );
}
```

*Note: This is a simplified example. The full Monkey Coder platform provides much more sophisticated code generation and analysis capabilities.*
