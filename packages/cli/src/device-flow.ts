/**
 * OAuth Device Flow Authentication for Monkey Coder CLI
 * 
 * Implements RFC 8628 Device Authorization Grant for secure CLI authentication.
 * No localhost required - works in SSH sessions, containers, and remote servers.
 */

import chalk from 'chalk';
import ora, { Ora } from 'ora';
import open from 'open';

interface DeviceAuthResponse {
  device_code: string;
  user_code: string;
  verification_uri: string;
  verification_uri_complete: string;
  expires_in: number;
  interval: number;
}

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  scope: string;
}

interface DeviceFlowOptions {
  apiBaseUrl: string;
  clientId?: string;
  autoOpenBrowser?: boolean;
  onCodeReceived?: (userCode: string, verificationUri: string) => void;
}

export class DeviceFlowAuth {
  private apiBaseUrl: string;
  private clientId: string;
  private autoOpenBrowser: boolean;

  constructor(options: DeviceFlowOptions) {
    this.apiBaseUrl = options.apiBaseUrl;
    this.clientId = options.clientId || 'monkey-coder-cli';
    this.autoOpenBrowser = options.autoOpenBrowser !== false;
  }

  /**
   * Perform device flow authentication
   */
  async authenticate(): Promise<TokenResponse> {
    // Step 1: Request device code
    const spinner = ora('Requesting authorization...').start();
    
    let deviceAuth: DeviceAuthResponse;
    try {
      deviceAuth = await this.requestDeviceCode();
      spinner.stop();
    } catch (error) {
      spinner.fail('Failed to request authorization');
      throw error;
    }

    // Step 2: Display user code and open browser
    this.displayUserInstructions(deviceAuth);

    if (this.autoOpenBrowser) {
      try {
        await open(deviceAuth.verification_uri_complete);
        console.log(chalk.gray('\n✓ Opened browser automatically\n'));
      } catch (error) {
        console.log(chalk.yellow('\n⚠  Could not open browser automatically\n'));
      }
    }

    // Step 3: Poll for token
    const pollSpinner = ora('Waiting for authorization...').start();
    
    try {
      const tokens = await this.pollForToken(
        deviceAuth.device_code,
        deviceAuth.interval,
        deviceAuth.expires_in
      );
      
      pollSpinner.succeed('Authorization successful!');
      return tokens;
    } catch (error) {
      pollSpinner.fail('Authorization failed');
      throw error;
    }
  }

  /**
   * Step 1: Request device and user codes from the server
   */
  private async requestDeviceCode(): Promise<DeviceAuthResponse> {
    const response = await fetch(`${this.apiBaseUrl}/device/authorize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        client_id: this.clientId,
        scope: 'read write',
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Step 2: Display instructions to the user
   */
  private displayUserInstructions(deviceAuth: DeviceAuthResponse): void {
    console.log('\n' + chalk.bold('🔐 Authentication Required\n'));
    console.log(chalk.gray('To authenticate this device, please:'));
    console.log(chalk.cyan(`\n  1. Visit: ${deviceAuth.verification_uri}`));
    console.log(chalk.yellow(`  2. Enter code: ${chalk.bold(deviceAuth.user_code)}`));
    console.log(chalk.gray(`\n  Code expires in ${Math.floor(deviceAuth.expires_in / 60)} minutes\n`));
  }

  /**
   * Step 3: Poll the token endpoint until authorization completes
   */
  private async pollForToken(
    deviceCode: string,
    interval: number,
    expiresIn: number
  ): Promise<TokenResponse> {
    const startTime = Date.now();
    const timeout = expiresIn * 1000; // Convert to milliseconds
    let pollInterval = interval * 1000; // Convert to milliseconds

    while (Date.now() - startTime < timeout) {
      // Wait for the polling interval
      await this.sleep(pollInterval);

      try {
        const response = await fetch(`${this.apiBaseUrl}/device/token`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            device_code: deviceCode,
            grant_type: 'urn:ietf:params:oauth:grant-type:device_code',
          }),
        });

        if (response.ok) {
          // Success! Return the tokens
          return await response.json();
        }

        const error = await response.json().catch(() => ({}));

        // Handle different error types
        if (error.detail === 'authorization_pending') {
          // Still waiting - continue polling
          continue;
        } else if (error.detail === 'slow_down') {
          // Server is rate limiting - increase interval
          pollInterval += 1000; // Add 1 second
          continue;
        } else if (error.detail === 'access_denied') {
          throw new Error('Authorization was denied by the user');
        } else if (error.detail === 'expired_token') {
          throw new Error('Authorization code has expired. Please try again.');
        } else {
          throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        // Network error or other exception
        if (error instanceof Error && error.message.includes('Authorization')) {
          throw error; // Rethrow authorization errors
        }
        // For network errors, continue polling
        continue;
      }
    }

    // Timeout reached
    throw new Error('Authorization timed out. Please try again.');
  }

  /**
   * Helper to sleep for a given duration
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * Convenience function to perform device flow authentication
 */
export async function deviceFlowLogin(apiBaseUrl: string): Promise<TokenResponse> {
  const deviceFlow = new DeviceFlowAuth({ apiBaseUrl });
  return await deviceFlow.authenticate();
}
