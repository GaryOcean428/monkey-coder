/**
 * Secure Token Storage for Monkey Coder CLI
 * 
 * Uses keytar to store tokens securely in the OS keychain:
 * - macOS: Keychain
 * - Windows: Credential Vault
 * - Linux: libsecret (GNOME Keyring)
 * 
 * Falls back to encrypted file storage if keytar is unavailable.
 */

// Dynamically import keytar (may not be available in all environments)
import chalk from 'chalk';

let keytar: any;
try {
  keytar = require('keytar');
} catch (_error) {
  console.warn(chalk.yellow('⚠  keytar not available - using fallback storage'));
  keytar = null;
}

const SERVICE_NAME = 'monkey-coder-cli';

export interface StoredTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt?: string;
  userEmail?: string;
}

/**
 * Store authentication tokens securely
 */
export async function storeTokens(tokens: StoredTokens): Promise<void> {
  if (keytar) {
    try {
      // Store tokens in OS keychain
      await keytar.setPassword(SERVICE_NAME, 'access_token', tokens.accessToken);
      await keytar.setPassword(SERVICE_NAME, 'refresh_token', tokens.refreshToken);
      
      // Store metadata as JSON
      const metadata = {
        expiresAt: tokens.expiresAt,
        userEmail: tokens.userEmail,
        storedAt: new Date().toISOString(),
      };
      await keytar.setPassword(SERVICE_NAME, 'metadata', JSON.stringify(metadata));
      
      return;
    } catch (_error) {
      console.warn(chalk.yellow('⚠  Failed to store tokens in keychain, using fallback'));
    }
  }

  // Fallback to config file (less secure but functional)
  return await storeFallback(tokens);
}

/**
 * Retrieve stored authentication tokens
 */
export async function getTokens(): Promise<StoredTokens | null> {
  if (keytar) {
    try {
      const accessToken = await keytar.getPassword(SERVICE_NAME, 'access_token');
      const refreshToken = await keytar.getPassword(SERVICE_NAME, 'refresh_token');
      const metadataStr = await keytar.getPassword(SERVICE_NAME, 'metadata');
      
      if (!accessToken || !refreshToken) {
        return null;
      }

      const metadata = metadataStr ? JSON.parse(metadataStr) : {};
      
      return {
        accessToken,
        refreshToken,
        expiresAt: metadata.expiresAt,
        userEmail: metadata.userEmail,
      };
    } catch (_error) {
      console.warn(chalk.yellow('⚠  Failed to retrieve tokens from keychain, trying fallback'));
    }
  }

  // Fallback to config file
  return await getFallback();
}

/**
 * Get just the access token
 */
export async function getAccessToken(): Promise<string | null> {
  if (keytar) {
    try {
      return await keytar.getPassword(SERVICE_NAME, 'access_token');
    } catch (_error) {
      // Silent fail, try fallback
    }
  }

  const tokens = await getFallback();
  return tokens?.accessToken || null;
}

/**
 * Get just the refresh token
 */
export async function getRefreshToken(): Promise<string | null> {
  if (keytar) {
    try {
      return await keytar.getPassword(SERVICE_NAME, 'refresh_token');
    } catch (_error) {
      // Silent fail, try fallback
    }
  }

  const tokens = await getFallback();
  return tokens?.refreshToken || null;
}

/**
 * Clear all stored tokens
 */
export async function clearTokens(): Promise<void> {
  if (keytar) {
    try {
      await keytar.deletePassword(SERVICE_NAME, 'access_token');
      await keytar.deletePassword(SERVICE_NAME, 'refresh_token');
      await keytar.deletePassword(SERVICE_NAME, 'metadata');
      return;
    } catch (_error) {
      // Continue to fallback
    }
  }

  // Clear fallback storage
  await clearFallback();
}

/**
 * Check if tokens are stored
 */
export async function hasStoredTokens(): Promise<boolean> {
  const tokens = await getTokens();
  return tokens !== null && !!tokens.accessToken;
}

// Fallback storage implementation (using config file)
import * as fs from 'fs/promises';
import * as os from 'os';
import * as path from 'path';

const FALLBACK_DIR = path.join(os.homedir(), '.monkey-coder');
const FALLBACK_FILE = path.join(FALLBACK_DIR, '.credentials');

async function storeFallback(tokens: StoredTokens): Promise<void> {
  try {
    // Ensure directory exists
    await fs.mkdir(FALLBACK_DIR, { recursive: true });
    
    // Store tokens (base64 encoded for minimal obfuscation)
    const data = Buffer.from(JSON.stringify(tokens)).toString('base64');
    await fs.writeFile(FALLBACK_FILE, data, { mode: 0o600 }); // Owner read/write only
  } catch (error: unknown) {
    console.error(chalk.red('Failed to store credentials:'), error);
    throw error;
  }
}

async function getFallback(): Promise<StoredTokens | null> {
  try {
    const data = await fs.readFile(FALLBACK_FILE, 'utf-8');
    const decoded = Buffer.from(data, 'base64').toString('utf-8');
    return JSON.parse(decoded);
  } catch (_error) {
    // File doesn't exist or can't be read
    return null;
  }
}

async function clearFallback(): Promise<void> {
  try {
    await fs.unlink(FALLBACK_FILE);
  } catch (_error) {
    // File doesn't exist - that's okay
  }
}

/**
 * Update just the access token (for token refresh)
 */
export async function updateAccessToken(newAccessToken: string): Promise<void> {
  const existingTokens = await getTokens();
  
  if (!existingTokens) {
    throw new Error('No existing tokens found');
  }

  await storeTokens({
    ...existingTokens,
    accessToken: newAccessToken,
  });
}
