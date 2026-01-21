#!/usr/bin/env node

/**
 * Manual test script for sandbox functionality
 * Tests different sandbox modes with simple commands
 */

import { getSandboxExecutor } from '../dist/sandbox/index.js';

async function testSandboxModes() {
  console.log('🧪 Testing Sandbox Modes\n');

  // Test 1: Spawn mode (default)
  console.log('📦 Test 1: Spawn mode (default)');
  const spawnExecutor = getSandboxExecutor({ mode: 'spawn' });
  const spawnResult = await spawnExecutor.execute('echo', ['Hello from spawn mode']);
  console.log(`   Exit code: ${spawnResult.exitCode}`);
  console.log(`   Output: ${spawnResult.stdout.trim()}`);
  console.log(`   Timed out: ${spawnResult.timedOut}`);
  console.log('');

  // Test 2: None mode (unsafe)
  console.log('⚠️  Test 2: None mode (unsafe)');
  const noneExecutor = getSandboxExecutor({ mode: 'none' });
  const noneResult = await noneExecutor.execute('whoami', []);
  console.log(`   Exit code: ${noneResult.exitCode}`);
  console.log(`   Output: ${noneResult.stdout.trim()}`);
  console.log('');

  // Test 3: Docker mode (will fall back to spawn if Docker unavailable)
  console.log('🐳 Test 3: Docker mode (with fallback)');
  const dockerExecutor = getSandboxExecutor({ mode: 'docker' });
  const dockerAvailable = await dockerExecutor.isDockerAvailable();
  console.log(`   Docker available: ${dockerAvailable}`);
  const dockerResult = await dockerExecutor.execute('echo', ['Hello from Docker mode']);
  console.log(`   Exit code: ${dockerResult.exitCode}`);
  console.log(`   Output: ${dockerResult.stdout.trim()}`);
  console.log('');

  // Test 4: Timeout test
  console.log('⏱️  Test 4: Timeout test (2 second timeout)');
  const timeoutExecutor = getSandboxExecutor({ mode: 'spawn', timeout: 2000 });
  const timeoutResult = await timeoutExecutor.execute('sleep', ['5']);
  console.log(`   Exit code: ${timeoutResult.exitCode}`);
  console.log(`   Timed out: ${timeoutResult.timedOut}`);
  console.log('');

  // Test 5: Working directory
  console.log('📁 Test 5: Working directory');
  const cwdExecutor = getSandboxExecutor({ mode: 'spawn', workdir: '/tmp' });
  const cwdResult = await cwdExecutor.execute('pwd', []);
  console.log(`   Exit code: ${cwdResult.exitCode}`);
  console.log(`   Working dir: ${cwdResult.stdout.trim()}`);
  console.log('');

  console.log('✅ All sandbox tests completed!');
}

testSandboxModes().catch(console.error);
