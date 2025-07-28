/**
 * Authentication commands for Monkey Coder CLI
 * Handles login, logout, and session management
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import * as readline from 'readline';
import { MonkeyCoderAPIClient } from '../api-client.js';
import { ConfigManager } from '../config.js';
import { formatError } from '../utils.js';

interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: {
    id: string;
    email: string;
    name: string;
    credits: number;
    subscription_tier: string;
  };
}

interface UserStatus {
  authenticated: boolean;
  user?: {
    email: string;
    name: string;
    credits: number;
    subscription_tier: string;
  };
  session_expires?: string;
}

export function createAuthCommand(config: ConfigManager): Command {
  const auth = new Command('auth')
    .description('Authentication and session management');

  // Login command
  auth
    .command('login')
    .description('Login to Monkey Coder')
    .option('--email <email>', 'Email address')
    .option('--password <password>', 'Password (not recommended, use interactive mode)')
    .action(async (options) => {
      try {
        const client = new MonkeyCoderAPIClient(config.getBaseUrl());
        
        // Get credentials
        let email = options.email;
        let password = options.password;

        if (!email || !password) {
          const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout,
          });

          if (!email) {
            email = await new Promise<string>((resolve) => {
              rl.question(chalk.cyan('Email: '), resolve);
            });
          }

          if (!password) {
            // Hide password input
            process.stdout.write(chalk.cyan('Password: '));
            password = await new Promise<string>((resolve) => {
              const stdin = process.stdin;
              const stdout = process.stdout;

              stdin.setRawMode(true);
              stdin.resume();
              stdin.setEncoding('utf8');

              let password = '';
              stdin.on('data', (data) => {
                const char = data.toString();
                
                if (char === '\n' || char === '\r' || char === '\u0004') {
                  stdin.setRawMode(false);
                  stdin.pause();
                  stdout.write('\n');
                  resolve(password);
                } else if (char === '\u0003') {
                  // Ctrl+C
                  process.exit();
                } else if (char === '\u007F') {
                  // Backspace
                  if (password.length > 0) {
                    password = password.slice(0, -1);
                    stdout.write('\b \b');
                  }
                } else {
                  password += char;
                  stdout.write('*');
                }
              });
            });
          }

          rl.close();
        }

        const spinner = ora('Authenticating...').start();

        // Authenticate
        const response = await client.authenticate({ email, password });
        const authData = response as AuthResponse;

        // Store tokens and user info
        config.set('apiKey', authData.access_token);
        config.set('refreshToken', authData.refresh_token);
        config.set('userEmail', authData.user.email);
        config.set('userName', authData.user.name);
        config.set('userCredits', authData.user.credits.toString());
        config.set('subscriptionTier', authData.user.subscription_tier);
        await config.saveConfig();

        spinner.succeed('Login successful!');
        
        console.log(chalk.green('\n✓ Authenticated as:'), authData.user.email);
        console.log(chalk.blue('  Name:'), authData.user.name);
        console.log(chalk.blue('  Credits:'), chalk.yellow(`$${(authData.user.credits / 100).toFixed(2)}`));
        console.log(chalk.blue('  Tier:'), authData.user.subscription_tier);
        
        console.log(chalk.gray('\nYour session has been saved. You can now use all Monkey Coder features.'));
        
      } catch (error: any) {
        console.error(formatError(error.message || 'Login failed'));
        process.exit(1);
      }
    });

  // Logout command
  auth
    .command('logout')
    .description('Logout from Monkey Coder')
    .action(async () => {
      try {
        const apiKey = config.getApiKey();
        
        if (!apiKey) {
          console.log(chalk.yellow('You are not logged in.'));
          return;
        }

        const spinner = ora('Logging out...').start();

        // Call logout endpoint to invalidate token
        try {
          const client = new MonkeyCoderAPIClient(config.getBaseUrl(), apiKey);
          await client.logout();
        } catch (error) {
          // Continue with local logout even if server call fails
          console.warn(chalk.yellow('Warning: Could not invalidate server session'));
        }

        // Clear local credentials
        config.set('apiKey', '');
        config.set('refreshToken', '');
        config.set('userEmail', '');
        config.set('userName', '');
        config.set('userCredits', '');
        config.set('subscriptionTier', '');
        await config.saveConfig();

        spinner.succeed('Logged out successfully');
        
      } catch (error: any) {
        console.error(formatError(error.message || 'Logout failed'));
        process.exit(1);
      }
    });

  // Status command
  auth
    .command('status')
    .description('Check authentication status')
    .action(async () => {
      try {
        const apiKey = config.getApiKey();
        
        if (!apiKey) {
          console.log(chalk.yellow('❌ Not authenticated'));
          console.log(chalk.gray('\nRun "monkey auth login" to authenticate.'));
          return;
        }

        const spinner = ora('Checking status...').start();

        try {
          const client = new MonkeyCoderAPIClient(config.getBaseUrl(), apiKey);
          const status = await client.getUserStatus() as UserStatus;

          spinner.stop();

          if (status.authenticated && status.user) {
            console.log(chalk.green('✓ Authenticated'));
            console.log(chalk.blue('\nUser Information:'));
            console.log('  Email:', status.user.email);
            console.log('  Name:', status.user.name);
            console.log('  Credits:', chalk.yellow(`$${(status.user.credits / 100).toFixed(2)}`));
            console.log('  Tier:', status.user.subscription_tier);
            
            if (status.session_expires) {
              const expiresDate = new Date(status.session_expires);
              const now = new Date();
              const hoursLeft = Math.round((expiresDate.getTime() - now.getTime()) / (1000 * 60 * 60));
              console.log('  Session expires:', chalk.gray(`in ${hoursLeft} hours`));
            }
          } else {
            console.log(chalk.yellow('⚠️  Session expired or invalid'));
            console.log(chalk.gray('\nRun "monkey auth login" to re-authenticate.'));
            
            // Clear invalid credentials
            config.set('apiKey', '');
            await config.saveConfig();
          }
          
        } catch (error: any) {
          spinner.stop();
          
          // Check if it's an auth error
          if (error.message.includes('401') || error.message.includes('403')) {
            console.log(chalk.yellow('⚠️  Session expired or invalid'));
            console.log(chalk.gray('\nRun "monkey auth login" to re-authenticate.'));
            
            // Clear invalid credentials
            config.set('apiKey', '');
            await config.saveConfig();
          } else {
            throw error;
          }
        }
        
      } catch (error: any) {
        console.error(formatError(error.message || 'Status check failed'));
        process.exit(1);
      }
    });

  // Refresh command
  auth
    .command('refresh')
    .description('Refresh authentication token')
    .action(async () => {
      try {
        const refreshToken = config.get('refreshToken');
        
        if (!refreshToken) {
          console.log(chalk.yellow('No refresh token found. Please login again.'));
          return;
        }

        const spinner = ora('Refreshing token...').start();

        const client = new MonkeyCoderAPIClient(config.getBaseUrl());
        const response = await client.refreshToken(refreshToken as string);
        const authData = response as AuthResponse;

        // Update tokens
        config.set('apiKey', authData.access_token);
        if (authData.refresh_token) {
          config.set('refreshToken', authData.refresh_token);
        }
        await config.saveConfig();

        spinner.succeed('Token refreshed successfully');
        
      } catch (error: any) {
        console.error(formatError(error.message || 'Token refresh failed'));
        console.log(chalk.gray('\nPlease run "monkey auth login" to re-authenticate.'));
        process.exit(1);
      }
    });

  return auth;
}

/**
 * Middleware to check authentication before executing commands
 */
export async function requireAuth(config: ConfigManager): Promise<void> {
  const apiKey = config.getApiKey();
  
  if (!apiKey) {
    console.error(chalk.red('❌ Authentication required'));
    console.log(chalk.gray('\nPlease run "monkey auth login" to authenticate.'));
    process.exit(1);
  }

  // Optionally check if token is still valid
  try {
    const client = new MonkeyCoderAPIClient(config.getBaseUrl(), apiKey);
    const status = await client.getUserStatus() as UserStatus;
    
    if (!status.authenticated) {
      console.error(chalk.red('❌ Session expired'));
      console.log(chalk.gray('\nPlease run "monkey auth login" to re-authenticate.'));
      process.exit(1);
    }
  } catch (error: any) {
    if (error.message.includes('401') || error.message.includes('403')) {
      console.error(chalk.red('❌ Session expired or invalid'));
      console.log(chalk.gray('\nPlease run "monkey auth login" to re-authenticate.'));
      process.exit(1);
    }
    // For other errors, continue - the actual command will handle it
  }
}
