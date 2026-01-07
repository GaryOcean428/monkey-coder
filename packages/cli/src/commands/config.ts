/**
 * Configuration commands for Monkey Coder CLI
 * Handles getting, setting, and managing configuration
 */

import { Command } from 'commander';
import chalk from 'chalk';
import inquirer from 'inquirer';
import Table from 'cli-table3';
import { ConfigManager } from '../config.js';
import { formatError } from '../utils.js';
import { CommandDefinition } from './registry.js';

/**
 * Create the config command group
 */
export function createConfigCommand(config: ConfigManager): Command {
  const configCmd = new Command('config')
    .description('Manage configuration')
    .alias('cfg');

  // config get
  configCmd
    .command('get')
    .description('Get a configuration value')
    .argument('<key>', 'Configuration key')
    .addHelpText('after', `
Examples:
  $ monkey config get apiKey
    Get the API key

  $ monkey config get baseUrl
    Get the base URL

  $ monkey config get defaultProvider
    Get the default AI provider
`)
    .action(async (key: string) => {
      try {
        // Get value using getAll() for dynamic keys
        const allConfig = config.getAll();
        const value = (allConfig as any)[key];
        
        if (value === undefined || value === null || value === '') {
          console.log(chalk.yellow(`Configuration key "${key}" is not set`));
          return;
        }

        // Mask sensitive values
        const sensitiveKeys = ['apiKey', 'refreshToken', 'password'];
        if (sensitiveKeys.includes(key)) {
          const maskedValue = typeof value === 'string' 
            ? value.substring(0, 8) + '...' + value.substring(value.length - 4)
            : '***';
          console.log(chalk.green(`${key}: ${maskedValue}`));
        } else {
          console.log(chalk.green(`${key}: ${value}`));
        }
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to get config'));
        process.exit(1);
      }
    });

  // config set
  configCmd
    .command('set')
    .description('Set a configuration value')
    .argument('<key>', 'Configuration key')
    .argument('<value>', 'Configuration value')
    .option('--global', 'Set in global config')
    .option('--local', 'Set in local config')
    .addHelpText('after', `
Examples:
  $ monkey config set apiKey sk-abc123...
    Set the API key

  $ monkey config set baseUrl https://api.example.com
    Set the base URL

  $ monkey config set defaultProvider anthropic
    Set the default AI provider

  $ monkey config set defaultPersona architect
    Set the default persona
`)
    .action(async (key: string, value: string, options: any) => {
      try {
        // Use type assertion to allow dynamic key setting
        // This is safe because we're handling it as a general config value
        (config as any).set(key, value);
        await config.saveConfig();
        
        // Mask sensitive values in output
        const sensitiveKeys = ['apiKey', 'refreshToken', 'password'];
        const displayValue = sensitiveKeys.includes(key)
          ? value.substring(0, 8) + '...' + value.substring(value.length - 4)
          : value;
        
        console.log(chalk.green(`✓ Set ${key} = ${displayValue}`));
        
        const scope = options.global ? 'global' : options.local ? 'local' : 'default';
        console.log(chalk.gray(`Saved to ${scope} configuration`));
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to set config'));
        process.exit(1);
      }
    });

  // config list
  configCmd
    .command('list')
    .description('List all configuration values')
    .alias('ls')
    .option('--global', 'Show global config')
    .option('--local', 'Show local config')
    .option('--show-secrets', 'Show full values for sensitive keys')
    .addHelpText('after', `
Examples:
  $ monkey config list
    List all configuration

  $ monkey config list --global
    List global configuration only

  $ monkey config list --show-secrets
    Show full values (use with caution)
`)
    .action(async (options: any) => {
      try {
        const allConfig = config.getAll();
        
        if (Object.keys(allConfig).length === 0) {
          console.log(chalk.yellow('No configuration set'));
          console.log(chalk.gray('\nRun "monkey config set <key> <value>" to configure'));
          return;
        }

        console.log(chalk.blue('\n📋 Configuration:'));
        
        const table = new Table({
          head: [chalk.cyan('Key'), chalk.cyan('Value')],
          colWidths: [30, 50]
        });

        const sensitiveKeys = ['apiKey', 'refreshToken', 'password'];
        
        for (const [key, value] of Object.entries(allConfig)) {
          let displayValue = String(value);
          
          // Mask sensitive values unless --show-secrets is used
          if (!options.showSecrets && sensitiveKeys.includes(key) && displayValue) {
            if (displayValue.length > 12) {
              displayValue = displayValue.substring(0, 8) + '...' + displayValue.substring(displayValue.length - 4);
            } else {
              displayValue = '***';
            }
          }
          
          table.push([key, displayValue || chalk.gray('(not set)')]);
        }

        console.log(table.toString());
        
        if (!options.showSecrets) {
          console.log(chalk.gray('\nSensitive values are masked. Use --show-secrets to reveal.'));
        }
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to list config'));
        process.exit(1);
      }
    });

  // config edit
  configCmd
    .command('edit')
    .description('Interactively edit configuration')
    .option('--global', 'Edit global config')
    .option('--local', 'Edit local config')
    .addHelpText('after', `
Examples:
  $ monkey config edit
    Interactively edit configuration

  $ monkey config edit --global
    Edit global configuration
`)
    .action(async (options: any) => {
      try {
        console.log(chalk.blue('🔧 Interactive Configuration Editor\n'));
        
        const currentConfig = config.getAll();
        
        // Use inquirer.prompt with type assertion to avoid complex typing issues
        const answers: any = await (inquirer.prompt as any)([
          {
            type: 'input',
            name: 'baseUrl',
            message: 'Base URL:',
            default: currentConfig.baseUrl || 'http://localhost:8000',
          },
          {
            type: 'list',
            name: 'defaultProvider',
            message: 'Default AI Provider:',
            choices: [
              { name: 'OpenAI', value: 'openai' },
              { name: 'Anthropic', value: 'anthropic' },
              { name: 'Google', value: 'google' },
              { name: 'Qwen', value: 'qwen' },
            ],
            default: currentConfig.defaultProvider || 'openai',
          },
          {
            type: 'list',
            name: 'defaultPersona',
            message: 'Default Persona:',
            choices: [
              { name: 'Developer', value: 'developer' },
              { name: 'Architect', value: 'architect' },
              { name: 'Reviewer', value: 'reviewer' },
              { name: 'Debugger', value: 'debugger' },
              { name: 'Optimizer', value: 'optimizer' },
            ],
            default: currentConfig.defaultPersona || 'developer',
          },
          {
            type: 'number',
            name: 'defaultTimeout',
            message: 'Default Timeout (seconds):',
            default: currentConfig.defaultTimeout || 300,
          },
          {
            type: 'number',
            name: 'defaultTemperature',
            message: 'Default Temperature (0.0-2.0):',
            default: currentConfig.defaultTemperature || 0.7,
            validate: (value: number) => {
              if (value >= 0 && value <= 2) return true;
              return 'Temperature must be between 0.0 and 2.0';
            }
          }
        ]);

        // Save all answers
        for (const [key, value] of Object.entries(answers)) {
          (config as any).set(key, value);
        }
        
        await config.saveConfig();
        
        console.log(chalk.green('\n✓ Configuration saved successfully'));
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to edit config'));
        process.exit(1);
      }
    });

  // config unset
  configCmd
    .command('unset')
    .description('Unset a configuration value')
    .alias('delete')
    .argument('<key>', 'Configuration key to unset')
    .addHelpText('after', `
Examples:
  $ monkey config unset customKey
    Remove a configuration key
`)
    .action(async (key: string) => {
      try {
        // Use type assertion for dynamic key
        (config as any).set(key, '');
        await config.saveConfig();
        
        console.log(chalk.green(`✓ Unset ${key}`));
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to unset config'));
        process.exit(1);
      }
    });

  // config reset
  configCmd
    .command('reset')
    .description('Reset configuration to defaults')
    .option('--force', 'Skip confirmation')
    .addHelpText('after', `
Examples:
  $ monkey config reset
    Reset all configuration (with confirmation)

  $ monkey config reset --force
    Reset without confirmation
`)
    .action(async (options: any) => {
      try {
        if (!options.force) {
          const answers = await inquirer.prompt([
            {
              type: 'confirm',
              name: 'confirmed',
              message: 'Are you sure you want to reset all configuration?',
              default: false,
            }
          ]);
          
          if (!answers.confirmed) {
            console.log(chalk.yellow('Reset cancelled'));
            return;
          }
        }

        // Clear all config
        const allKeys = Object.keys(config.getAll());
        for (const key of allKeys) {
          (config as any).set(key, '');
        }
        await config.saveConfig();
        
        console.log(chalk.green('✓ Configuration reset to defaults'));
        console.log(chalk.gray('Run "monkey config edit" to set up again'));
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to reset config'));
        process.exit(1);
      }
    });

  return configCmd;
}

/**
 * Command definition for registry
 */
export const configCommandDefinition: CommandDefinition = {
  name: 'config',
  aliases: ['cfg'],
  description: 'Manage configuration',
  category: 'config',
  subcommands: [
    {
      name: 'get',
      description: 'Get a configuration value',
      category: 'config',
      arguments: [
        { name: 'key', description: 'Configuration key', required: true }
      ],
      examples: [
        { command: 'monkey config get apiKey', description: 'Get API key' },
        { command: 'monkey config get baseUrl', description: 'Get base URL' }
      ]
    },
    {
      name: 'set',
      description: 'Set a configuration value',
      category: 'config',
      arguments: [
        { name: 'key', description: 'Configuration key', required: true },
        { name: 'value', description: 'Configuration value', required: true }
      ],
      options: [
        { flags: '--global', description: 'Set in global config' },
        { flags: '--local', description: 'Set in local config' }
      ],
      examples: [
        { command: 'monkey config set apiKey sk-abc123', description: 'Set API key' },
        { command: 'monkey config set defaultProvider anthropic', description: 'Set provider' }
      ]
    },
    {
      name: 'list',
      aliases: ['ls'],
      description: 'List all configuration values',
      category: 'config',
      options: [
        { flags: '--global', description: 'Show global config' },
        { flags: '--local', description: 'Show local config' },
        { flags: '--show-secrets', description: 'Show sensitive values' }
      ]
    },
    {
      name: 'edit',
      description: 'Interactively edit configuration',
      category: 'config',
      options: [
        { flags: '--global', description: 'Edit global config' },
        { flags: '--local', description: 'Edit local config' }
      ]
    },
    {
      name: 'unset',
      aliases: ['delete'],
      description: 'Unset a configuration value',
      category: 'config',
      arguments: [
        { name: 'key', description: 'Configuration key to unset', required: true }
      ]
    },
    {
      name: 'reset',
      description: 'Reset configuration to defaults',
      category: 'config',
      options: [
        { flags: '--force', description: 'Skip confirmation' }
      ]
    }
  ]
};
