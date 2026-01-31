/**
 * Hierarchical Configuration Manager for Monkey Coder CLI
 * Supports global, local, and project-level configuration with cascading
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
  _encrypted?: {
    [K in SensitiveField]?: string;
  };
  _salt?: string;
}

export type ConfigScope = 'global' | 'local' | 'project';

export class HierarchicalConfigManager {
  private globalConfigDir: string;
  private globalConfigPath: string;
  private localConfigPath: string;
  private projectConfigPath: string;
  private encryptionKey?: Buffer;
  
  private globalConfig: ConfigFile = {};
  private localConfig: ConfigFile = {};
  private projectConfig: ConfigFile = {};
  private mergedConfig: ConfigFile = {};

  constructor(cwd: string = process.cwd()) {
    // Global config: ~/.config/monkey-coder/config.json
    const xdgConfigHome = process.env.XDG_CONFIG_HOME;
    this.globalConfigDir = xdgConfigHome
      ? path.join(xdgConfigHome, 'monkey-coder')
      : path.join(os.homedir(), '.config', 'monkey-coder');
    this.globalConfigPath = path.join(this.globalConfigDir, 'config.json');

    // Local config: .monkey-coder/config.json (in current directory or parent)
    this.localConfigPath = this.findLocalConfig(cwd);

    // Project config: monkey-coder.json or package.json field
    this.projectConfigPath = this.findProjectConfig(cwd);

    // Initialize encryption
    this.initializeEncryption();

    // Load all configs and merge
    this.loadAllConfigsSync();
  }

  /**
   * Find local config by walking up directory tree
   */
  private findLocalConfig(startDir: string): string {
    let currentDir = startDir;
    const root = path.parse(currentDir).root;

    while (currentDir !== root) {
      const localConfigPath = path.join(currentDir, '.monkey-coder', 'config.json');
      if (fs.existsSync(localConfigPath)) {
        return localConfigPath;
      }
      currentDir = path.dirname(currentDir);
    }

    // Default to .monkey-coder/config.json in current directory
    return path.join(startDir, '.monkey-coder', 'config.json');
  }

  /**
   * Find project config (monkey-coder.json or package.json field)
   */
  private findProjectConfig(startDir: string): string {
    // Check for monkey-coder.json
    const monkeyCoderJson = path.join(startDir, 'monkey-coder.json');
    if (fs.existsSync(monkeyCoderJson)) {
      return monkeyCoderJson;
    }

    // Check for package.json with monkey-coder field
    const packageJson = path.join(startDir, 'package.json');
    if (fs.existsSync(packageJson)) {
      try {
        const pkg = fs.readJsonSync(packageJson);
        if (pkg['monkey-coder']) {
          return packageJson;
        }
      } catch (error) {
        // Ignore invalid package.json
      }
    }

    return monkeyCoderJson; // Default path even if it doesn't exist
  }

  /**
   * Initialize encryption key
   */
  private initializeEncryption(): void {
    const machineId = os.hostname() + os.userInfo().username + this.globalConfigDir;
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

    const authTag = cipher.getAuthTag();
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

      const iv = Buffer.from(parts[0]!, 'hex');
      const authTag = Buffer.from(parts[1]!, 'hex');
      const encrypted = parts[2]!;

      const decipher = crypto.createDecipheriv(algorithm, this.encryptionKey, iv);
      decipher.setAuthTag(authTag);

      const decryptedBuffer = decipher.update(encrypted, 'hex');
      const finalBuffer = decipher.final();

      return Buffer.concat([decryptedBuffer, finalBuffer]).toString('utf8');
    } catch (error) {
      console.warn('Warning: Failed to decrypt stored token, may be corrupted');
      return '';
    }
  }

  /**
   * Decrypt config file (handles encrypted sensitive fields)
   */
  private decryptConfig(secureConfig: SecureConfigFile): ConfigFile {
    const config = { ...secureConfig } as any;

    if (secureConfig._encrypted && secureConfig._salt) {
      for (const field of SENSITIVE_FIELDS) {
        if (secureConfig._encrypted[field]) {
          try {
            config[field] = this.decrypt(secureConfig._encrypted[field]!);
          } catch (error) {
            console.warn(`Warning: Failed to decrypt ${field}`);
            config[field] = '';
          }
        }
      }
    }

    delete config._encrypted;
    delete config._salt;

    return config;
  }

  /**
   * Encrypt config file (encrypts sensitive fields)
   */
  private encryptConfig(config: ConfigFile): SecureConfigFile {
    const secureConfig: SecureConfigFile = { ...config };
    const encrypted: any = {};
    const salt = crypto.randomBytes(16).toString('hex');
    let hasSensitiveData = false;

    for (const field of SENSITIVE_FIELDS) {
      if (config[field] && typeof config[field] === 'string' && config[field] !== '') {
        encrypted[field] = this.encrypt(config[field] as string, salt);
        delete (secureConfig as any)[field];
        hasSensitiveData = true;
      }
    }

    if (hasSensitiveData) {
      secureConfig._encrypted = encrypted;
      secureConfig._salt = salt;
    }

    return secureConfig;
  }

  /**
   * Load all configs and merge them
   */
  private loadAllConfigsSync(): void {
    // Load global config
    if (fs.existsSync(this.globalConfigPath)) {
      try {
        const secureConfig = fs.readJsonSync(this.globalConfigPath);
        this.globalConfig = this.decryptConfig(secureConfig);
      } catch (error) {
        console.warn('Warning: Could not load global config');
        this.globalConfig = {};
      }
    }

    // Load local config
    if (fs.existsSync(this.localConfigPath)) {
      try {
        const secureConfig = fs.readJsonSync(this.localConfigPath);
        this.localConfig = this.decryptConfig(secureConfig);
      } catch (error) {
        console.warn('Warning: Could not load local config');
        this.localConfig = {};
      }
    }

    // Load project config
    if (fs.existsSync(this.projectConfigPath)) {
      try {
        if (this.projectConfigPath.endsWith('package.json')) {
          const pkg = fs.readJsonSync(this.projectConfigPath);
          this.projectConfig = pkg['monkey-coder'] || {};
        } else {
          this.projectConfig = fs.readJsonSync(this.projectConfigPath);
        }
      } catch (error) {
        console.warn('Warning: Could not load project config');
        this.projectConfig = {};
      }
    }

    // Merge configs: project > local > global
    this.mergedConfig = {
      ...this.globalConfig,
      ...this.localConfig,
      ...this.projectConfig,
    };
  }

  /**
   * Get configuration value from merged config
   */
  get<K extends keyof ConfigFile>(key: K): ConfigFile[K] {
    return this.mergedConfig[key];
  }

  /**
   * Set configuration value at specified scope
   */
  set<K extends keyof ConfigFile>(key: K, value: ConfigFile[K], scope: ConfigScope = 'global'): void {
    switch (scope) {
      case 'global':
        this.globalConfig[key] = value;
        break;
      case 'local':
        this.localConfig[key] = value;
        break;
      case 'project':
        this.projectConfig[key] = value;
        break;
    }

    // Re-merge configs
    this.mergedConfig = {
      ...this.globalConfig,
      ...this.localConfig,
      ...this.projectConfig,
    };
  }

  /**
   * Save configuration at specified scope
   */
  async saveConfig(scope: ConfigScope = 'global'): Promise<void> {
    let configToSave: ConfigFile;
    let configPath: string;

    switch (scope) {
      case 'global':
        configToSave = this.globalConfig;
        configPath = this.globalConfigPath;
        await fs.ensureDir(this.globalConfigDir);
        break;
      case 'local':
        configToSave = this.localConfig;
        configPath = this.localConfigPath;
        await fs.ensureDir(path.dirname(configPath));
        break;
      case 'project':
        configToSave = this.projectConfig;
        configPath = this.projectConfigPath;
        break;
      default:
        throw new Error(`Invalid config scope: ${scope}`);
    }

    try {
      // For project config in package.json, merge with existing package.json
      if (configPath.endsWith('package.json')) {
        const pkg = fs.existsSync(configPath) ? fs.readJsonSync(configPath) : {};
        pkg['monkey-coder'] = configToSave;
        await fs.writeJson(configPath, pkg, { spaces: 2 });
      } else {
        // Encrypt sensitive fields for global and local configs
        const secureConfig = scope !== 'project' 
          ? this.encryptConfig(configToSave)
          : configToSave;
        
        await fs.writeJson(configPath, secureConfig, { spaces: 2 });

        // Set restrictive permissions
        try {
          await fs.chmod(configPath, 0o600);
        } catch (error) {
          // chmod might fail on some systems
        }
      }
    } catch (error) {
      throw new Error(`Failed to save ${scope} config: ${error}`);
    }
  }

  /**
   * Get all configuration (merged)
   */
  getAll(): ConfigFile {
    return { ...this.mergedConfig };
  }

  /**
   * Get configuration at specific scope
   */
  getByScope(scope: ConfigScope): ConfigFile {
    switch (scope) {
      case 'global':
        return { ...this.globalConfig };
      case 'local':
        return { ...this.localConfig };
      case 'project':
        return { ...this.projectConfig };
      default:
        return {};
    }
  }

  /**
   * Get config sources (shows which config sets which keys)
   */
  getSources(): Record<string, ConfigScope> {
    const sources: Record<string, ConfigScope> = {};

    for (const key of Object.keys(this.mergedConfig)) {
      if (this.projectConfig[key as keyof ConfigFile] !== undefined) {
        sources[key] = 'project';
      } else if (this.localConfig[key as keyof ConfigFile] !== undefined) {
        sources[key] = 'local';
      } else if (this.globalConfig[key as keyof ConfigFile] !== undefined) {
        sources[key] = 'global';
      }
    }

    return sources;
  }

  /**
   * Get API key from config or environment
   */
  getApiKey(): string | undefined {
    return process.env.MONKEY_CODER_API_KEY || this.mergedConfig.apiKey;
  }

  /**
   * Get base URL from config or environment
   */
  getBaseUrl(): string {
    return process.env.MONKEY_CODER_BASE_URL || this.mergedConfig.baseUrl || 'http://localhost:8000';
  }

  /**
   * Get default persona
   */
  getDefaultPersona(): string {
    return this.mergedConfig.defaultPersona || 'developer';
  }

  /**
   * Get default model
   */
  getDefaultModel(): string {
    return this.mergedConfig.defaultModel || 'gpt-4.1';
  }

  /**
   * Get default provider
   */
  getDefaultProvider(): string {
    return this.mergedConfig.defaultProvider || 'openai';
  }

  /**
   * Get default temperature
   */
  getDefaultTemperature(): number {
    return this.mergedConfig.defaultTemperature || 0.7;
  }

  /**
   * Get default timeout
   */
  getDefaultTimeout(): number {
    return this.mergedConfig.defaultTimeout || 300;
  }

  /**
   * Reset configuration at specified scope
   */
  async reset(scope: ConfigScope = 'global'): Promise<void> {
    switch (scope) {
      case 'global':
        this.globalConfig = {};
        break;
      case 'local':
        this.localConfig = {};
        break;
      case 'project':
        this.projectConfig = {};
        break;
    }

    await this.saveConfig(scope);

    // Re-merge configs
    this.mergedConfig = {
      ...this.globalConfig,
      ...this.localConfig,
      ...this.projectConfig,
    };
  }
}
