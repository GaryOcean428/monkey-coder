#!/usr/bin/env node
/**
 * CLI Smoke Tests for Monkey Coder
 * 
 * Tests CLI commands and functionality to ensure they work as expected.
 * Focuses on command availability and basic functionality without requiring authentication.
 */

import { spawn, execSync } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

class CLISmokeTest {
    constructor() {
        this.results = [];
        this.cliPath = join(__dirname, '..', 'packages', 'cli');
    }

    async runCommand(command, args = [], options = {}) {
        return new Promise((resolve) => {
            const startTime = Date.now();
            const timeout = options.timeout || 15000;
            
            const child = spawn(command, args, {
                cwd: this.cliPath,
                stdio: 'pipe',
                timeout: timeout,
                ...options
            });
            
            let stdout = '';
            let stderr = '';
            
            child.stdout?.on('data', (data) => {
                stdout += data.toString();
            });
            
            child.stderr?.on('data', (data) => {
                stderr += data.toString();
            });
            
            const timeoutId = setTimeout(() => {
                child.kill('SIGTERM');
            }, timeout);
            
            child.on('close', (code) => {
                clearTimeout(timeoutId);
                const responseTime = Date.now() - startTime;
                
                resolve({
                    command: `${command} ${args.join(' ')}`.trim(),
                    code,
                    stdout,
                    stderr,
                    responseTime,
                    success: code === 0,
                    timedOut: false
                });
            });
            
            child.on('error', (error) => {
                clearTimeout(timeoutId);
                const responseTime = Date.now() - startTime;
                
                resolve({
                    command: `${command} ${args.join(' ')}`.trim(),
                    code: -1,
                    stdout: '',
                    stderr: error.message,
                    responseTime,
                    success: false,
                    timedOut: false,
                    error: error.message
                });
            });
        });
    }

    async testCLIAvailability() {
        console.log('🔍 Testing CLI Availability...');
        
        try {
            // Test if yarn and the CLI workspace are available
            const yarnVersion = execSync('yarn --version', { 
                cwd: join(__dirname, '..'),
                encoding: 'utf8',
                timeout: 5000
            }).trim();
            console.log(`  ✅ Yarn available: ${yarnVersion}`);
            
            // Test CLI help command
            const helpResult = await this.runCommand('yarn', ['monkey', '--help'], { timeout: 10000 });
            const status = helpResult.success || helpResult.stdout.includes('Usage:') ? '✅' : '❌';
            console.log(`  ${status} CLI help command - ${helpResult.code} (${helpResult.responseTime}ms)`);
            
            this.results.push({
                test: 'CLI Help',
                ...helpResult
            });
            
        } catch (error) {
            console.log(`  ❌ CLI availability check failed: ${error.message}`);
            this.results.push({
                test: 'CLI Availability',
                success: false,
                error: error.message,
                responseTime: 0
            });
        }
    }

    async testCLICommands() {
        console.log('⚡ Testing CLI Commands...');
        
        const commands = [
            {
                name: 'Version',
                args: ['monkey', '--version'],
                expectInOutput: ['version', 'monkey-coder']
            },
            {
                name: 'Auth Status', 
                args: ['monkey', 'auth', 'status'],
                expectInOutput: ['authentication', 'status', 'logged']
            },
            {
                name: 'Help',
                args: ['monkey', '--help'],
                expectInOutput: ['usage', 'commands', 'options']
            }
        ];
        
        for (const cmd of commands) {
            const result = await this.runCommand('yarn', cmd.args, { timeout: 15000 });
            
            // Check if output contains expected content (case insensitive)
            const outputCheck = cmd.expectInOutput.some(expected => 
                result.stdout.toLowerCase().includes(expected.toLowerCase()) ||
                result.stderr.toLowerCase().includes(expected.toLowerCase())
            );
            
            const success = result.success || outputCheck;
            const status = success ? '✅' : '❌';
            
            console.log(`  ${status} ${cmd.name} - ${result.code} (${result.responseTime}ms)`);
            
            this.results.push({
                test: cmd.name,
                ...result,
                success
            });
        }
    }

    async testCLIWithoutAuth() {
        console.log('🔓 Testing CLI Without Authentication...');
        
        const unauthenticatedCommands = [
            {
                name: 'Implement (should fail)',
                args: ['monkey', 'implement', 'hello world'],
                expectFailure: true
            },
            {
                name: 'Analyze (should fail)',
                args: ['monkey', 'analyze', 'test.py'],
                expectFailure: true
            }
        ];
        
        for (const cmd of unauthenticatedCommands) {
            const result = await this.runCommand('yarn', cmd.args, { timeout: 10000 });
            
            // For commands that should fail, we expect non-zero exit code
            const success = cmd.expectFailure ? !result.success : result.success;
            const status = success ? '✅' : '❌';
            
            console.log(`  ${status} ${cmd.name} - ${result.code} (${result.responseTime}ms)`);
            
            this.results.push({
                test: cmd.name,
                ...result,
                success
            });
        }
    }

    async testCLIConfiguration() {
        console.log('⚙️ Testing CLI Configuration...');
        
        const configCommands = [
            {
                name: 'Config List',
                args: ['monkey', 'config', '--help'],
                expectInOutput: ['config', 'configuration']
            }
        ];
        
        for (const cmd of configCommands) {
            const result = await this.runCommand('yarn', cmd.args, { timeout: 10000 });
            
            const outputCheck = cmd.expectInOutput.some(expected => 
                result.stdout.toLowerCase().includes(expected.toLowerCase()) ||
                result.stderr.toLowerCase().includes(expected.toLowerCase())
            );
            
            const success = result.success || outputCheck;
            const status = success ? '✅' : '❌';
            
            console.log(`  ${status} ${cmd.name} - ${result.code} (${result.responseTime}ms)`);
            
            this.results.push({
                test: cmd.name,
                ...result,
                success
            });
        }
    }

    async runAllTests() {
        console.log('🚀 Starting CLI Smoke Tests');
        console.log('=' .repeat(50));
        
        await this.testCLIAvailability();
        await this.testCLICommands();
        await this.testCLIWithoutAuth();
        await this.testCLIConfiguration();
        
        // Summary
        const totalTests = this.results.length;
        const successfulTests = this.results.filter(r => r.success).length;
        const failedTests = totalTests - successfulTests;
        const avgResponseTime = this.results.length > 0 
            ? this.results.reduce((sum, r) => sum + (r.responseTime || 0), 0) / totalTests 
            : 0;
        
        console.log('\n' + '='.repeat(50));
        console.log('📋 Test Summary');
        console.log(`  Total Tests: ${totalTests}`);
        console.log(`  ✅ Successful: ${successfulTests}`);
        console.log(`  ❌ Failed: ${failedTests}`);
        console.log(`  ⏱️ Average Response Time: ${avgResponseTime.toFixed(0)}ms`);
        
        if (failedTests > 0) {
            console.log('\n❌ Failed Tests:');
            this.results.filter(r => !r.success).forEach(result => {
                console.log(`  - ${result.test}: ${result.error || 'Command failed'}`);
                if (result.stderr) {
                    console.log(`    stderr: ${result.stderr.substring(0, 200)}...`);
                }
            });
        }
        
        return successfulTests === totalTests;
    }
}

async function main() {
    const tester = new CLISmokeTest();
    const success = await tester.runAllTests();
    
    if (!success) {
        process.exit(1);
    }
}

// Run if this is the main module
if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch(console.error);
}

export { CLISmokeTest };