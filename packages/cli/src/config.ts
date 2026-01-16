/**
 * Configuration Manager for Monkey Coder CLI
 * Handles loading and saving user preferences and API settings with secure token storage
 */

import * as path from 'path';
import * as os from 'os';
import * as crypto from 'crypto';

import fs from 'fs-extra';

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
  private workingDir: string;

  constructor(workingDir?: string) {
    // Working directory for finding local/project configs
    this.workingDir = workingDir || process.cwd();

    // Use XDG config directory or fallback to ~/.config
    const xdgConfigHome = process.env.XDG_CONFIG_HOME;
    this.configDir = xdgConfigHome
      ? path.join(xdgConfigHome, 'monkey-coder')
      : path.join(os.homedir(), '.config', 'monkey-coder');

    this.configPath = path.join(this.configDir, 'config.json');
    this.config = {};

    // Initialize encryption key from machine-specific data
    this.initializeEncryption();

    // Load config with hierarchy (global -> local -> project)
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
   * Find local config file by traversing up directory tree
   * Looks for .monkey-coder/config.json
   */
  private findLocalConfigPath(): string | null {
    let currentDir = this.workingDir;
    const root = path.parse(currentDir).root;

    while (currentDir !== root) {
      const localConfigPath = path.join(currentDir, '.monkey-coder', 'config.json');
      if (fs.pathExistsSync(localConfigPath)) {
        return localConfigPath;
      }
      const parentDir = path.dirname(currentDir);
      if (parentDir === currentDir) break; // Safety check
      currentDir = parentDir;
    }

    return null;
  }

  /**
   * Find project config file in current directory
   * Looks for monkey-coder.json or package.json with monkey-coder field
   */
  private findProjectConfigPath(): string | null {
    // First check for dedicated monkey-coder.json
    const monkeyCoderJson = path.join(this.workingDir, 'monkey-coder.json');
    if (fs.pathExistsSync(monkeyCoderJson)) {
      return monkeyCoderJson;
    }

    // Then check for package.json with monkey-coder field
    const packageJson = path.join(this.workingDir, 'package.json');
    if (fs.pathExistsSync(packageJson)) {
      try {
        const pkg = JSON.parse(fs.readFileSync(packageJson, 'utf-8'));
        if (pkg['monkey-coder']) {
          return packageJson;
        }
      } catch (error) {
        // Ignore invalid package.json
      }
    }

    return null;
  }

  /**
   * Load configuration from file synchronously
   */
  private loadConfigSync(): void {
    // Start with empty config
    this.config = {};

    // 1. Load global config (lowest priority)
    this.mergeConfigFromFile(this.configPath, true);

    // 2. Load local config (medium priority)
    const localConfigPath = this.findLocalConfigPath();
    if (localConfigPath) {
      this.mergeConfigFromFile(localConfigPath, true);
    }

    // 3. Load project config (highest priority)
    const projectConfigPath = this.findProjectConfigPath();
    if (projectConfigPath) {
      if (projectConfigPath.endsWith('package.json')) {
        // Extract monkey-coder field from package.json
        try {
          const pkg = JSON.parse(fs.readFileSync(projectConfigPath, 'utf-8'));
          if (pkg['monkey-coder']) {
            Object.assign(this.config, pkg['monkey-coder']);
          }
        } catch (error) {
          // Ignore errors
        }
      } else {
        // Load dedicated config file
        this.mergeConfigFromFile(projectConfigPath, false);
      }
    }

    // 4. Environment variables override everything
    this.mergeFromEnvironment();
  }

  /**
   * Merge config from a file into current config
   */
  private mergeConfigFromFile(filePath: string, encrypted: boolean): void {
    try {
      if (fs.pathExistsSync(filePath)) {
        const configData = fs.readFileSync(filePath, 'utf-8');
        const rawConfig = JSON.parse(configData);
        
        if (encrypted) {
          const decryptedConfig = this.decryptConfig(rawConfig);
          Object.assign(this.config, decryptedConfig);
          // Ensure encryption metadata is not exposed
          delete (this.config as any)._encrypted;
          delete (this.config as any)._salt;
        } else {
          // Project configs are not encrypted
          Object.assign(this.config, rawConfig);
        }
      }
    } catch (error) {
      // Silently ignore errors for non-critical configs
    }
  }

  /**
   * Merge config from environment variables
   */
  private mergeFromEnvironment(): void {
    // Environment variables take highest priority
    if (process.env.MONKEY_CODER_API_KEY) {
      this.config.apiKey = process.env.MONKEY_CODER_API_KEY;
    }
    if (process.env.MONKEY_CODER_BASE_URL) {
      this.config.baseUrl = process.env.MONKEY_CODER_BASE_URL;
    }
    if (process.env.MONKEY_CODER_DEFAULT_MODEL) {
      this.config.defaultModel = process.env.MONKEY_CODER_DEFAULT_MODEL;
    }
    if (process.env.MONKEY_CODER_DEFAULT_PROVIDER) {
      this.config.defaultProvider = process.env.MONKEY_CODER_DEFAULT_PROVIDER;
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
    const config = { ...this.config };
    // Ensure encryption metadata is never exposed
    delete (config as any)._encrypted;
    delete (config as any)._salt;
    return config;
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

  /**
   * Get all config locations in priority order (lowest to highest)
   * Returns paths of config files that exist and would be loaded
   */
  getConfigLocations(): string[] {
    const locations: string[] = [];

    // Global config
    if (fs.pathExistsSync(this.configPath)) {
      locations.push(this.configPath);
    }

    // Local config
    const localConfigPath = this.findLocalConfigPath();
    if (localConfigPath) {
      locations.push(localConfigPath);
    }

    // Project config
    const projectConfigPath = this.findProjectConfigPath();
    if (projectConfigPath) {
      locations.push(projectConfigPath);
    }

    return locations;
  }

  /**
   * Get effective config showing which file each value came from
   */
  getEffectiveConfig(): { [key: string]: { value: any; source: string } } {
    const result: { [key: string]: { value: any; source: string } } = {};
    const configs: { source: string; data: Partial<ConfigFile> }[] = [];

    // Load all configs
    if (fs.pathExistsSync(this.configPath)) {
      try {
        const configData = fs.readFileSync(this.configPath, 'utf-8');
        const rawConfig = JSON.parse(configData);
        const decrypted = this.decryptConfig(rawConfig);
        configs.push({ source: `global (${this.configPath})`, data: decrypted });
      } catch (error) {
        // Ignore
      }
    }

    const localConfigPath = this.findLocalConfigPath();
    if (localConfigPath) {
      try {
        const configData = fs.readFileSync(localConfigPath, 'utf-8');
        const rawConfig = JSON.parse(configData);
        const decrypted = this.decryptConfig(rawConfig);
        configs.push({ source: `local (${localConfigPath})`, data: decrypted });
      } catch (error) {
        // Ignore
      }
    }

    const projectConfigPath = this.findProjectConfigPath();
    if (projectConfigPath) {
      try {
        let projectConfig: Partial<ConfigFile>;
        if (projectConfigPath.endsWith('package.json')) {
          const pkg = JSON.parse(fs.readFileSync(projectConfigPath, 'utf-8'));
          projectConfig = pkg['monkey-coder'] || {};
        } else {
          const configData = fs.readFileSync(projectConfigPath, 'utf-8');
          projectConfig = JSON.parse(configData);
        }
        configs.push({ source: `project (${projectConfigPath})`, data: projectConfig });
      } catch (error) {
        // Ignore
      }
    }

    // Build result showing which file each value came from
    for (const { source, data } of configs) {
      for (const [key, value] of Object.entries(data)) {
        if (value !== undefined && value !== null) {
          result[key] = { value, source };
        }
      }
    }

    // Environment variables
    if (process.env.MONKEY_CODER_API_KEY) {
      result.apiKey = { value: process.env.MONKEY_CODER_API_KEY, source: 'environment (MONKEY_CODER_API_KEY)' };
    }
    if (process.env.MONKEY_CODER_BASE_URL) {
      result.baseUrl = { value: process.env.MONKEY_CODER_BASE_URL, source: 'environment (MONKEY_CODER_BASE_URL)' };
    }
    if (process.env.MONKEY_CODER_DEFAULT_MODEL) {
      result.defaultModel = { value: process.env.MONKEY_CODER_DEFAULT_MODEL, source: 'environment (MONKEY_CODER_DEFAULT_MODEL)' };
    }
    if (process.env.MONKEY_CODER_DEFAULT_PROVIDER) {
      result.defaultProvider = { value: process.env.MONKEY_CODER_DEFAULT_PROVIDER, source: 'environment (MONKEY_CODER_DEFAULT_PROVIDER)' };
    }

    return result;
  }
}
