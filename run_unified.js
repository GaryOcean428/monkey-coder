#!/usr/bin/env node
/**
 * Unified process launcher for Railway
 * 1. Starts the Python backend on an internal port (8000)
 * 2. After a short delay, starts the Next.js server on the public port (Railway-assigned $PORT)
 *    and points NEXT_PUBLIC_API_URL to the backend.
 */

import { spawn } from 'node:child_process';

const PUBLIC_PORT = process.env.PORT || '3000';
const BACKEND_PORT = '8000';

// Helper to spawn a child process and inherit stdio
function start(cmd, args, env = {}) {
  const proc = spawn(cmd, args, {
    stdio: 'inherit',
    env: { ...process.env, ...env },
  });
  proc.on('exit', (code, signal) => {
    console.log(`[${cmd}] exited with code ${code} signal ${signal}`);
    process.exit(code || 0); // propagate exit to container
  });
  return proc;
}

// 1. Start Python backend
start('python', ['run_server.py'], { PORT: BACKEND_PORT });

// 2. After 5s, start Next.js frontend
setTimeout(() => {
  start(
    'yarn',
    ['workspace', '@monkey-coder/web', 'start'],
    {
      PORT: PUBLIC_PORT,
      NEXT_PUBLIC_API_URL: `http://127.0.0.1:${BACKEND_PORT}`,
    },
  );
}, 5000);
