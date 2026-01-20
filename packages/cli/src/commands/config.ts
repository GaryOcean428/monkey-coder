/**
 * Configuration commands for Monkey Coder CLI
 * Handles getting, setting, and managing hierarchical configuration
 */

import { Command } from 'commander';
import chalk from 'chalk';
import inquirer from 'inquirer';
import Table from 'cli-table3';

import { ConfigManager } from '../config.js';
import { formatError } from '../utils.js';
import { CommandDefinition } from './registry.js';
import { loadConfig, initConfig, findProjectConfig, getGlobalConfigPath } from '../config/loader.js';

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
    .option('--global', 'Show global config only')
    .option('--local', 'Show local config only')
    .option('--project', 'Show project config only')
    .option('--show-sources', 'Show which file each value comes from')
    .option('--show-secrets', 'Show full values for sensitive keys')
    .addHelpText('after', `
Examples:
  $ monkey config list
    List all effective configuration

  $ monkey config list --show-sources
    Show which file each config value comes from

  $ monkey config list --global
    List global configuration only

  $ monkey config list --show-secrets
    Show full values (use with caution)
`)
    .action(async (options: any) => {
      try {
        // If showing sources, use getEffectiveConfig()
        if (options.showSources) {
          const effectiveConfig = config.getEffectiveConfig();
          
          if (Object.keys(effectiveConfig).length === 0) {
            console.log(chalk.yellow('No configuration set'));
            console.log(chalk.gray('\nRun "monkey config set <key> <value>" to configure'));
            return;
          }

          console.log(chalk.blue('\n📋 Configuration with Sources:'));
          
          const table = new Table({
            head: [chalk.cyan('Key'), chalk.cyan('Value'), chalk.cyan('Source')],
            colWidths: [25, 35, 40]
          });

          const sensitiveKeys = ['apiKey', 'refreshToken', 'password'];
          
          for (const [key, { value, source }] of Object.entries(effectiveConfig)) {
            let displayValue = String(value);
            
            // Mask sensitive values unless --show-secrets is used
            if (!options.showSecrets && sensitiveKeys.includes(key) && displayValue) {
              if (displayValue.length > 12) {
                displayValue = displayValue.substring(0, 8) + '...' + displayValue.substring(displayValue.length - 4);
              } else {
                displayValue = '***';
              }
            }
            
            table.push([key, displayValue || chalk.gray('(not set)'), chalk.gray(source)]);
          }

          console.log(table.toString());
          
          const locations = config.getConfigLocations();
          if (locations.length > 0) {
            console.log(chalk.blue('\n📂 Config Files (in priority order):'));
            locations.forEach((loc, idx) => {
              console.log(chalk.gray(`  ${idx + 1}. ${loc}`));
            });
          }
          
          if (!options.showSecrets) {
            console.log(chalk.gray('\nSensitive values are masked. Use --show-secrets to reveal.'));
          }
        } else {
          // Original simple list
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
          
          console.log(chalk.gray('\nTip: Use --show-sources to see which file each value comes from'));
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

  // config where - Show config file locations and which scope sets which keys
  configCmd
    .command('where')
    .description('Show configuration file locations and sources')
    .option('--verbose', 'Show detailed information')
    .addHelpText('after', `
Examples:
  $ monkey config where
    Show all config file locations

  $ monkey config where --verbose
    Show config locations and which file sets each key
`)
    .action(async (options: any) => {
      try {
        console.log(chalk.blue('\n📁 Configuration File Locations:\n'));
        
        // Show global config location
        const globalPath = '~/.config/monkey-coder/config.json';
        console.log(chalk.cyan('Global:   '), globalPath);
        
        // Show local config location
        const localPath = './.monkey-coder/config.json';
        console.log(chalk.cyan('Local:    '), localPath);
        
        // Show project config location  
        const projectPath = './monkey-coder.json (or package.json field)';
        console.log(chalk.cyan('Project:  '), projectPath);
        
        console.log(chalk.gray('\nPrecedence: project > local > global'));
        
        // If verbose, show which scope sets which keys
        if (options.verbose) {
          // This would use HierarchicalConfigManager.getSources()
          // For now, show a message
          console.log(chalk.blue('\n📊 Configuration Sources:\n'));
          console.log(chalk.gray('(Use hierarchical config to see which file sets each key)'));
        }
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to show config locations'));
        process.exit(1);
      }
    });

  // config init - Create .monkey-coder.json file
  configCmd
    .command('init')
    .description('Create .monkey-coder.json in current directory')
    .option('--force', 'Overwrite existing config file')
    .addHelpText('after', `
Examples:
  $ monkey config init
    Create a new .monkey-coder.json with default settings

  $ monkey config init --force
    Overwrite existing config file
`)
    .action(async (options: any) => {
      try {
        const configPath = await initConfig();
        console.log(chalk.green(`✓ Created config at ${configPath}`));
        console.log(chalk.gray('\nEdit this file to customize permissions, MCP servers, and agent defaults.'));
      } catch (error: any) {
        if (error.message.includes('already exists') && !options.force) {
          console.error(chalk.red('Config file already exists. Use --force to overwrite.'));
          process.exit(1);
        }
        console.error(formatError(error.message || 'Failed to initialize config'));
        process.exit(1);
      }
    });

  // config show - Display resolved configuration
  configCmd
    .command('show')
    .description('Show current resolved configuration')
    .option('--json', 'Output as JSON')
    .addHelpText('after', `
Examples:
  $ monkey config show
    Display the merged configuration from all sources

  $ monkey config show --json
    Output configuration as JSON
`)
    .action(async (options: any) => {
      try {
        const resolvedConfig = await loadConfig();
        
        if (options.json) {
          console.log(JSON.stringify(resolvedConfig, null, 2));
        } else {
          console.log(chalk.blue('\n📋 Resolved Configuration:\n'));
          console.log(chalk.gray('(Merged from global, local, and project configs)\n'));
          console.log(JSON.stringify(resolvedConfig, null, 2));
          
          const projectConfigPath = findProjectConfig();
          const globalConfigPath = getGlobalConfigPath();
          
          console.log(chalk.blue('\n📂 Configuration Sources:\n'));
          if (projectConfigPath) {
            console.log(chalk.green(`✓ Project: ${projectConfigPath}`));
          } else {
            console.log(chalk.gray('  Project: (none)'));
          }
          console.log(chalk.gray(`  Global:  ${globalConfigPath}`));
        }
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to show config'));
        process.exit(1);
      }
    });

  // config path - Show config file locations
  configCmd
    .command('path')
    .description('Show configuration file locations')
    .addHelpText('after', `
Examples:
  $ monkey config path
    Show where config files are searched for
`)
    .action(async () => {
      try {
        console.log(chalk.blue('\n📁 Configuration File Search Paths:\n'));
        console.log(chalk.cyan('Project configs (searched upward from current directory):'));
        console.log(chalk.gray('  1. .monkey-coder.json'));
        console.log(chalk.gray('  2. .monkeycoderrc'));
        console.log(chalk.gray('  3. .monkeycoderrc.json'));
        
        console.log(chalk.cyan('\nGlobal config:'));
        const globalPath = getGlobalConfigPath();
        console.log(chalk.gray(`  ${globalPath}`));
        
        console.log(chalk.blue('\n📊 Current Status:\n'));
        const projectConfigPath = findProjectConfig();
        if (projectConfigPath) {
          console.log(chalk.green(`✓ Project config found: ${projectConfigPath}`));
        } else {
          console.log(chalk.yellow('  No project config found'));
          console.log(chalk.gray('  Run "monkey config init" to create one'));
        }
        
        const globalConfigPath = getGlobalConfigPath();
        const fs = await import('fs');
        if (fs.existsSync(globalConfigPath)) {
          console.log(chalk.green(`✓ Global config found: ${globalConfigPath}`));
        } else {
          console.log(chalk.gray(`  No global config (${globalConfigPath})`));
        }
        
        console.log(chalk.gray('\nPrecedence: project > global > defaults'));
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to show paths'));
        process.exit(1);
      }
    });

  // config permissions - Manage permission rules
  const permissionsCmd = new Command('permissions')
    .description('Manage permission rules for file access and command execution')
    .alias('perms');

  // config permissions list
  permissionsCmd
    .command('list')
    .description('List current permission rules')
    .alias('ls')
    .option('--global', 'Show only global permissions')
    .option('--project', 'Show only project permissions')
    .option('--json', 'Output as JSON')
    .addHelpText('after', `
Examples:
  $ monkey config permissions list
    Show merged permission rules

  $ monkey config permissions list --global
    Show only global permission rules

  $ monkey config permissions list --json
    Output as JSON
`)
    .action(async (options: any) => {
      try {
        const { PermissionManager } = await import('../permissions.js');
        const permMgr = new PermissionManager();

        if (options.json) {
          if (options.global) {
            console.log(JSON.stringify(permMgr.getGlobalRules(), null, 2));
          } else if (options.project) {
            console.log(JSON.stringify(permMgr.getProjectRules() || {}, null, 2));
          } else {
            console.log(JSON.stringify(permMgr.getMergedRulesPublic(), null, 2));
          }
        } else {
          console.log(chalk.blue('\n📋 Permission Rules:\n'));

          const rules = options.global 
            ? permMgr.getGlobalRules() 
            : options.project 
              ? permMgr.getProjectRules() 
              : permMgr.getMergedRulesPublic();

          if (!rules) {
            console.log(chalk.yellow('No project-specific permissions set'));
            return;
          }

          console.log(chalk.cyan('File Read:'));
          console.log(chalk.green('  Allow:'));
          (rules.fileRead?.allow || []).forEach(p => console.log(chalk.gray(`    - ${p}`)));
          console.log(chalk.red('  Deny:'));
          (rules.fileRead?.deny || []).forEach(p => console.log(chalk.gray(`    - ${p}`)));

          console.log(chalk.cyan('\nFile Write:'));
          console.log(chalk.green('  Allow:'));
          (rules.fileWrite?.allow || []).forEach(p => console.log(chalk.gray(`    - ${p}`)));
          console.log(chalk.red('  Deny:'));
          (rules.fileWrite?.deny || []).forEach(p => console.log(chalk.gray(`    - ${p}`)));

          console.log(chalk.cyan('\nShell Execute:'));
          console.log(chalk.green('  Allow:'));
          (rules.shellExecute?.allow || []).forEach(p => console.log(chalk.gray(`    - ${p}`)));
          console.log(chalk.red('  Deny:'));
          (rules.shellExecute?.deny || []).forEach(p => console.log(chalk.gray(`    - ${p}`)));

          console.log(chalk.cyan('\nRequire Approval:'));
          (rules.requireApproval || []).forEach(p => console.log(chalk.gray(`  - ${p}`)));

          console.log(chalk.gray(`\nConfig file: ${permMgr.getPermissionsFilePath()}`));
          if (!options.global) {
            console.log(chalk.gray(`Project file: ${permMgr.getProjectRCPath()}`));
          }
        }
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to list permissions'));
        process.exit(1);
      }
    });

  // config permissions allow
  permissionsCmd
    .command('allow')
    .description('Add a pattern to the allow list')
    .argument('<category>', 'Category: fileRead, fileWrite, or shellExecute')
    .argument('<pattern>', 'Glob pattern to allow')
    .option('--global', 'Add to global permissions')
    .option('--project', 'Add to project permissions')
    .addHelpText('after', `
Examples:
  $ monkey config permissions allow fileRead "src/**/*.ts"
    Allow reading TypeScript files in src directory

  $ monkey config permissions allow shellExecute "docker *"
    Allow docker commands

  $ monkey config permissions allow fileWrite "dist/**/*" --project
    Allow writing to dist directory (project-specific)
`)
    .action(async (category: string, pattern: string, options: any) => {
      try {
        const { PermissionManager } = await import('../permissions.js');
        const permMgr = new PermissionManager();

        if (!['fileRead', 'fileWrite', 'shellExecute'].includes(category)) {
          console.error(chalk.red('Invalid category. Must be: fileRead, fileWrite, or shellExecute'));
          process.exit(1);
        }

        const rules = options.project 
          ? (permMgr.getProjectRules() || {})
          : permMgr.getGlobalRules();

        // Get current category rules
        const currentCategory = rules[category as 'fileRead' | 'fileWrite' | 'shellExecute'];
        const allowList = Array.isArray(currentCategory) ? [] : (currentCategory?.allow || []);

        const updatedCategory = {
          allow: [...allowList, pattern],
          deny: Array.isArray(currentCategory) ? [] : (currentCategory?.deny || [])
        };

        const updatedRules = {
          [category]: updatedCategory
        };

        if (options.project) {
          await permMgr.saveProjectRules(updatedRules);
          console.log(chalk.green(`✓ Added "${pattern}" to ${category} allow list (project)`));
        } else {
          await permMgr.saveGlobalRules(updatedRules);
          console.log(chalk.green(`✓ Added "${pattern}" to ${category} allow list (global)`));
        }
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to add permission'));
        process.exit(1);
      }
    });

  // config permissions deny
  permissionsCmd
    .command('deny')
    .description('Add a pattern to the deny list')
    .argument('<category>', 'Category: fileRead, fileWrite, or shellExecute')
    .argument('<pattern>', 'Glob pattern to deny')
    .option('--global', 'Add to global permissions')
    .option('--project', 'Add to project permissions')
    .addHelpText('after', `
Examples:
  $ monkey config permissions deny fileRead "**/.env*"
    Deny reading .env files

  $ monkey config permissions deny shellExecute "rm -rf /*"
    Deny dangerous rm command

  $ monkey config permissions deny fileWrite "**/node_modules/**" --project
    Deny writing to node_modules (project-specific)
`)
    .action(async (category: string, pattern: string, options: any) => {
      try {
        const { PermissionManager } = await import('../permissions.js');
        const permMgr = new PermissionManager();

        if (!['fileRead', 'fileWrite', 'shellExecute'].includes(category)) {
          console.error(chalk.red('Invalid category. Must be: fileRead, fileWrite, or shellExecute'));
          process.exit(1);
        }

        const rules = options.project 
          ? (permMgr.getProjectRules() || {})
          : permMgr.getGlobalRules();

        // Get current category rules
        const currentCategory = rules[category as 'fileRead' | 'fileWrite' | 'shellExecute'];
        const denyList = Array.isArray(currentCategory) ? [] : (currentCategory?.deny || []);

        const updatedCategory = {
          allow: Array.isArray(currentCategory) ? [] : (currentCategory?.allow || []),
          deny: [...denyList, pattern]
        };

        const updatedRules = {
          [category]: updatedCategory
        };

        if (options.project) {
          await permMgr.saveProjectRules(updatedRules);
          console.log(chalk.green(`✓ Added "${pattern}" to ${category} deny list (project)`));
        } else {
          await permMgr.saveGlobalRules(updatedRules);
          console.log(chalk.green(`✓ Added "${pattern}" to ${category} deny list (global)`));
        }
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to add permission'));
        process.exit(1);
      }
    });

  // config permissions test
  permissionsCmd
    .command('test')
    .description('Test if a file or command is allowed')
    .argument('<type>', 'Type: read, write, or command')
    .argument('<value>', 'File path or command to test')
    .addHelpText('after', `
Examples:
  $ monkey config permissions test read ".env"
    Test if .env file can be read

  $ monkey config permissions test write "src/index.ts"
    Test if src/index.ts can be written

  $ monkey config permissions test command "npm install"
    Test if npm install command is allowed
`)
    .action(async (type: string, value: string) => {
      try {
        const { PermissionManager } = await import('../permissions.js');
        const permMgr = new PermissionManager();

        let result: { allowed: boolean; reason?: string; requiresApproval?: boolean };

        if (type === 'read') {
          result = permMgr.canReadFile(value);
        } else if (type === 'write') {
          result = permMgr.canWriteFile(value);
        } else if (type === 'command') {
          result = permMgr.canExecuteCommand(value);
        } else {
          console.error(chalk.red('Invalid type. Must be: read, write, or command'));
          process.exit(1);
        }

        if (result.allowed) {
          console.log(chalk.green(`✓ Allowed${result.requiresApproval ? ' (requires approval)' : ''}`));
        } else {
          console.log(chalk.red(`✗ Denied: ${result.reason}`));
        }
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to test permission'));
        process.exit(1);
      }
    });

  // config permissions reset
  permissionsCmd
    .command('reset')
    .description('Reset permissions to defaults')
    .option('--global', 'Reset global permissions')
    .option('--project', 'Reset project permissions')
    .option('--force', 'Skip confirmation')
    .addHelpText('after', `
Examples:
  $ monkey config permissions reset --global
    Reset global permissions to defaults

  $ monkey config permissions reset --project
    Remove all project-specific permissions
`)
    .action(async (options: any) => {
      try {
        if (!options.force) {
          const scope = options.project ? 'project' : 'global';
          const answers = await inquirer.prompt([
            {
              type: 'confirm',
              name: 'confirmed',
              message: `Are you sure you want to reset ${scope} permissions?`,
              default: false,
            }
          ]);
          
          if (!answers.confirmed) {
            console.log(chalk.yellow('Reset cancelled'));
            return;
          }
        }

        const { PermissionManager } = await import('../permissions.js');
        const permMgr = new PermissionManager();
        const fs = await import('fs/promises');

        if (options.project) {
          // Remove permissions from .monkeyrc.json
          const rcPath = permMgr.getProjectRCPath();
          try {
            const content = await fs.readFile(rcPath, 'utf-8');
            const rc = JSON.parse(content);
            delete rc.permissions;
            await fs.writeFile(rcPath, JSON.stringify(rc, null, 2), 'utf-8');
            console.log(chalk.green('✓ Project permissions reset'));
          } catch (error: any) {
            if (error.code === 'ENOENT') {
              console.log(chalk.yellow('No project permissions file found'));
            } else {
              throw error;
            }
          }
        } else {
          // Delete global permissions file
          try {
            await fs.unlink(permMgr.getPermissionsFilePath());
            console.log(chalk.green('✓ Global permissions reset to defaults'));
          } catch (error: any) {
            if (error.code === 'ENOENT') {
              console.log(chalk.yellow('Global permissions already at defaults'));
            } else {
              throw error;
            }
          }
        }
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to reset permissions'));
        process.exit(1);
      }
    });

  configCmd.addCommand(permissionsCmd);

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
    },
    {
      name: 'init',
      description: 'Create .monkey-coder.json in current directory',
      category: 'config',
      options: [
        { flags: '--force', description: 'Overwrite existing config' }
      ],
      examples: [
        { command: 'monkey config init', description: 'Create default config file' }
      ]
    },
    {
      name: 'show',
      description: 'Show current resolved configuration',
      category: 'config',
      options: [
        { flags: '--json', description: 'Output as JSON' }
      ],
      examples: [
        { command: 'monkey config show', description: 'Display merged configuration' }
      ]
    },
    {
      name: 'path',
      description: 'Show configuration file locations',
      category: 'config',
      examples: [
        { command: 'monkey config path', description: 'Show config file search paths' }
      ]
    },
    {
      name: 'permissions',
      aliases: ['perms'],
      description: 'Manage permission rules for file access and command execution',
      category: 'config',
      subcommands: [
        {
          name: 'list',
          aliases: ['ls'],
          description: 'List current permission rules',
          category: 'config',
          options: [
            { flags: '--global', description: 'Show only global permissions' },
            { flags: '--project', description: 'Show only project permissions' },
            { flags: '--json', description: 'Output as JSON' }
          ],
          examples: [
            { command: 'monkey config permissions list', description: 'Show merged permission rules' }
          ]
        },
        {
          name: 'allow',
          description: 'Add a pattern to the allow list',
          category: 'config',
          arguments: [
            { name: 'category', description: 'fileRead, fileWrite, or shellExecute', required: true },
            { name: 'pattern', description: 'Glob pattern to allow', required: true }
          ],
          options: [
            { flags: '--global', description: 'Add to global permissions' },
            { flags: '--project', description: 'Add to project permissions' }
          ],
          examples: [
            { command: 'monkey config permissions allow fileRead "src/**/*.ts"', description: 'Allow reading TypeScript files' }
          ]
        },
        {
          name: 'deny',
          description: 'Add a pattern to the deny list',
          category: 'config',
          arguments: [
            { name: 'category', description: 'fileRead, fileWrite, or shellExecute', required: true },
            { name: 'pattern', description: 'Glob pattern to deny', required: true }
          ],
          options: [
            { flags: '--global', description: 'Add to global permissions' },
            { flags: '--project', description: 'Add to project permissions' }
          ],
          examples: [
            { command: 'monkey config permissions deny fileRead "**/.env*"', description: 'Deny reading .env files' }
          ]
        },
        {
          name: 'test',
          description: 'Test if a file or command is allowed',
          category: 'config',
          arguments: [
            { name: 'type', description: 'read, write, or command', required: true },
            { name: 'value', description: 'File path or command to test', required: true }
          ],
          examples: [
            { command: 'monkey config permissions test read ".env"', description: 'Test if .env can be read' }
          ]
        },
        {
          name: 'reset',
          description: 'Reset permissions to defaults',
          category: 'config',
          options: [
            { flags: '--global', description: 'Reset global permissions' },
            { flags: '--project', description: 'Reset project permissions' },
            { flags: '--force', description: 'Skip confirmation' }
          ]
        }
      ]
    }
  ]
};
