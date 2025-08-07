/**
 * Configuration Manager for Monkey Coder CLI
 * Handles loading and saving user preferences and API settings with secure token storage
 */

import fs from 'fs-extra';
import * as path from 'path';
import * as os from 'os';
import * as crypto from 'crypto';
import { ConfigFile } from './types.js';

// Sensitive fields that should be encrypted
const SENSITIVE_FIELDS = ['apiKey', 'refreshToken'] as const;
type SensitiveField = typeof SENSITIVE_FIELDS[number];

interface SecureConfigFile extends Omit<ConfigFile, SensitiveField> {
  // Encrypted sensitive data
  _encrypted?: {
    [K in SensitiveField]?: string;
  };
  _salt?: string;
}

export class ConfigManager {
  private configDir: string;
  private configPath: string;
  private config: ConfigFile;
  private encryptionKey?: Buffer;

  constructor() {
    // Use XDG config directory or fallback to ~/.config
    const xdgConfigHome = process.env.XDG_CONFIG_HOME;
    this.configDir = xdgConfigHome
      ? path.join(xdgConfigHome, 'monkey-coder')
      : path.join(os.homedir(), '.config', 'monkey-coder');

    this.configPath = path.join(this.configDir, 'config.json');
    this.config = {};

    // Initialize encryption key from machine-specific data
    this.initializeEncryption();

    // Load config synchronously to ensure it's available immediately
    this.loadConfigSync();
  }

  /**
   * Initialize encryption key based on machine-specific data
   */
  private initializeEncryption(): void {
    // Create a machine-specific key using hostname and user info
    // This is not perfect security but much better than plaintext
    const machineId = os.hostname() + os.userInfo().username + this.configDir;
    this.encryptionKey = crypto.scryptSync(machineId, 'monkey-coder-salt', 32);
  }

  /**
   * Encrypt sensitive data
   */
  private encrypt(text: string, salt: string): string {
    if (!this.encryptionKey) {
      throw new Error('Encryption not initialized');
    }

    const algorithm = 'aes-256-gcm';
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv(algorithm, this.encryptionKey, iv);

    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');

    // Get the auth tag for GCM mode
    const authTag = cipher.getAuthTag();

    // Include IV and auth tag in the encrypted string for decryption
    return iv.toString('hex') + ':' + authTag.toString('hex') + ':' + encrypted;
  }

  /**
   * Decrypt sensitive data
   */
  private decrypt(encryptedText: string): string {
    if (!this.encryptionKey) {
      throw new Error('Encryption not initialized');
    }

    try {
      const algorithm = 'aes-256-gcm';
      const parts = encryptedText.split(':');
      if (parts.length !== 3) {
        throw new Error('Invalid encrypted data format');
      }

      const ivHex = parts[0]!;
      const authTagHex = parts[1]!;
      const encrypted = parts[2]!;

      const iv = Buffer.from(ivHex, 'hex');
      const authTag = Buffer.from(authTagHex, 'hex');
      const decipher = crypto.createDecipheriv(algorithm, this.encryptionKey, iv);

      decipher.setAuthTag(authTag);

      const decryptedBuffer = decipher.update(encrypted, 'hex');
      const finalBuffer = decipher.final();

      return Buffer.concat([decryptedBuffer, finalBuffer]).toString('utf8');
    } catch (error) {
      // If decryption fails, return empty string (corrupted data)
      console.warn('Warning: Failed to decrypt stored token, may be corrupted');
      return '';
    }
  }

  /**
   * Load configuration from file
   */
  private async loadConfig(): Promise<void> {
    try {
      if (await fs.pathExists(this.configPath)) {
        const configData = await fs.readFile(this.configPath, 'utf-8');
        const rawConfig: SecureConfigFile = JSON.parse(configData);
        this.config = this.decryptConfig(rawConfig);
      }
    } catch (error) {
      console.warn('Warning: Failed to load config file, using defaults');
      this.config = {};
    }
  }

  /**
   * Load configuration from file synchronously
   */
  private loadConfigSync(): void {
    try {
      if (fs.pathExistsSync(this.configPath)) {
        const configData = fs.readFileSync(this.configPath, 'utf-8');
        const rawConfig: SecureConfigFile = JSON.parse(configData);
        this.config = this.decryptConfig(rawConfig);
      }
    } catch (error) {
      // Silently use defaults for sync loading
      this.config = {};
    }
  }

  /**
   * Decrypt sensitive fields from stored config
   */
  private decryptConfig(secureConfig: SecureConfigFile): ConfigFile {
    const config: ConfigFile = { ...secureConfig } as ConfigFile;

    // Decrypt sensitive fields if they exist
    if (secureConfig._encrypted && secureConfig._salt) {
      for (const field of SENSITIVE_FIELDS) {
        const encryptedValue = secureConfig._encrypted[field];
        if (encryptedValue) {
          try {
            config[field] = this.decrypt(encryptedValue);
          } catch (error) {
            console.warn(`Warning: Failed to decrypt ${field}, using empty value`);
            config[field] = '';
          }
        }
      }
    }

    // Remove encryption metadata from the returned config
    delete (config as any)._encrypted;
    delete (config as any)._salt;

    return config;
  }

  /**
   * Encrypt sensitive fields for storage
   */
  private encryptConfig(config: ConfigFile): SecureConfigFile {
    const secureConfig: SecureConfigFile = { ...config };
    const salt = crypto.randomBytes(16).toString('hex');

    // Remove and encrypt sensitive fields
    const encrypted: { [K in SensitiveField]?: string } = {};
    let hasSensitiveData = false;

    for (const field of SENSITIVE_FIELDS) {
      if (config[field] && config[field].trim() !== '') {
        encrypted[field] = this.encrypt(config[field], salt);
        delete (secureConfig as any)[field];
        hasSensitiveData = true;
      }
    }

    // Only add encryption metadata if we actually encrypted something
    if (hasSensitiveData) {
      secureConfig._encrypted = encrypted;
      secureConfig._salt = salt;
    }

    return secureConfig;
  }

  /**
   * Save configuration to file with encryption for sensitive data
   */
  async saveConfig(): Promise<void> {
    try {
      await fs.ensureDir(this.configDir);

      // Encrypt sensitive fields before saving
      const secureConfig = this.encryptConfig(this.config);
      const configJson = JSON.stringify(secureConfig, null, 2);

      // Write config file
      await fs.writeFile(this.configPath, configJson, 'utf-8');

      // Set restrictive permissions (readable only by owner)
      try {
        await fs.chmod(this.configPath, 0o600);
      } catch (chmodError) {
        // chmod might fail on some systems (e.g., Windows), but that's okay
        console.warn('Warning: Could not set restrictive file permissions on config file');
      }

      // Also set permissions on config directory
      try {
        await fs.chmod(this.configDir, 0o700);
      } catch (chmodError) {
        // chmod might fail on some systems, but that's okay
      }
    } catch (error) {
      throw new Error(`Failed to save config: ${error}`);
    }
  }

  /**
   * Get configuration value
   */
  get<K extends keyof ConfigFile>(key: K): ConfigFile[K] {
    return this.config[key];
  }

  /**
   * Set configuration value
   */
  set<K extends keyof ConfigFile>(key: K, value: ConfigFile[K]): void {
    this.config[key] = value;
  }

  /**
   * Get API key from config or environment
   */
  getApiKey(): string | undefined {
    return process.env.MONKEY_CODER_API_KEY || this.config.apiKey;
  }

  /**
   * Get base URL from config or environment
   */
  getBaseUrl(): string {
    return process.env.MONKEY_CODER_BASE_URL || this.config.baseUrl || 'http://localhost:8000';
  }

  /**
   * Get default persona
   */
  getDefaultPersona(): string {
    return this.config.defaultPersona || 'developer';
  }

  /**
   * Get default model
   */
  getDefaultModel(): string {
    return this.config.defaultModel || 'gpt-4.1';
  }

  /**
   * Get default provider
   */
  getDefaultProvider(): string {
    return this.config.defaultProvider || 'openai';
  }

  /**
   * Get default temperature
   */
  getDefaultTemperature(): number {
    return this.config.defaultTemperature || 0.1;
  }

  /**
   * Get default timeout
   */
  getDefaultTimeout(): number {
    return this.config.defaultTimeout || 300;
  }

  /**
   * Get show splash screen setting
   */
  getShowSplash(): boolean {
    return this.config.showSplash === false ? false : true;
  }

  /**
   * Get all configuration
   */
  getAll(): ConfigFile {
    return { ...this.config };
  }

  /**
   * Update multiple config values
   */
  async update(updates: Partial<ConfigFile>): Promise<void> {
    Object.assign(this.config, updates);
    await this.saveConfig();
  }

  /**
   * Reset configuration to defaults
   */
  async reset(): Promise<void> {
    this.config = {};
    await this.saveConfig();
  }

  /**
   * Check if config file exists
   */
  async exists(): Promise<boolean> {
    return fs.pathExists(this.configPath);
  }

  /**
   * Get config file path
   */
  getConfigPath(): string {
    return this.configPath;
  }
}
