/**
 * Bun Example - Monkey Coder SDK
 * 
 * This example demonstrates how to use the Monkey Coder SDK with Bun runtime.
 * Run with: bun run index.ts
 */

import { MonkeyCoderClient, createCodeReviewRequest, createFileData } from '@monkey-coder/sdk';

async function main() {
  // Initialize the client with Bun-optimized settings
  const client = new MonkeyCoderClient({
    baseURL: process.env.MONKEY_CODER_BASE_URL || 'http://localhost:8000',
    apiKey: process.env.MONKEY_CODER_API_KEY,
    timeout: 60000, // 1 minute for code review
    retries: 2,
    onRetry: (retryCount, error) => {
      console.log(`🔄 Retry ${retryCount}: ${error.message}`);
    }
  });

  try {
    console.log('🍞 Bun + Monkey Coder SDK Example');
    
    // Health check
    const health = await client.health();
    console.log('✅ API Health:', health.status);

    // Read some TypeScript files for review
    const file1 = await Bun.file('./src/server.ts').text().catch(() => `
      import express from 'express';
      
      const app = express();
      
      app.get('/', (req, res) => {
        res.send('Hello World!');
      });
      
      app.listen(3000);
    `);

    const file2 = await Bun.file('./src/utils.ts').text().catch(() => `
      export function processData(data: any) {
        // TODO: Add input validation
        return data.map(item => item.value * 2);
      }
      
      export const config = {
        apiKey: 'hardcoded-key-123',
        timeout: 5000
      };
    `);

    // Create file data for review
    const files = [
      createFileData('./src/server.ts', file1, 'typescript'),
      createFileData('./src/utils.ts', file2, 'typescript')
    ];

    // Code review with streaming
    console.log('🔍 Starting code review...');
    
    const reviewRequest = createCodeReviewRequest(
      'Please review this TypeScript code for security issues, performance problems, and best practices',
      'bun-user',
      files,
      {
        focus_areas: ['security', 'performance', 'type-safety', 'best-practices']
      }
    );

    let reviewResult: any = null;

    await client.executeStream(reviewRequest, (event) => {
      switch (event.type) {
        case 'start':
          console.log('🚀 Review started...');
          break;
        case 'progress':
          if (event.progress?.percentage) {
            const bar = '█'.repeat(Math.floor(event.progress.percentage / 5));
            const empty = '░'.repeat(20 - Math.floor(event.progress.percentage / 5));
            console.log(`📊 [${bar}${empty}] ${event.progress.percentage}% - ${event.progress.step}`);
          }
          break;
        case 'result':
          console.log('📝 Analysis in progress...');
          break;
        case 'complete':
          console.log('✅ Review completed!');
          reviewResult = event.data;
          break;
        case 'error':
          console.error('❌ Review failed:', event.error?.message);
          break;
      }
    });

    if (reviewResult?.result) {
      console.log('📋 Review Results:');
      console.log('================');
      console.log(reviewResult.result.result);
      
      if (reviewResult.result.artifacts?.length > 0) {
        console.log('\n📎 Generated Artifacts:');
        reviewResult.result.artifacts.forEach((artifact: any, index: number) => {
          console.log(`${index + 1}. ${artifact.type}: ${artifact.title}`);
        });
      }

      console.log(`\n📊 Confidence Score: ${reviewResult.result.confidence_score}`);
      console.log(`⏱️  Execution Time: ${reviewResult.execution_time}s`);
      console.log(`🎯 Tokens Used: ${reviewResult.usage?.tokens_used || 'N/A'}`);
    }

    // List providers optimized for code review
    console.log('\n🤖 Available Providers:');
    const providers = await client.listProviders();
    Object.keys(providers.providers || {}).forEach(provider => {
      console.log(`  - ${provider}: ${providers.providers[provider].status}`);
    });

  } catch (error: any) {
    console.error('💥 Error:', error.message);
    if (error.code) {
      console.error('Code:', error.code);
    }
    process.exit(1);
  }
}

// Bun-specific cleanup
process.on('SIGTERM', () => {
  console.log('🛑 Received SIGTERM, shutting down gracefully...');
  process.exit(0);
});

console.log('Starting Bun example...');
await main();
