/**
 * Deno Example - Monkey Coder SDK
 * 
 * This example demonstrates how to use the Monkey Coder SDK in a Deno environment.
 * 
 * Run with: deno run --allow-net index.ts
 */

import { MonkeyCoderClient, createDocumentationRequest, createFileData } from '@monkey-coder/sdk';

const client = new MonkeyCoderClient({
  baseURL: Deno.env.get('MONKEY_CODER_BASE_URL') || 
    (Deno.env.get('RAILWAY_PUBLIC_DOMAIN') ? `https://${Deno.env.get('RAILWAY_PUBLIC_DOMAIN')}` : 'http://localhost:8000'),
  apiKey: Deno.env.get('MONKEY_CODER_API_KEY'),
  retries: 1,
  timeout: 50000, // 50 seconds
  onRetry: (retryCount, error) => {
    console.log(`🔄 Retry attempt ${retryCount}: ${error.message}`);
  }
});

async function main() {
  console.log('📜 Deno + Monkey Coder SDK Example');

  try {
    // Health check
    console.log('Checking API health...');
    const health = await client.health();
    console.log('Health check:', health);

    // Create documentation file data
    const fileData = createFileData('./docs/api-spec.md', '# API Specification\n\nDefine the API...', 'markdown');

    // Documentation generation
    console.log('Generating API documentation...');
    const request = createDocumentationRequest(
      'Generate detailed API documentation from the provided markdown file',
      'deno-user',
      [fileData],
      'API documentation'
    );

    const response = await client.execute(request);
    console.log('Documentation generation completed:', {
      status: response.status,
      executionTime: response.execution_time,
      tokensUsed: response.usage?.tokens_used
    });

    if (response.result) {
      console.log('\nGenerated Documentation:\n', response.result.result);
    }

    // List available providers
    console.log('\nListing available providers...');
    const providers = await client.listProviders();
    const availableProviders = Object.keys(providers.providers || {});
    console.log('Available providers:', availableProviders);

  } catch (error) {
    console.error('❌ Error:', error.message);
    if (error.statusCode) {
      console.error('Status code:', error.statusCode);
    }
    if (error.details) {
      console.error('Details:', error.details);
    }
  }
}

main().catch(console.error);

// Handle shutdown
self.addEventListener('unload', () => {
  console.log('👋 Shutting down...');
});
