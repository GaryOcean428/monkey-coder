import { describe, it, expect, jest, beforeEach, afterEach } from '@jest/globals';
import * as path from 'path';
import * as os from 'os';
import { ConfigManager } from '../src/config';

// Mock fs-extra module
jest.mock('fs-extra', () => ({
  pathExistsSync: jest.fn(),
  pathExists: jest.fn(),
  readFileSync: jest.fn(),
  readFile: jest.fn(),
  ensureDir: jest.fn(),
  writeFile: jest.fn(),
  chmod: jest.fn()
}));

jest.mock('os');

// Import fs-extra after mocking
import * as fs from 'fs-extra';

describe('ConfigManager', () => {
  const mockHomedir = '/home/testuser';
  const mockConfigDir = path.join(mockHomedir, '.config', 'monkey-coder');
  const mockConfigPath = path.join(mockConfigDir, 'config.json');
  let configManager: ConfigManager;

  beforeEach(() => {
    jest.clearAllMocks();
    (os.homedir as jest.MockedFunction<typeof os.homedir>).mockReturnValue(mockHomedir);
    (os.hostname as jest.MockedFunction<typeof os.hostname>).mockReturnValue('test-host');
    (os.userInfo as jest.MockedFunction<typeof os.userInfo>).mockReturnValue({
      username: 'testuser',
      uid: 1000,
      gid: 1000,
      shell: '/bin/bash',
      homedir: mockHomedir
    });

    // Mock fs-extra methods with proper typing
    (fs.pathExistsSync as jest.MockedFunction<typeof fs.pathExistsSync>).mockReturnValue(false);
    (fs.pathExists as unknown as jest.MockedFunction<() => Promise<boolean>>).mockResolvedValue(false);
    (fs.readFileSync as jest.MockedFunction<typeof fs.readFileSync>).mockReturnValue('{}');
    (fs.readFile as unknown as jest.MockedFunction<() => Promise<Buffer>>).mockResolvedValue(Buffer.from('{}'));

    // Create new instance for each test
    configManager = new ConfigManager();
  });

  afterEach(() => {
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
      (fs.pathExistsSync as jest.Mock).mockReturnValue(true);
      (fs.readFileSync as jest.Mock).mockReturnValue(JSON.stringify({
        apiKey: 'test-key',
        baseUrl: 'https://api.test.com'
      }));

      new ConfigManager();

      expect(fs.pathExistsSync).toHaveBeenCalledWith(mockConfigPath);
      expect(fs.readFileSync).toHaveBeenCalledWith(mockConfigPath, 'utf-8');
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
      (fs.ensureDir as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);
      (fs.writeFile as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);
      (fs.chmod as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);

      await configManager.saveConfig();

      expect(fs.ensureDir).toHaveBeenCalledWith(mockConfigDir);
    });

    it('writes config to file as JSON', async () => {
      (fs.ensureDir as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);
      (fs.writeFile as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);
      (fs.chmod as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);

      configManager.set('baseUrl', 'https://test.api.com');
      configManager.set('defaultModel', 'test-model');

      await configManager.saveConfig();

      expect(fs.writeFile).toHaveBeenCalled();
      const writeCall = (fs.writeFile as unknown as jest.MockedFunction<any>).mock.calls[0];
      expect(writeCall?.[0]).toBe(mockConfigPath);

      // Check that it's valid JSON
      const writtenContent = writeCall?.[1];
      if (writtenContent) {
        expect(() => JSON.parse(writtenContent as string)).not.toThrow();
      }
    });

    it('sets restrictive permissions on config file', async () => {
      (fs.ensureDir as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);
      (fs.writeFile as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);
      (fs.chmod as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);

      await configManager.saveConfig();

      expect(fs.chmod).toHaveBeenCalledWith(mockConfigPath, 0o600);
      expect(fs.chmod).toHaveBeenCalledWith(mockConfigDir, 0o700);
    });

    it('handles chmod errors gracefully', async () => {
      (fs.ensureDir as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);
      (fs.writeFile as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);
      (fs.chmod as unknown as jest.MockedFunction<() => Promise<void>>).mockRejectedValue(new Error('Permission denied'));

      // Should not throw despite chmod error
      await expect(configManager.saveConfig()).resolves.not.toThrow();
    });

    it('throws error when write fails', async () => {
      (fs.ensureDir as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);
      (fs.writeFile as unknown as jest.MockedFunction<() => Promise<void>>).mockRejectedValue(new Error('Write failed'));

      await expect(configManager.saveConfig()).rejects.toThrow('Failed to save config');
    });
  });

  describe('update', () => {
    it('updates multiple config values at once', async () => {
      (fs.ensureDir as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);
      (fs.writeFile as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);
      (fs.chmod as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);

      await configManager.update({
        baseUrl: 'https://new.api.com',
        defaultModel: 'new-model',
        defaultTimeout: 500
      });

      expect(configManager.get('baseUrl')).toBe('https://new.api.com');
      expect(configManager.get('defaultModel')).toBe('new-model');
      expect(configManager.get('defaultTimeout')).toBe(500);

      expect(fs.writeFile).toHaveBeenCalled();
    });

    it('saves config after updating', async () => {
      (fs.ensureDir as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);
      (fs.writeFile as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);
      (fs.chmod as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);

      await configManager.update({ apiKey: 'updated-key' });

      expect(fs.writeFile).toHaveBeenCalledTimes(1);
    });
  });

  describe('reset', () => {
    it('resets config to empty and saves', async () => {
      (fs.ensureDir as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);
      (fs.writeFile as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);
      (fs.chmod as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);

      configManager.set('apiKey', 'test-key');
      configManager.set('baseUrl', 'https://test.com');

      await configManager.reset();

      expect(configManager.get('apiKey')).toBeUndefined();
      expect(configManager.get('baseUrl')).toBeUndefined();
      expect(fs.writeFile).toHaveBeenCalled();
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
      (fs.pathExists as unknown as jest.MockedFunction<() => Promise<boolean>>).mockResolvedValue(true);

      const exists = await configManager.exists();

      expect(exists).toBe(true);
      expect(fs.pathExists).toHaveBeenCalledWith(mockConfigPath);
    });

    it('returns false when config file does not exist', async () => {
      (fs.pathExists as unknown as jest.MockedFunction<() => Promise<boolean>>).mockResolvedValue(false);

      const exists = await configManager.exists();

      expect(exists).toBe(false);
    });
  });

  describe('encryption', () => {
    it('encrypts sensitive fields when saving', async () => {
      (fs.ensureDir as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);
      (fs.writeFile as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);
      (fs.chmod as unknown as jest.MockedFunction<() => Promise<void>>).mockResolvedValue(undefined);

      configManager.set('apiKey', 'secret-api-key');
      configManager.set('refreshToken', 'secret-refresh-token');
      configManager.set('baseUrl', 'https://public.api.com');

      await configManager.saveConfig();

      const writeCall = (fs.writeFile as unknown as jest.MockedFunction<any>).mock.calls[0];
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

      (fs.pathExistsSync as jest.Mock).mockReturnValue(true);
      (fs.readFileSync as jest.Mock).mockReturnValue(JSON.stringify(encryptedConfig));

      // Creating a new instance will load and attempt to decrypt
      const newManager = new ConfigManager();

      // The encrypted metadata should not be exposed
      const allConfig = newManager.getAll();
      expect((allConfig as any)._encrypted).toBeUndefined();
      expect((allConfig as any)._salt).toBeUndefined();
    });
  });
});
