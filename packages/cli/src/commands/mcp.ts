/**
 * MCP (Model Context Protocol) commands for the Monkey CLI
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import Table from 'cli-table3';

import { ConfigManager } from '../config.js';
import { MonkeyCoderAPIClient } from '../api-client.js';
import { formatError } from '../utils.js';

export function createMCPCommand(config: ConfigManager): Command {
  const mcp = new Command('mcp')
    .description('Manage MCP (Model Context Protocol) servers');
    
  const client = new MonkeyCoderAPIClient(config.getBaseUrl(), config.getApiKey());

  // List available MCP servers
  mcp
    .command('list')
    .description('List all available MCP servers')
    .option('-s, --status', 'Show server status')
    .option('-j, --json', 'Output as JSON')
    .action(async (options) => {
      const spinner = ora('Fetching MCP servers...').start();

      try {
        const response = await client.get('/mcp/servers');
        const servers = response.data.servers;

        spinner.stop();

        if (options.json) {
          console.log(JSON.stringify(servers, null, 2));
          return;
        }

        if (servers.length === 0) {
          console.log(chalk.yellow('No MCP servers found'));
          return;
        }

        const table = new Table({
          head: options.status
            ? ['Name', 'Type', 'Status', 'Enabled', 'Tools', 'Resources']
            : ['Name', 'Type', 'Description', 'Enabled'],
          style: {
            head: ['cyan'],
          },
        });

        servers.forEach((server: any) => {
          if (options.status) {
            table.push([
              server.name,
              server.type,
              server.status === 'connected'
                ? chalk.green(server.status)
                : server.status === 'error'
                ? chalk.red(server.status)
                : chalk.yellow(server.status),
              server.enabled ? chalk.green('Yes') : chalk.gray('No'),
              server.tools || 0,
              server.resources || 0,
            ]);
          } else {
            table.push([
              server.name,
              server.type,
              server.description || '-',
              server.enabled ? chalk.green('Yes') : chalk.gray('No'),
            ]);
          }
        });

        console.log(table.toString());
      } catch (error: any) {
        spinner.stop();
        console.error(formatError(error.message || 'Failed to list MCP servers'));
      }
    });

  // Enable an MCP server
  mcp
    .command('enable <server>')
    .description('Enable an MCP server')
    .action(async (serverName) => {
      const spinner = ora(`Enabling ${serverName}...`).start();

      try {
        await client.post(`/mcp/servers/${serverName}/enable`);
        spinner.succeed(`MCP server ${chalk.green(serverName)} enabled`);
      } catch (error: any) {
        spinner.fail(`Failed to enable ${serverName}`);
        console.error(formatError(error.message));
      }
    });

  // Disable an MCP server
  mcp
    .command('disable <server>')
    .description('Disable an MCP server')
    .action(async (serverName) => {
      const spinner = ora(`Disabling ${serverName}...`).start();

      try {
        await client.post(`/mcp/servers/${serverName}/disable`);
        spinner.succeed(`MCP server ${chalk.gray(serverName)} disabled`);
      } catch (error: any) {
        spinner.fail(`Failed to disable ${serverName}`);
        console.error(formatError(error.message));
      }
    });

  // Start an MCP server
  mcp
    .command('start <server>')
    .description('Start an MCP server')
    .action(async (serverName) => {
      const spinner = ora(`Starting ${serverName}...`).start();

      try {
        await client.post(`/mcp/servers/${serverName}/start`);
        spinner.succeed(`MCP server ${chalk.green(serverName)} started`);
      } catch (error: any) {
        spinner.fail(`Failed to start ${serverName}`);
        console.error(formatError(error.message));
      }
    });

  // Stop an MCP server
  mcp
    .command('stop <server>')
    .description('Stop an MCP server')
    .action(async (serverName) => {
      const spinner = ora(`Stopping ${serverName}...`).start();

      try {
        await client.post(`/mcp/servers/${serverName}/stop`);
        spinner.succeed(`MCP server ${chalk.red(serverName)} stopped`);
      } catch (error: any) {
        spinner.fail(`Failed to stop ${serverName}`);
        console.error(formatError(error.message));
      }
    });

  // Install a new MCP server
  mcp
    .command('install <package>')
    .description('Install an MCP server from npm package')
    .option('-n, --name <name>', 'Custom name for the server')
    .action(async (packageName, options) => {
      const spinner = ora(`Installing ${packageName}...`).start();

      try {
        const response = await client.post('/mcp/servers/install', {
          package: packageName,
          name: options.name,
        });

        spinner.succeed(
          `MCP server ${chalk.green(response.data.name)} installed successfully`
        );
        console.log(chalk.gray('Run `monkey mcp enable ' + response.data.name + '` to enable it'));
      } catch (error: any) {
        spinner.fail(`Failed to install ${packageName}`);
        console.error(formatError(error.message));
      }
    });

  // Search for MCP servers
  mcp
    .command('search <query>')
    .description('Search for available MCP servers')
    .option('-t, --tags <tags>', 'Filter by tags (comma-separated)')
    .action(async (query, options) => {
      const spinner = ora('Searching MCP servers...').start();

      try {
        const params: any = { query };
        if (options.tags) {
          params.tags = options.tags.split(',');
        }

        const response = await client.get('/mcp/servers/search', { params });
        const servers = response.data.servers;

        spinner.stop();

        if (servers.length === 0) {
          console.log(chalk.yellow('No matching MCP servers found'));
          return;
        }

        const table = new Table({
          head: ['Name', 'Type', 'Description', 'Tags'],
          style: {
            head: ['cyan'],
          },
        });

        servers.forEach((server: any) => {
          table.push([
            server.name,
            server.type,
            server.description || '-',
            server.tags ? server.tags.join(', ') : '-',
          ]);
        });

        console.log(table.toString());
      } catch (error: any) {
        spinner.stop();
        console.error(formatError(error.message || 'Failed to search MCP servers'));
      }
    });

  // Configure an MCP server
  mcp
    .command('config <server>')
    .description('Configure an MCP server')
    .option('-i, --interactive', 'Interactive configuration')
    .option('-s, --set <key=value>', 'Set a config value', (val: string, prev: Record<string, string>) => {
      const parts = val.split('=');
      if (parts.length >= 2 && parts[0]) {
        const key = parts[0];
        const value = parts.slice(1).join('='); // Handle values with = in them
        const result: Record<string, string> = { ...prev };
        result[key] = value;
        return result;
      }
      return prev;
    }, {} as Record<string, string>)
    .action(async (serverName, options) => {
      try {
        // Get current config
        const response = await client.get(`/mcp/servers/${serverName}`);
        const serverInfo = response.data;

        if (!serverInfo) {
          console.error(chalk.red(`Server ${serverName} not found`));
          return;
        }

        let newConfig = {};

        if (options.interactive) {
          // Interactive configuration based on schema
          const schema = serverInfo.config_schema;
          if (!schema || !schema.properties) {
            console.error(chalk.red('No configuration schema available for this server'));
            return;
          }

          const questions = Object.entries(schema.properties).map(
            ([key, prop]: [string, any]) => ({
              type: prop.type === 'boolean' ? 'confirm' : 'input',
              name: key,
              message: prop.description || `Enter ${key}:`,
              default: serverInfo.config?.[key] || prop.default,
            })
          );

          const inquirer = (await import('inquirer')).default;
          const answers = await inquirer.prompt(questions as any);
          newConfig = answers;
        } else if (options.set) {
          newConfig = options.set;
        } else {
          // Show current config
          console.log(chalk.cyan(`Configuration for ${serverName}:`));
          console.log(JSON.stringify(serverInfo.config || {}, null, 2));
          return;
        }

        // Update config
        const spinner = ora('Updating configuration...').start();
        await client.put(`/mcp/servers/${serverName}/config`, newConfig);
        spinner.succeed('Configuration updated successfully');
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to configure server'));
      }
    });

  // Show server info
  mcp
    .command('info <server>')
    .description('Show detailed information about an MCP server')
    .action(async (serverName) => {
      try {
        const response = await client.get(`/mcp/servers/${serverName}`);
        const server = response.data;

        if (!server) {
          console.error(chalk.red(`Server ${serverName} not found`));
          return;
        }

        console.log(chalk.cyan('Server Information:'));
        console.log(`  Name: ${server.name}`);
        console.log(`  Type: ${server.type}`);
        console.log(`  Status: ${server.status}`);
        console.log(`  Enabled: ${server.enabled ? 'Yes' : 'No'}`);

        if (server.description) {
          console.log(`  Description: ${server.description}`);
        }

        if (server.capabilities && server.capabilities.length > 0) {
          console.log(`  Capabilities: ${server.capabilities.join(', ')}`);
        }

        if (server.tools && server.tools.length > 0) {
          console.log('\n' + chalk.cyan('Available Tools:'));
          server.tools.forEach((tool: any) => {
            console.log(`  - ${chalk.green(tool.name)}: ${tool.description || '-'}`);
          });
        }

        if (server.resources && server.resources.length > 0) {
          console.log('\n' + chalk.cyan('Available Resources:'));
          server.resources.forEach((resource: any) => {
            console.log(`  - ${chalk.blue(resource.uri)}: ${resource.name || '-'}`);
          });
        }

        if (server.config_schema) {
          console.log('\n' + chalk.cyan('Configuration Options:'));
          Object.entries(server.config_schema.properties || {}).forEach(
            ([key, prop]: [string, any]) => {
              console.log(
                `  - ${key}: ${prop.description || prop.type || 'No description'}`
              );
            }
          );
        }
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to get server info'));
      }
    });

  // Test MCP server connection
  mcp
    .command('test <server>')
    .description('Test connection to an MCP server')
    .action(async (serverName) => {
      const spinner = ora(`Testing connection to ${serverName}...`).start();

      try {
        const response = await client.post(`/mcp/servers/${serverName}/test`);
        
        if (response.data.success) {
          spinner.succeed(`Connection to ${chalk.green(serverName)} successful`);
          
          if (response.data.tools) {
            console.log(`  Tools available: ${response.data.tools}`);
          }
          if (response.data.resources) {
            console.log(`  Resources available: ${response.data.resources}`);
          }
        } else {
          spinner.fail(`Connection to ${serverName} failed`);
          if (response.data.error) {
            console.error(chalk.red(`  Error: ${response.data.error}`));
          }
        }
      } catch (error: any) {
        spinner.fail(`Failed to test ${serverName}`);
        console.error(formatError(error.message));
      }
    });

  // Export MCP configuration
  mcp
    .command('export [file]')
    .description('Export MCP configuration to a file')
    .action(async (file) => {
      try {
        const response = await client.get('/mcp/config');
        const configData = response.data;

        if (file) {
          const fs = await import('fs/promises');
          await fs.writeFile(file, JSON.stringify(configData, null, 2));
          console.log(chalk.green(`✓ Configuration exported to ${file}`));
        } else {
          console.log(JSON.stringify(configData, null, 2));
        }
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to export configuration'));
      }
    });

  // Import MCP configuration
  mcp
    .command('import <file>')
    .description('Import MCP configuration from a file')
    .option('-f, --force', 'Overwrite existing configuration')
    .action(async (file, options) => {
      try {
        const fs = await import('fs/promises');
        const configData = JSON.parse(await fs.readFile(file, 'utf-8'));

        const spinner = ora('Importing configuration...').start();
        await client.post('/mcp/config/import', {
          config: configData,
          force: options.force,
        });
        spinner.succeed('Configuration imported successfully');
      } catch (error: any) {
        console.error(formatError(error.message || 'Failed to import configuration'));
      }
    });
    
  return mcp;
}
