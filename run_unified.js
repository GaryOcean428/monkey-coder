#!/usr/bin/env node
/**
 * Unified process launcher for Railway production deployment
 * 
 * This script provides an alternative deployment strategy that runs both
 * the Python backend and Next.js frontend as separate processes in a single container.
 * 
 * Process flow:
 * 1. Starts the Python backend on internal port 8000
 * 2. Waits for backend to be ready (health check)
 * 3. Starts the Next.js server on the public port (Railway-assigned $PORT)
 * 4. Configures frontend to proxy API calls to the backend
 * 
 * Environment Variables:
 * - PORT: Railway-assigned public port (for Next.js)
 * - BACKEND_PORT: Internal port for Python API (default: 8000)
 * - FRONTEND_START_DELAY: Delay before starting frontend (default: 8000ms)
 * - HEALTH_CHECK_RETRIES: Number of backend health check attempts (default: 30)
 */

import { spawn } from 'node:child_process';
import { setTimeout } from 'node:timers';

const PUBLIC_PORT = process.env.PORT || '3000';
const BACKEND_PORT = process.env.BACKEND_PORT || '8000';
const FRONTEND_START_DELAY = parseInt(process.env.FRONTEND_START_DELAY || '8000');
const HEALTH_CHECK_RETRIES = parseInt(process.env.HEALTH_CHECK_RETRIES || '30');

// Track child processes for graceful shutdown
const childProcesses = [];

// Helper to spawn a child process and inherit stdio
function start(cmd, args, env = {}, name = cmd) {
  console.log(`[${name}] Starting: ${cmd} ${args.join(' ')}`);
  
  const proc = spawn(cmd, args, {
    stdio: 'inherit',
    env: { ...process.env, ...env },
  });
  
  childProcesses.push({ proc, name });
  
  proc.on('exit', (code, signal) => {
    console.log(`[${name}] exited with code ${code} signal ${signal}`);
    
    // If backend fails, exit immediately
    if (name === 'backend') {
      console.error(`[${name}] Backend process failed, shutting down...`);
      process.exit(code || 1);
    }
    
    // If frontend fails, try to restart it once
    if (name === 'frontend' && !proc._restarted) {
      console.log(`[${name}] Frontend failed, attempting restart in 5 seconds...`);
      proc._restarted = true;
      setTimeout(() => startFrontend(), 5000);
    }
  });
  
  return proc;
}

// Health check function for backend
async function waitForBackend() {
  console.log(`[health] Waiting for backend at http://127.0.0.1:${BACKEND_PORT}/health`);
  
  for (let i = 0; i < HEALTH_CHECK_RETRIES; i++) {
    try {
      // Use curl since it's available in most containers
      const { spawn } = await import('node:child_process');
      
      const curlCheck = spawn('curl', [
        '-s', '-f', '--max-time', '2',
        `http://127.0.0.1:${BACKEND_PORT}/health`
      ], { stdio: 'pipe' });
      
      const exitCode = await new Promise((resolve) => {
        curlCheck.on('exit', resolve);
      });
      
      if (exitCode === 0) {
        console.log(`[health] ✅ Backend is ready (attempt ${i + 1})`);
        return true;
      }
    } catch (error) {
      // Ignore curl errors, try next attempt
    }
    
    console.log(`[health] ⏳ Backend not ready, attempt ${i + 1}/${HEALTH_CHECK_RETRIES}`);
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  console.error(`[health] ❌ Backend failed to start after ${HEALTH_CHECK_RETRIES} attempts`);
  return false;
}

// Start frontend process
function startFrontend() {
  console.log(`[frontend] Starting Next.js on port ${PUBLIC_PORT}`);
  
  // Check if we need to build first
  const fs = require('fs');
  const path = require('path');
  const nextDir = path.join(process.cwd(), 'packages/web/.next');
  
  if (!fs.existsSync(nextDir)) {
    console.log(`[frontend] No .next directory found, building first...`);
    
    // Build the frontend first
    const buildProc = start(
      'yarn',
      ['workspace', '@monkey-coder/web', 'run', 'build'],
      {
        NODE_ENV: 'production',
        NEXT_PUBLIC_API_URL: `http://127.0.0.1:${BACKEND_PORT}`,
        NEXT_PUBLIC_APP_URL: `http://localhost:${PUBLIC_PORT}`,
      },
      'frontend-build'
    );
    
    buildProc.on('exit', (code) => {
      if (code === 0) {
        console.log(`[frontend] Build completed, starting server...`);
        startNextServer();
      } else {
        console.error(`[frontend] Build failed with code ${code}`);
        process.exit(1);
      }
    });
  } else {
    startNextServer();
  }
}

function startNextServer() {
  start(
    'yarn',
    ['workspace', '@monkey-coder/web', 'start'],
    {
      PORT: PUBLIC_PORT,
      NODE_ENV: 'production',
      NEXT_PUBLIC_API_URL: `http://127.0.0.1:${BACKEND_PORT}`,
      NEXT_PUBLIC_APP_URL: `http://localhost:${PUBLIC_PORT}`,
    },
    'frontend'
  );
}

// Graceful shutdown handler
function gracefulShutdown(signal) {
  console.log(`[main] Received ${signal}, shutting down gracefully...`);
  
  childProcesses.forEach(({ proc, name }) => {
    if (!proc.killed) {
      console.log(`[main] Terminating ${name}...`);
      proc.kill('SIGTERM');
    }
  });
  
  // Force exit after 10 seconds
  setTimeout(() => {
    console.log(`[main] Force exiting...`);
    process.exit(0);
  }, 10000);
}

// Register shutdown handlers
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Main execution
async function main() {
  console.log(`[main] 🚀 Starting unified Monkey Coder deployment`);
  console.log(`[main] Backend will run on port ${BACKEND_PORT}`);
  console.log(`[main] Frontend will run on port ${PUBLIC_PORT}`);
  
  // 1. Start Python backend
  const backendProc = start('python', ['run_server.py'], { PORT: BACKEND_PORT }, 'backend');
  
  // 2. Wait for backend to be ready
  console.log(`[main] ⏳ Waiting ${FRONTEND_START_DELAY}ms before health checks...`);
  await new Promise(resolve => setTimeout(resolve, FRONTEND_START_DELAY));
  
  const backendReady = await waitForBackend();
  if (!backendReady) {
    console.error(`[main] ❌ Backend startup failed, exiting...`);
    process.exit(1);
  }
  
  // 3. Start frontend
  startFrontend();
  
  console.log(`[main] ✅ Both services started successfully`);
  console.log(`[main] API available at: http://127.0.0.1:${BACKEND_PORT}`);
  console.log(`[main] Frontend available at: http://localhost:${PUBLIC_PORT}`);
}

// Execute main function
main().catch((error) => {
  console.error(`[main] ❌ Startup failed:`, error);
  process.exit(1);
});
