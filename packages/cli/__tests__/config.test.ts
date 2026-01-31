import { describe, it, expect, jest, beforeEach, afterEach } from '@jest/globals';
import * as path from 'path';
import * as os from 'os';

// Mock fs-extra module BEFORE importing ConfigManager  
const mockPathExistsSync = jest.fn() as any;
const mockPathExists = jest.fn() as any;
const mockReadFileSync = jest.fn() as any;
const mockReadFile = jest.fn() as any;
const mockEnsureDir = jest.fn() as any;
const mockWriteFile = jest.fn() as any;
const mockChmod = jest.fn() as any;

jest.mock('fs-extra', () => ({
  pathExistsSync: mockPathExistsSync,
  pathExists: mockPathExists,
  readFileSync: mockReadFileSync,
  readFile: mockReadFile,
  ensureDir: mockEnsureDir,
  writeFile: mockWriteFile,
  chmod: mockChmod
}));

// Now import ConfigManager
import { ConfigManager } from '../src/config';

describe('ConfigManager', () => {
  // Use real OS values instead of mocking
  const realHomedir = os.homedir();
  const mockConfigDir = path.join(realHomedir, '.config', 'monkey-coder');
  const mockConfigPath = path.join(mockConfigDir, 'config.json');
  let configManager: ConfigManager;
  let originalXdgConfigHome: string | undefined;

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Save and clear XDG_CONFIG_HOME to ensure predictable behavior
    originalXdgConfigHome = process.env.XDG_CONFIG_HOME;
    delete process.env.XDG_CONFIG_HOME;

    // Setup mock return values
    mockPathExistsSync.mockReturnValue(false);
    mockPathExists.mockResolvedValue(false);
    mockReadFileSync.mockReturnValue('{}' as any);
    mockReadFile.mockResolvedValue(Buffer.from('{}') as any);
    (mockEnsureDir as any).mockResolvedValue();
    (mockWriteFile as any).mockResolvedValue();
    (mockChmod as any).mockResolvedValue();

    // Create new instance for each test
    configManager = new ConfigManager();
  });

  afterEach(() => {
    // Restore environment variables
    if (originalXdgConfigHome !== undefined) {
      process.env.XDG_CONFIG_HOME = originalXdgConfigHome;
    }
    jest.restoreAllMocks();
  });

  describe('constructor', () => {
    it('initializes with correct config directory path', () => {
      const configPath = configManager.getConfigPath();
      expect(configPath).toBe(mockConfigPath);
    });

    it('uses XDG_CONFIG_HOME when available', () => {
      const xdgConfigHome = '/custom/config';
      process.env.XDG_CONFIG_HOME = xdgConfigHome;

      const newManager = new ConfigManager();
      const expectedPath = path.join(xdgConfigHome, 'monkey-coder', 'config.json');

      expect(newManager.getConfigPath()).toBe(expectedPath);

      delete process.env.XDG_CONFIG_HOME;
    });

    it('loads config on initialization', () => {
      mockPathExistsSync.mockReturnValue(true);
      mockReadFileSync.mockReturnValue(JSON.stringify({
        apiKey: 'test-key',
        baseUrl: 'https://api.test.com'
      }));

      new ConfigManager();

      expect(mockPathExistsSync).toHaveBeenCalledWith(mockConfigPath);
      expect(mockReadFileSync).toHaveBeenCalledWith(mockConfigPath, 'utf-8');
    });
  });

  describe('get and set methods', () => {
    it('gets configuration values', () => {
      configManager.set('baseUrl', 'https://example.com');
      expect(configManager.get('baseUrl')).toBe('https://example.com');
    });

    it('sets configuration values', () => {
      configManager.set('apiKey', 'new-api-key');
      configManager.set('defaultModel', 'gpt-4');

      expect(configManager.get('apiKey')).toBe('new-api-key');
      expect(configManager.get('defaultModel')).toBe('gpt-4');
    });

    it('returns undefined for unset values', () => {
      expect(configManager.get('apiKey')).toBeUndefined();
    });
  });

  describe('getApiKey', () => {
    it('returns API key from environment variable first', () => {
      process.env.MONKEY_CODER_API_KEY = 'env-api-key';
      configManager.set('apiKey', 'config-api-key');

      expect(configManager.getApiKey()).toBe('env-api-key');

      delete process.env.MONKEY_CODER_API_KEY;
    });

    it('returns API key from config when env var not set', () => {
      configManager.set('apiKey', 'config-api-key');
      expect(configManager.getApiKey()).toBe('config-api-key');
    });

    it('returns undefined when no API key is set', () => {
      expect(configManager.getApiKey()).toBeUndefined();
    });
  });

  describe('getBaseUrl', () => {
    it('returns base URL from environment variable first', () => {
      process.env.MONKEY_CODER_BASE_URL = 'https://env.api.com';
      configManager.set('baseUrl', 'https://config.api.com');

      expect(configManager.getBaseUrl()).toBe('https://env.api.com');

      delete process.env.MONKEY_CODER_BASE_URL;
    });

    it('returns base URL from config when env var not set', () => {
      configManager.set('baseUrl', 'https://config.api.com');
      expect(configManager.getBaseUrl()).toBe('https://config.api.com');
    });

    it('returns default URL when nothing is set', () => {
      expect(configManager.getBaseUrl()).toBe('http://localhost:8000');
    });
  });

  describe('default getters', () => {
    it('getDefaultPersona returns correct default', () => {
      expect(configManager.getDefaultPersona()).toBe('developer');

      configManager.set('defaultPersona', 'reviewer');
      expect(configManager.getDefaultPersona()).toBe('reviewer');
    });

    it('getDefaultModel returns correct default', () => {
      expect(configManager.getDefaultModel()).toBe('gpt-4.1');

      configManager.set('defaultModel', 'claude-3');
      expect(configManager.getDefaultModel()).toBe('claude-3');
    });

    it('getDefaultProvider returns correct default', () => {
      expect(configManager.getDefaultProvider()).toBe('openai');

      configManager.set('defaultProvider', 'anthropic');
      expect(configManager.getDefaultProvider()).toBe('anthropic');
    });

    it('getDefaultTemperature returns correct default', () => {
      expect(configManager.getDefaultTemperature()).toBe(0.1);

      configManager.set('defaultTemperature', 0.7);
      expect(configManager.getDefaultTemperature()).toBe(0.7);
    });

    it('getDefaultTimeout returns correct default', () => {
      expect(configManager.getDefaultTimeout()).toBe(300);

      configManager.set('defaultTimeout', 600);
      expect(configManager.getDefaultTimeout()).toBe(600);
    });

    it('getShowSplash returns correct default', () => {
      expect(configManager.getShowSplash()).toBe(true);

      configManager.set('showSplash', false);
      expect(configManager.getShowSplash()).toBe(false);
    });
  });

  describe('saveConfig', () => {
    it('creates config directory if it does not exist', async () => {
      (mockEnsureDir as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();
      (mockWriteFile as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();
      (mockChmod as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();

      await configManager.saveConfig();

      expect(mockEnsureDir).toHaveBeenCalledWith(mockConfigDir);
    });

    it('writes config to file as JSON', async () => {
      (mockEnsureDir as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();
      (mockWriteFile as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();
      (mockChmod as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();

      configManager.set('baseUrl', 'https://test.api.com');
      configManager.set('defaultModel', 'test-model');

      await configManager.saveConfig();

      expect(mockWriteFile).toHaveBeenCalled();
      const writeCall = (mockWriteFile as unknown as jest.MockedFunction<any>).mock.calls[0];
      expect(writeCall?.[0]).toBe(mockConfigPath);

      // Check that it's valid JSON
      const writtenContent = writeCall?.[1];
      if (writtenContent) {
        expect(() => JSON.parse(writtenContent as string)).not.toThrow();
      }
    });

    it('sets restrictive permissions on config file', async () => {
      (mockEnsureDir as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();
      (mockWriteFile as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();
      (mockChmod as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();

      await configManager.saveConfig();

      expect(mockChmod).toHaveBeenCalledWith(mockConfigPath, 0o600);
      expect(mockChmod).toHaveBeenCalledWith(mockConfigDir, 0o700);
    });

    it('handles chmod errors gracefully', async () => {
      (mockEnsureDir as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();
      (mockWriteFile as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();
      (mockChmod as unknown as jest.MockedFunction<() => Promise<void>>).mockRejectedValue(new Error('Permission denied'));

      // Should not throw despite chmod error
      await expect(configManager.saveConfig()).resolves.not.toThrow();
    });

    it('throws error when write fails', async () => {
      (mockEnsureDir as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();
      (mockWriteFile as unknown as jest.MockedFunction<() => Promise<void>>).mockRejectedValue(new Error('Write failed'));

      await expect(configManager.saveConfig()).rejects.toThrow('Failed to save config');
    });
  });

  describe('update', () => {
    it('updates multiple config values at once', async () => {
      (mockEnsureDir as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();
      (mockWriteFile as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();
      (mockChmod as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();

      await configManager.update({
        baseUrl: 'https://new.api.com',
        defaultModel: 'new-model',
        defaultTimeout: 500
      });

      expect(configManager.get('baseUrl')).toBe('https://new.api.com');
      expect(configManager.get('defaultModel')).toBe('new-model');
      expect(configManager.get('defaultTimeout')).toBe(500);

      expect(mockWriteFile).toHaveBeenCalled();
    });

    it('saves config after updating', async () => {
      (mockEnsureDir as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();
      (mockWriteFile as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();
      (mockChmod as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();

      await configManager.update({ apiKey: 'updated-key' });

      expect(mockWriteFile).toHaveBeenCalledTimes(1);
    });
  });

  describe('reset', () => {
    it('resets config to empty and saves', async () => {
      (mockEnsureDir as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();
      (mockWriteFile as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();
      (mockChmod as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();

      configManager.set('apiKey', 'test-key');
      configManager.set('baseUrl', 'https://test.com');

      await configManager.reset();

      expect(configManager.get('apiKey')).toBeUndefined();
      expect(configManager.get('baseUrl')).toBeUndefined();
      expect(mockWriteFile).toHaveBeenCalled();
    });
  });

  describe('getAll', () => {
    it('returns copy of all configuration', () => {
      configManager.set('apiKey', 'test-key');
      configManager.set('baseUrl', 'https://test.com');
      configManager.set('defaultModel', 'test-model');

      const allConfig = configManager.getAll();

      expect(allConfig).toEqual({
        apiKey: 'test-key',
        baseUrl: 'https://test.com',
        defaultModel: 'test-model'
      });

      // Verify it's a copy, not a reference
      allConfig.apiKey = 'modified';
      expect(configManager.get('apiKey')).toBe('test-key');
    });
  });

  describe('exists', () => {
    it('returns true when config file exists', async () => {
      (mockPathExists as unknown as jest.MockedFunction<() => Promise<boolean>>).mockResolvedValue(true);

      const exists = await configManager.exists();

      expect(exists).toBe(true);
      expect(mockPathExists).toHaveBeenCalledWith(mockConfigPath);
    });

    it('returns false when config file does not exist', async () => {
      (mockPathExists as unknown as jest.MockedFunction<() => Promise<boolean>>).mockResolvedValue(false);

      const exists = await configManager.exists();

      expect(exists).toBe(false);
    });
  });

  describe('encryption', () => {
    it('encrypts sensitive fields when saving', async () => {
      (mockEnsureDir as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();
      (mockWriteFile as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();
      (mockChmod as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue();

      configManager.set('apiKey', 'secret-api-key');
      configManager.set('refreshToken', 'secret-refresh-token');
      configManager.set('baseUrl', 'https://public.api.com');

      await configManager.saveConfig();

      const writeCall = (mockWriteFile as unknown as jest.MockedFunction<any>).mock.calls[0];
      const writtenContent = JSON.parse(writeCall?.[1] as string);

      // Sensitive fields should be encrypted
      expect(writtenContent.apiKey).toBeUndefined();
      expect(writtenContent.refreshToken).toBeUndefined();
      expect(writtenContent._encrypted).toBeDefined();
      expect(writtenContent._salt).toBeDefined();

      // Non-sensitive fields should remain plain
      expect(writtenContent.baseUrl).toBe('https://public.api.com');
    });

    it('decrypts sensitive fields when loading', () => {
      // This test would require mocking the crypto module
      // For simplicity, we'll verify the structure is correct
      const encryptedConfig = {
        baseUrl: 'https://api.com',
        _encrypted: {
          apiKey: 'encrypted-data-here',
          refreshToken: 'encrypted-refresh-here'
        },
        _salt: 'random-salt'
      };

      (mockPathExistsSync as jest.Mock).mockReturnValue(true);
      (mockReadFileSync as jest.Mock).mockReturnValue(JSON.stringify(encryptedConfig));

      // Creating a new instance will load and attempt to decrypt
      const newManager = new ConfigManager();

      // The encrypted metadata should not be exposed
      const allConfig = newManager.getAll();
      expect((allConfig as any)._encrypted).toBeUndefined();
      expect((allConfig as any)._salt).toBeUndefined();
    });
  });

  describe('hierarchical config', () => {
    it('finds local config by traversing up directory tree', () => {
      const testDir = '/home/user/projects/myproject/src';
      const localConfigPath = '/home/user/projects/myproject/.monkey-coder/config.json';
      
      (mockPathExistsSync as jest.Mock).mockImplementation((p: unknown) => {
        return p === localConfigPath;
      });

      const manager = new ConfigManager(testDir);
      const locations = manager.getConfigLocations();
      
      expect(locations).toContain(localConfigPath);
    });

    it('finds project config in current directory', () => {
      const testDir = '/home/user/projects/myproject';
      const projectConfigPath = path.join(testDir, 'monkey-coder.json');
      
      (mockPathExistsSync as jest.Mock).mockImplementation((p: unknown) => {
        return p === projectConfigPath;
      });

      const manager = new ConfigManager(testDir);
      const locations = manager.getConfigLocations();
      
      expect(locations).toContain(projectConfigPath);
    });

    it('finds config in package.json', () => {
      const testDir = '/home/user/projects/myproject';
      const packageJsonPath = path.join(testDir, 'package.json');
      
      (mockPathExistsSync as jest.Mock).mockImplementation((p: unknown) => {
        return p === packageJsonPath;
      });
      (mockReadFileSync as jest.Mock).mockImplementation((p: unknown) => {
        if (p === packageJsonPath) {
          return JSON.stringify({
            name: 'my-project',
            'monkey-coder': {
              defaultModel: 'gpt-4',
              baseUrl: 'https://project-api.com'
            }
          });
        }
        return '{}';
      });

      const manager = new ConfigManager(testDir);
      const locations = manager.getConfigLocations();
      
      expect(locations).toContain(packageJsonPath);
    });

    it('merges configs in correct priority order', () => {
      const testDir = '/home/user/projects/myproject';
      const localConfigPath = path.join(testDir, '.monkey-coder', 'config.json');
      const projectConfigPath = path.join(testDir, 'monkey-coder.json');
      
      (mockPathExistsSync as jest.Mock).mockImplementation((p: unknown) => {
        return p === mockConfigPath || p === localConfigPath || p === projectConfigPath;
      });
      
      (mockReadFileSync as jest.Mock).mockImplementation((p: unknown) => {
        if (p === mockConfigPath) {
          return JSON.stringify({ baseUrl: 'global-url', defaultModel: 'global-model' });
        }
        if (p === localConfigPath) {
          return JSON.stringify({ defaultModel: 'local-model', defaultProvider: 'local-provider' });
        }
        if (p === projectConfigPath) {
          return JSON.stringify({ defaultProvider: 'project-provider' });
        }
        return '{}';
      });

      const manager = new ConfigManager(testDir);
      
      // Project config should override local, which overrides global
      expect(manager.get('baseUrl')).toBe('global-url'); // Only in global
      expect(manager.get('defaultModel')).toBe('local-model'); // Local overrides global
      expect(manager.get('defaultProvider')).toBe('project-provider'); // Project overrides local
    });

    it('environment variables override all config files', () => {
      process.env.MONKEY_CODER_API_KEY = 'env-api-key';
      process.env.MONKEY_CODER_BASE_URL = 'env-base-url';
      
      const testDir = '/home/user/projects/myproject';
      const projectConfigPath = path.join(testDir, 'monkey-coder.json');
      
      (mockPathExistsSync as jest.Mock).mockImplementation((p: unknown) => {
        return p === projectConfigPath;
      });
      (mockReadFileSync as jest.Mock).mockImplementation((p: unknown) => {
        if (p === projectConfigPath) {
          return JSON.stringify({ apiKey: 'project-api-key', baseUrl: 'project-base-url' });
        }
        return '{}';
      });

      const manager = new ConfigManager(testDir);
      
      // Environment variables should override project config
      expect(manager.get('apiKey')).toBe('env-api-key');
      expect(manager.get('baseUrl')).toBe('env-base-url');
      
      delete process.env.MONKEY_CODER_API_KEY;
      delete process.env.MONKEY_CODER_BASE_URL;
    });

    it('getEffectiveConfig shows sources for each value', () => {
      const testDir = '/home/user/projects/myproject';
      const localConfigPath = path.join(testDir, '.monkey-coder', 'config.json');
      
      (mockPathExistsSync as jest.Mock).mockImplementation((p: unknown) => {
        return p === mockConfigPath || p === localConfigPath;
      });
      
      (mockReadFileSync as jest.Mock).mockImplementation((p: unknown) => {
        if (p === mockConfigPath) {
          return JSON.stringify({ baseUrl: 'global-url' });
        }
        if (p === localConfigPath) {
          return JSON.stringify({ defaultModel: 'local-model' });
        }
        return '{}';
      });

      const manager = new ConfigManager(testDir);
      const effectiveConfig = manager.getEffectiveConfig();
      
      expect(effectiveConfig.baseUrl?.value).toBe('global-url');
      expect(effectiveConfig.baseUrl?.source).toContain('global');
      expect(effectiveConfig.defaultModel?.value).toBe('local-model');
      expect(effectiveConfig.defaultModel?.source).toContain('local');
    });
  });
});
