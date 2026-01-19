/**
 * Configuration loader for Monkey Coder CLI
 * Handles loading, merging, and validating configuration from multiple sources
 */

import * as fs from 'fs';
import * as path from 'path';
import { MonkeyCoderConfigSchema, MonkeyCoderConfig } from './schema.js';

/**
 * List of config filenames to search for (in priority order)
 */
const CONFIG_FILENAMES = [
  '.monkey-coder.json',
  '.monkeycoderrc',
  '.monkeycoderrc.json',
];

/**
 * Global config path
 */
const GLOBAL_CONFIG_PATH = path.join(
  process.env.HOME || process.env.USERPROFILE || '',
  '.config',
  'monkey-coder',
  'config.json'
);

/**
 * Deep merge two objects, with override taking precedence
 * Arrays are replaced, not merged
 */
function deepMerge<T>(base: T, override: Partial<T>): T {
  const result = { ...base };
  for (const key of Object.keys(override) as (keyof T)[]) {
    const val = override[key];
    if (val !== undefined) {
      if (typeof val === 'object' && val !== null && !Array.isArray(val)) {
        result[key] = deepMerge(result[key] as any, val as any);
      } else {
        result[key] = val as any;
      }
    }
  }
  return result;
}

/**
 * Load configuration from all sources and merge them
 * Priority: project config > local config > global config > defaults
 * 
 * @param cwd - Current working directory to start search from
 * @returns Validated and merged configuration
 */
export async function loadConfig(cwd: string = process.cwd()): Promise<MonkeyCoderConfig> {
  // 1. Start with defaults
  let config = MonkeyCoderConfigSchema.parse({});

  // 2. Load global config if it exists
  if (fs.existsSync(GLOBAL_CONFIG_PATH)) {
    try {
      const globalConfig = JSON.parse(fs.readFileSync(GLOBAL_CONFIG_PATH, 'utf-8'));
      config = deepMerge(config, globalConfig);
    } catch (error) {
      console.warn(`Warning: Failed to load global config from ${GLOBAL_CONFIG_PATH}:`, error);
    }
  }

  // 3. Walk up directory tree looking for project config
  let dir = cwd;
  const root = path.parse(dir).root;
  
  while (dir !== path.dirname(dir)) {
    for (const filename of CONFIG_FILENAMES) {
      const configPath = path.join(dir, filename);
      if (fs.existsSync(configPath)) {
        try {
          const projectConfig = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
          config = deepMerge(config, projectConfig);
          // Stop at first found config
          return MonkeyCoderConfigSchema.parse(config);
        } catch (error) {
          console.warn(`Warning: Failed to load config from ${configPath}:`, error);
        }
      }
    }
    
    // Stop if we've reached the root directory
    if (dir === root) {
      break;
    }
    
    dir = path.dirname(dir);
  }

  // 4. Validate final config
  return MonkeyCoderConfigSchema.parse(config);
}

/**
 * Initialize a new config file in the specified directory
 * Creates a .monkey-coder.json with sensible defaults
 * 
 * @param cwd - Directory to create the config file in
 * @returns Path to the created config file
 */
export async function initConfig(cwd: string = process.cwd()): Promise<string> {
  const configPath = path.join(cwd, '.monkey-coder.json');
  
  // Check if config already exists
  if (fs.existsSync(configPath)) {
    throw new Error(`Config file already exists at ${configPath}`);
  }
  
  const defaultConfig = {
    version: 1,
    permissions: {
      allowedPaths: ['./**/*'],
      deniedPaths: [
        '**/.env*',
        '**/.git/**',
        '**/node_modules/**',
        '**/*.pem',
        '**/*.key',
        '**/secrets/**',
      ],
      allowedCommands: [
        'git *',
        'npm *',
        'yarn *',
        'pnpm *',
        'ls *',
        'cat *',
        'head *',
        'tail *',
        'grep *',
        'find *',
      ],
      deniedCommands: [
        'rm -rf /*',
        'sudo *',
        'chmod 777 *',
      ],
      requireApproval: true,
      maxFileSize: 10485760, // 10MB
      timeout: 30000, // 30 seconds
    },
    mcp: {
      servers: [],
    },
    agent: {
      defaultProvider: 'anthropic',
      defaultModel: 'claude-sonnet-4-5-20250929',
      maxIterations: 10,
      autoApprove: false,
      sandbox: 'basic',
    },
  };

  fs.writeFileSync(configPath, JSON.stringify(defaultConfig, null, 2) + '\n');
  return configPath;
}

/**
 * Get the path to the global config file
 */
export function getGlobalConfigPath(): string {
  return GLOBAL_CONFIG_PATH;
}

/**
 * Find the nearest project config file by walking up the directory tree
 * 
 * @param cwd - Current working directory to start search from
 * @returns Path to config file, or null if not found
 */
export function findProjectConfig(cwd: string = process.cwd()): string | null {
  let dir = cwd;
  const root = path.parse(dir).root;
  
  while (dir !== path.dirname(dir)) {
    for (const filename of CONFIG_FILENAMES) {
      const configPath = path.join(dir, filename);
      if (fs.existsSync(configPath)) {
        return configPath;
      }
    }
    
    if (dir === root) {
      break;
    }
    
    dir = path.dirname(dir);
  }
  
  return null;
}
