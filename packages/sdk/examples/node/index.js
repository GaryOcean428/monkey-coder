/**
 * Node.js Example - Monkey Coder SDK
 * 
 * This example demonstrates how to use the Monkey Coder SDK in a Node.js environment.
 */

import { MonkeyCoderClient, createCodeGenerationRequest } from '@monkey-coder/sdk';

async function main() {
  // Initialize the client
  const client = new MonkeyCoderClient({
    baseURL: process.env.MONKEY_CODER_BASE_URL || 
      (process.env.RAILWAY_PUBLIC_DOMAIN ? `https://${process.env.RAILWAY_PUBLIC_DOMAIN}` : 'http://localhost:8000'),
    apiKey: process.env.MONKEY_CODER_API_KEY,
    retries: 3,
    timeout: 30000, // 30 seconds
    onRetry: (retryCount, error) => {
      console.log(`Retry attempt ${retryCount}: ${error.message}`);
    }
  });

  try {
    // Health check
    console.log('Checking API health...');
    const health = await client.health();
    console.log('Health check:', health);

    // Code generation example
    console.log('\nGenerating code...');
    const request = createCodeGenerationRequest(
      'Create a Node.js Express server with authentication middleware',
      'user123',
      {
        language: 'javascript',
        temperature: 0.2,
        max_tokens: 2048
      }
    );

    // Non-streaming execution
    const response = await client.execute(request);
    console.log('Code generation completed:', {
      status: response.status,
      executionTime: response.execution_time,
      tokensUsed: response.usage?.tokens_used
    });

    if (response.result) {
      console.log('\nGenerated code:\n', response.result.result);
    }

    // Streaming execution example
    console.log('\nStreaming code generation...');
    const streamingRequest = createCodeGenerationRequest(
      'Create a React component for a todo list with TypeScript',
      'user123',
      {
        language: 'typescript',
        temperature: 0.1
      }
    );

    await client.executeStream(streamingRequest, (event) => {
      switch (event.type) {
        case 'start':
          console.log('⏳ Starting execution...');
          break;
        case 'progress':
          if (event.progress?.percentage) {
            console.log(`📊 Progress: ${event.progress.percentage}% - ${event.progress.step}`);
          }
          break;
        case 'result':
          console.log('✨ Intermediate result received');
          break;
        case 'complete':
          console.log('✅ Execution completed');
          if (event.data?.result) {
            console.log('\nFinal result:\n', event.data.result.result);
          }
          break;
        case 'error':
          console.error('❌ Error:', event.error?.message);
          break;
      }
    });

    // List available models
    console.log('\nListing available models...');
    const models = await client.listModels();
    console.log('Available models:', Object.keys(models.models || {}));

    // Usage metrics
    console.log('\nGetting usage metrics...');
    const usage = await client.getUsage({
      granularity: 'daily',
      include_details: true
    });
    console.log('Usage summary:', {
      totalRequests: usage.total_requests,
      totalTokens: usage.total_tokens,
      totalCost: usage.total_cost
    });

  } catch (error) {
    console.error('Error:', error.message);
    if (error.statusCode) {
      console.error('Status code:', error.statusCode);
    }
    if (error.details) {
      console.error('Details:', error.details);
    }
  }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\n👋 Shutting down...');
  process.exit(0);
});

main().catch(console.error);
