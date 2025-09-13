#!/usr/bin/env node
/**
 * Frontend Route Smoke Tests for Monkey Coder Web App
 * 
 * Tests all Next.js routes to ensure they're accessible and return expected responses.
 * This focuses on route availability without requiring authentication or deep UI testing.
 */

import fetch from 'node-fetch';
import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

class FrontendSmokeTest {
    constructor(baseUrl = 'http://localhost:3000') {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.results = [];
    }

    async testRoute(route, expectedStatus = 200) {
        const url = `${this.baseUrl}${route}`;
        const startTime = Date.now();
        
        try {
            const response = await fetch(url, {
                method: 'GET',
                timeout: 30000,
                redirect: 'manual' // Don't follow redirects automatically
            });
            
            const responseTime = Date.now() - startTime;
            const success = response.status === expectedStatus;
            
            const result = {
                route,
                status: response.status,
                responseTime,
                success,
                error: success ? null : `Expected ${expectedStatus}, got ${response.status}`
            };
            
            this.results.push(result);
            return result;
            
        } catch (error) {
            const responseTime = Date.now() - startTime;
            const result = {
                route,
                status: 0,
                responseTime,
                success: false,
                error: error.message
            };
            
            this.results.push(result);
            return result;
        }
    }

    async testHealthEndpoint() {
        console.log('🔍 Testing Health Endpoint...');
        
        const result = await this.testRoute('/api/health');
        const status = result.success ? '✅' : '❌';
        console.log(`  ${status} /api/health - ${result.status} (${result.responseTime}ms)`);
        
        return result;
    }

    async testPublicRoutes() {
        console.log('🏠 Testing Public Routes...');
        
        const publicRoutes = [
            '/',
            '/pricing',
            '/contact',
            '/terms',
            '/privacy',
            '/blog',
            '/docs',
            '/getting-started'
        ];
        
        for (const route of publicRoutes) {
            const result = await this.testRoute(route);
            const status = result.success ? '✅' : '❌';
            console.log(`  ${status} ${route} - ${result.status} (${result.responseTime}ms)`);
        }
    }

    async testAuthRoutes() {
        console.log('🔐 Testing Auth Routes...');
        
        const authRoutes = [
            '/login',
            '/signup',
            '/forgot-password'
        ];
        
        for (const route of authRoutes) {
            const result = await this.testRoute(route);
            const status = result.success ? '✅' : '❌';
            console.log(`  ${status} ${route} - ${result.status} (${result.responseTime}ms)`);
        }
    }

    async testProtectedRoutes() {
        console.log('🛡️ Testing Protected Routes...');
        
        // These routes might redirect to login (302) or show a login page (200)
        // We accept both as valid responses for unauthenticated users
        const protectedRoutes = [
            { route: '/dashboard', expectedStatuses: [200, 302] },
            { route: '/projects', expectedStatuses: [200, 302] },
            { route: '/api-keys', expectedStatuses: [200, 302] }
        ];
        
        for (const { route, expectedStatuses } of protectedRoutes) {
            const result = await this.testRoute(route);
            const success = expectedStatuses.includes(result.status);
            const status = success ? '✅' : '❌';
            console.log(`  ${status} ${route} - ${result.status} (${result.responseTime}ms)`);
            
            // Update the result to reflect if it matches any expected status
            result.success = success;
            if (!success) {
                result.error = `Expected one of ${expectedStatuses}, got ${result.status}`;
            }
        }
    }

    async testErrorPages() {
        console.log('❌ Testing Error Pages...');
        
        // Test 404 page
        const result = await this.testRoute('/nonexistent-page-12345', 404);
        const status = result.success ? '✅' : '❌';
        console.log(`  ${status} /nonexistent-page-12345 - ${result.status} (${result.responseTime}ms)`);
    }

    async testStaticAssets() {
        console.log('📁 Testing Static Assets...');
        
        // Test common static assets that should exist
        const staticAssets = [
            '/favicon.ico',
            '/robots.txt'
        ];
        
        for (const asset of staticAssets) {
            const result = await this.testRoute(asset);
            const status = result.success ? '✅' : '❌';
            console.log(`  ${status} ${asset} - ${result.status} (${result.responseTime}ms)`);
        }
    }

    async runAllTests() {
        console.log('🚀 Starting Frontend Route Smoke Tests');
        console.log('=' .repeat(50));
        
        await this.testHealthEndpoint();
        await this.testPublicRoutes();
        await this.testAuthRoutes();
        await this.testProtectedRoutes();
        await this.testErrorPages();
        await this.testStaticAssets();
        
        // Summary
        const totalTests = this.results.length;
        const successfulTests = this.results.filter(r => r.success).length;
        const failedTests = totalTests - successfulTests;
        const avgResponseTime = this.results.reduce((sum, r) => sum + r.responseTime, 0) / totalTests;
        
        console.log('\n' + '='.repeat(50));
        console.log('📋 Test Summary');
        console.log(`  Total Tests: ${totalTests}`);
        console.log(`  ✅ Successful: ${successfulTests}`);
        console.log(`  ❌ Failed: ${failedTests}`);
        console.log(`  ⏱️ Average Response Time: ${avgResponseTime.toFixed(0)}ms`);
        
        if (failedTests > 0) {
            console.log('\n❌ Failed Tests:');
            this.results.filter(r => !r.success).forEach(result => {
                console.log(`  - ${result.route}: ${result.error}`);
            });
        }
        
        return successfulTests === totalTests;
    }
}

async function main() {
    const baseUrl = process.env.FRONTEND_URL || 'http://localhost:3000';
    
    const tester = new FrontendSmokeTest(baseUrl);
    const success = await tester.runAllTests();
    
    if (!success) {
        process.exit(1);
    }
}

// Run if this is the main module
if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch(console.error);
}

export { FrontendSmokeTest };