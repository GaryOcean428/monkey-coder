/**
 * Configuration Manager for Monkey Coder CLI
 * Handles loading and saving user preferences and API settings
 */

import fs from 'fs-extra';
import * as path from 'path';
import * as os from 'os';
import { ConfigFile } from './types.js';

export class ConfigManager {
  private configDir: string;
  private configPath: string;
  private config: ConfigFile;

  constructor() {
    // Use XDG config directory or fallback to ~/.config
    const xdgConfigHome = process.env.XDG_CONFIG_HOME;
    this.configDir = xdgConfigHome 
      ? path.join(xdgConfigHome, 'monkey-coder')
      : path.join(os.homedir(), '.config', 'monkey-coder');
    
    this.configPath = path.join(this.configDir, 'config.json');
    this.config = {};
    
    // Load config synchronously to ensure it's available immediately
    this.loadConfigSync();
  }

  /**
   * Load configuration from file
   */
  private async loadConfig(): Promise<void> {
    try {
      if (await fs.pathExists(this.configPath)) {
        const configData = await fs.readFile(this.configPath, 'utf-8');
        this.config = JSON.parse(configData);
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
        this.config = JSON.parse(configData);
      }
    } catch (error) {
      // Silently use defaults for sync loading
      this.config = {};
    }
  }

  /**
   * Save configuration to file
   */
  async saveConfig(): Promise<void> {
    try {
      await fs.ensureDir(this.configDir);
      await fs.writeFile(this.configPath, JSON.stringify(this.config, null, 2), 'utf-8');
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
    return process.env.MONKEY_CODER_API_URL || this.config.baseUrl || 'https://monkey-coder.up.railway.app';
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
    return this.config.defaultModel || 'claude-sonnet-4-20250514';
  }

  /**
   * Get default provider
   */
  getDefaultProvider(): string {
    return this.config.defaultProvider || 'anthropic';
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
