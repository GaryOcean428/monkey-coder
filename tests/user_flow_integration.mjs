#!/usr/bin/env node
/**
 * User Flow Integration Tests for Monkey Coder
 * 
 * Tests complete user journeys across the platform including:
 * - Authentication flows
 * - Task execution flows  
 * - Frontend/backend integration
 */

import fetch from 'node-fetch';

class UserFlowIntegrationTest {
    constructor(backendUrl = 'http://localhost:8000', frontendUrl = 'http://localhost:3000') {
        this.backendUrl = backendUrl.replace(/\/$/, '');
        this.frontendUrl = frontendUrl.replace(/\/$/, '');
        this.results = [];
    }

    async makeRequest(url, options = {}) {
        const startTime = Date.now();
        
        try {
            const response = await fetch(url, {
                timeout: 30000,
                ...options
            });
            
            const responseTime = Date.now() - startTime;
            const body = response.headers.get('content-type')?.includes('application/json') 
                ? await response.json().catch(() => null)
                : await response.text().catch(() => null);
            
            return {
                success: response.ok,
                status: response.status,
                responseTime,
                body,
                headers: Object.fromEntries(response.headers.entries())
            };
            
        } catch (error) {
            const responseTime = Date.now() - startTime;
            return {
                success: false,
                status: 0,
                responseTime,
                error: error.message,
                body: null,
                headers: {}
            };
        }
    }

    async testBackendFrontendHealthSync() {
        console.log('🔄 Testing Backend/Frontend Health Sync...');
        
        // Test backend health
        const backendHealth = await this.makeRequest(`${this.backendUrl}/health`);
        const backendStatus = backendHealth.success ? '✅' : '❌';
        console.log(`  ${backendStatus} Backend health - ${backendHealth.status} (${backendHealth.responseTime}ms)`);
        
        // Test frontend health
        const frontendHealth = await this.makeRequest(`${this.frontendUrl}/api/health`);
        const frontendStatus = frontendHealth.success ? '✅' : '❌';
        console.log(`  ${frontendStatus} Frontend health - ${frontendHealth.status} (${frontendHealth.responseTime}ms)`);
        
        // Test if both services are in sync
        const bothHealthy = backendHealth.success && frontendHealth.success;
        const syncStatus = bothHealthy ? '✅' : '❌';
        console.log(`  ${syncStatus} Health sync check`);
        
        this.results.push({
            test: 'Health Sync',
            success: bothHealthy,
            backend: backendHealth,
            frontend: frontendHealth
        });
        
        return bothHealthy;
    }

    async testAuthenticationFlow() {
        console.log('🔐 Testing Authentication Flow...');
        
        // Test auth status endpoint (should be unauthenticated)
        const authStatus = await this.makeRequest(`${this.backendUrl}/api/v1/auth/status`);
        const statusExpected = authStatus.status === 401; // Should be unauthorized
        const statusResult = statusExpected ? '✅' : '❌';
        console.log(`  ${statusResult} Auth status (unauthenticated) - ${authStatus.status} (${authStatus.responseTime}ms)`);
        
        // Test login endpoint with invalid credentials (should fail gracefully)
        const loginAttempt = await this.makeRequest(`${this.backendUrl}/api/v1/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: 'test@example.com',
                password: 'invalid'
            })
        });
        
        const loginExpected = [401, 422].includes(loginAttempt.status); // Should reject invalid creds
        const loginResult = loginExpected ? '✅' : '❌';
        console.log(`  ${loginResult} Login with invalid credentials - ${loginAttempt.status} (${loginAttempt.responseTime}ms)`);
        
        // Test frontend login page accessibility
        const loginPage = await this.makeRequest(`${this.frontendUrl}/login`);
        const pageResult = loginPage.success ? '✅' : '❌';
        console.log(`  ${pageResult} Frontend login page - ${loginPage.status} (${loginPage.responseTime}ms)`);
        
        const overallAuthSuccess = statusExpected && loginExpected && loginPage.success;
        
        this.results.push({
            test: 'Authentication Flow',
            success: overallAuthSuccess,
            components: {
                authStatus: { success: statusExpected, ...authStatus },
                loginAttempt: { success: loginExpected, ...loginAttempt },
                loginPage: { success: loginPage.success, ...loginPage }
            }
        });
        
        return overallAuthSuccess;
    }

    async testTaskExecutionFlow() {
        console.log('⚡ Testing Task Execution Flow...');
        
        // Test execute endpoint without auth (should require authentication)
        const executeUnauth = await this.makeRequest(`${this.backendUrl}/api/v1/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                task_type: 'code_generation',
                persona: 'developer',
                query: 'test query'
            })
        });
        
        const executeExpected = executeUnauth.status === 401; // Should require auth
        const executeResult = executeExpected ? '✅' : '❌';
        console.log(`  ${executeResult} Execute without auth - ${executeUnauth.status} (${executeUnauth.responseTime}ms)`);
        
        // Test billing endpoint without auth
        const billingUnauth = await this.makeRequest(`${this.backendUrl}/api/v1/billing/usage`);
        const billingExpected = billingUnauth.status === 401; // Should require auth
        const billingResult = billingExpected ? '✅' : '❌';
        console.log(`  ${billingResult} Billing without auth - ${billingUnauth.status} (${billingUnauth.responseTime}ms)`);
        
        // Test frontend dashboard (should redirect or show auth)
        const dashboard = await this.makeRequest(`${this.frontendUrl}/dashboard`);
        const dashboardExpected = [200, 302, 401].includes(dashboard.status); // Various auth responses
        const dashboardResult = dashboardExpected ? '✅' : '❌';
        console.log(`  ${dashboardResult} Frontend dashboard - ${dashboard.status} (${dashboard.responseTime}ms)`);
        
        const overallTaskSuccess = executeExpected && billingExpected && dashboardExpected;
        
        this.results.push({
            test: 'Task Execution Flow',
            success: overallTaskSuccess,
            components: {
                executeUnauth: { success: executeExpected, ...executeUnauth },
                billingUnauth: { success: billingExpected, ...billingUnauth },
                dashboard: { success: dashboardExpected, ...dashboard }
            }
        });
        
        return overallTaskSuccess;
    }

    async testAPIDiscovery() {
        console.log('🔍 Testing API Discovery...');
        
        // Test providers endpoint
        const providers = await this.makeRequest(`${this.backendUrl}/api/v1/providers`);
        const providersResult = providers.success ? '✅' : '❌';
        console.log(`  ${providersResult} Providers endpoint - ${providers.status} (${providers.responseTime}ms)`);
        
        // Test models endpoint
        const models = await this.makeRequest(`${this.backendUrl}/api/v1/models`);
        const modelsResult = models.success ? '✅' : '❌';
        console.log(`  ${modelsResult} Models endpoint - ${models.status} (${models.responseTime}ms)`);
        
        // Test metrics endpoint
        const metrics = await this.makeRequest(`${this.backendUrl}/metrics`);
        const metricsResult = metrics.success ? '✅' : '❌';
        console.log(`  ${metricsResult} Metrics endpoint - ${metrics.status} (${metrics.responseTime}ms)`);
        
        // Test frontend API documentation accessibility
        const apiDocs = await this.makeRequest(`${this.frontendUrl}/docs`);
        const docsResult = apiDocs.success ? '✅' : '❌';
        console.log(`  ${docsResult} Frontend docs - ${apiDocs.status} (${apiDocs.responseTime}ms)`);
        
        const overallDiscoverySuccess = providers.success && models.success && metrics.success && apiDocs.success;
        
        this.results.push({
            test: 'API Discovery',
            success: overallDiscoverySuccess,
            components: {
                providers: { success: providers.success, ...providers },
                models: { success: models.success, ...models },
                metrics: { success: metrics.success, ...metrics },
                docs: { success: apiDocs.success, ...apiDocs }
            }
        });
        
        return overallDiscoverySuccess;
    }

    async testCrossServiceIntegration() {
        console.log('🔗 Testing Cross-Service Integration...');
        
        // Test if frontend can reach backend (via CORS/proxy)
        const corsTest = await this.makeRequest(`${this.frontendUrl}/api/health`);
        const corsResult = corsTest.success ? '✅' : '❌';
        console.log(`  ${corsResult} Frontend health proxy - ${corsTest.status} (${corsTest.responseTime}ms)`);
        
        // Test cache stats (should work without auth)
        const cacheStats = await this.makeRequest(`${this.backendUrl}/api/v1/cache/stats`);
        const cacheResult = cacheStats.success ? '✅' : '❌';
        console.log(`  ${cacheResult} Cache stats - ${cacheStats.status} (${cacheStats.responseTime}ms)`);
        
        // Test production validation
        const prodValidation = await this.makeRequest(`${this.backendUrl}/api/v1/production/validate`);
        const prodResult = [200, 503].includes(prodValidation.status) ? '✅' : '❌'; // Either ready or not ready
        console.log(`  ${prodResult} Production validation - ${prodValidation.status} (${prodValidation.responseTime}ms)`);
        
        const overallIntegrationSuccess = corsTest.success && cacheStats.success && [200, 503].includes(prodValidation.status);
        
        this.results.push({
            test: 'Cross-Service Integration',
            success: overallIntegrationSuccess,
            components: {
                cors: { success: corsTest.success, ...corsTest },
                cache: { success: cacheStats.success, ...cacheStats },
                production: { success: [200, 503].includes(prodValidation.status), ...prodValidation }
            }
        });
        
        return overallIntegrationSuccess;
    }

    async runAllTests() {
        console.log('🚀 Starting User Flow Integration Tests');
        console.log('=' .repeat(50));
        
        const healthSync = await this.testBackendFrontendHealthSync();
        const authFlow = await this.testAuthenticationFlow();
        const taskFlow = await this.testTaskExecutionFlow();
        const apiDiscovery = await this.testAPIDiscovery();
        const crossService = await this.testCrossServiceIntegration();
        
        // Summary
        const allTests = [healthSync, authFlow, taskFlow, apiDiscovery, crossService];
        const successfulTests = allTests.filter(Boolean).length;
        const totalTests = allTests.length;
        const failedTests = totalTests - successfulTests;
        
        console.log('\n' + '='.repeat(50));
        console.log('📋 Integration Test Summary');
        console.log(`  Total Tests: ${totalTests}`);
        console.log(`  ✅ Successful: ${successfulTests}`);
        console.log(`  ❌ Failed: ${failedTests}`);
        
        if (failedTests > 0) {
            console.log('\n❌ Failed Tests:');
            this.results.filter(r => !r.success).forEach(result => {
                console.log(`  - ${result.test}: Check individual components`);
            });
        }
        
        return successfulTests === totalTests;
    }
}

async function main() {
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const frontendUrl = process.env.FRONTEND_URL || 'http://localhost:3000';
    
    const tester = new UserFlowIntegrationTest(backendUrl, frontendUrl);
    const success = await tester.runAllTests();
    
    if (!success) {
        process.exit(1);
    }
}

// Run if this is the main module
if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch(console.error);
}

export { UserFlowIntegrationTest };