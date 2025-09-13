#!/usr/bin/env node
/**
 * Test script for direct Monkey Coder backend API access using Node.js.
 * 
 * This script demonstrates how to integrate with the Monkey Coder backend
 * from external Node.js projects.
 */

class MonkeyCoderBackendClient {
    constructor(baseUrl = 'http://localhost:8000', apiKey = null) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.apiKey = apiKey;
    }

    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.apiKey) {
            headers.Authorization = `Bearer ${this.apiKey}`;
        }

        const response = await fetch(url, {
            ...options,
            headers
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    async createDevApiKey() {
        return await this.makeRequest('/api/v1/auth/keys/dev', {
            method: 'POST'
        });
    }

    async checkHealth() {
        return await this.makeRequest('/health');
    }

    async getAuthStatus() {
        if (!this.apiKey) {
            throw new Error('API key required for authentication check');
        }
        return await this.makeRequest('/api/v1/auth/status');
    }

    async executeTask(prompt, taskType = 'code_generation', persona = 'developer', options = {}) {
        if (!this.apiKey) {
            throw new Error('API key required for task execution');
        }

        const taskData = {
            task_id: `api-task-${Math.floor(Math.random() * 1000000)}`,
            task_type: taskType,
            prompt: prompt,
            context: {
                user_id: 'api-user',
                session_id: `session-${Math.floor(Math.random() * 1000)}`,
                environment: 'nodejs-backend-access',
                ...options.context
            },
            persona_config: {
                persona: persona,
                ...options.persona_config
            },
            ...options
        };

        return await this.makeRequest('/api/v1/execute', {
            method: 'POST',
            body: JSON.stringify(taskData)
        });
    }

    async getCapabilities() {
        return await this.makeRequest('/api/v1/capabilities');
    }
}

async function main() {
    console.log('🐒 Monkey Coder Backend API Access Test (Node.js)\n');

    const client = new MonkeyCoderBackendClient();

    // Test 1: Health check
    console.log('1. Testing backend health...');
    try {
        const health = await client.checkHealth();
        console.log(`   ✓ Backend is ${health.status}`);
        console.log(`   ✓ Version: ${health.version}`);
    } catch (error) {
        console.log(`   ✗ Health check failed: ${error.message}`);
        return;
    }

    // Test 2: Create API key
    console.log('\n2. Creating development API key...');
    let apiKey;
    try {
        const keyData = await client.createDevApiKey();
        apiKey = keyData.key;
        console.log(`   ✓ Created API key: ${apiKey.substring(0, 20)}...`);
        
        // Update client with new key
        client.apiKey = apiKey;
    } catch (error) {
        console.log(`   ✗ API key creation failed: ${error.message}`);
        return;
    }

    // Test 3: Authentication status
    console.log('\n3. Testing authentication...');
    try {
        const authStatus = await client.getAuthStatus();
        if (authStatus.authenticated) {
            const user = authStatus.user || {};
            console.log(`   ✓ Authenticated as: ${user.name || 'Unknown'}`);
            console.log(`   ✓ Subscription tier: ${user.subscription_tier || 'Unknown'}`);
            console.log(`   ✓ Credits: $${((user.credits || 0) / 100).toFixed(2)}`);
        } else {
            console.log('   ✗ Authentication failed');
            return;
        }
    } catch (error) {
        console.log(`   ✗ Authentication check failed: ${error.message}`);
        return;
    }

    // Test 4: Get capabilities
    console.log('\n4. Getting system capabilities...');
    try {
        const capabilities = await client.getCapabilities();
        console.log(`   ✓ Available features: ${(capabilities.features || []).length}`);
        console.log(`   ✓ Available models: ${(capabilities.models || []).length}`);
    } catch (error) {
        console.log(`   ✗ Capabilities check failed: ${error.message}`);
    }

    // Test 5: Execute a simple task
    console.log('\n5. Testing task execution...');
    try {
        const result = await client.executeTask(
            'Create a simple Hello World function in JavaScript',
            'code_generation'
        );

        const taskId = result.task_id || 'Unknown';
        const status = result.status || 'Unknown';
        const confidence = result.confidence || 0;

        console.log(`   ✓ Task executed: ${taskId}`);
        console.log(`   ✓ Status: ${status}`);
        console.log(`   ✓ Confidence: ${confidence}%`);

        // Show first 100 chars of result if available
        if (result.result) {
            const resultText = JSON.stringify(result.result).substring(0, 100);
            console.log(`   ✓ Result preview: ${resultText}...`);
        }
    } catch (error) {
        console.log(`   ✗ Task execution failed: ${error.message}`);
    }

    console.log('\n✅ Backend API access test completed!');
    console.log(`🔑 API Key: ${apiKey}`);
    console.log('📚 Full documentation: BACKEND_API_ACCESS.md');
}

// Run the test
main().catch(console.error);