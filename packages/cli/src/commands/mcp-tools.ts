/**
 * MCP Tools Commands - Enhanced tool discovery and execution
 * Provides commands for connecting to MCP servers, listing tools, and executing them
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import Table from 'cli-table3';
import * as fs from 'fs-extra';
import * as path from 'path';
import * as os from 'os';

import { getMCPManager, MCPServerConfig } from '../mcp-client.js';

// Config directory and file paths
const CONFIG_DIR = path.join(os.homedir(), '.monkey-coder');
const MCP_CONFIG_FILE = path.join(CONFIG_DIR, 'mcp-servers.json');

interface MCPConfig {
  servers: MCPServerConfig[];
}

/**
 * Load MCP server configuration from file
 */
function loadMCPConfig(): MCPConfig {
  if (!fs.existsSync(MCP_CONFIG_FILE)) {
    return { servers: [] };
  }
  try {
    return fs.readJSONSync(MCP_CONFIG_FILE);
  } catch (error) {
    console.warn(chalk.yellow(`Warning: Failed to load MCP config: ${error}`));
    return { servers: [] };
  }
}

/**
 * Save MCP server configuration to file
 */
function saveMCPConfig(config: MCPConfig): void {
  fs.ensureDirSync(CONFIG_DIR);
  fs.writeJSONSync(MCP_CONFIG_FILE, config, { spaces: 2 });
}

/**
 * Create the MCP tools command
 */
export function createMCPToolsCommand(): Command {
  const mcpTools = new Command('mcp-tools')
    .description('Manage and execute MCP tools');
  
  // List available tools
  mcpTools
    .command('list')
    .description('List all available MCP tools from connected servers')
    .option('-s, --server <name>', 'Filter by server name')
    .option('-j, --json', 'Output as JSON')
    .action(async (options) => {
      const spinner = ora('Fetching MCP tools...').start();
      
      try {
        const manager = getMCPManager();
        
        // Load and connect to configured servers
        const config = loadMCPConfig();
        for (const serverConfig of config.servers) {
          if (serverConfig.enabled !== false) {
            try {
              manager.registerServer(serverConfig);
              if (!manager.isConnected(serverConfig.name)) {
                await manager.connect(serverConfig.name);
              }
            } catch (error) {
              console.warn(chalk.yellow(`Warning: Failed to connect to ${serverConfig.name}: ${error}`));
            }
          }
        }
        
        const allTools = manager.getAllTools();
        
        // Filter by server if specified
        const tools = options.server
          ? allTools.filter(t => t.serverName === options.server)
          : allTools;
        
        spinner.stop();
        
        if (options.json) {
          console.log(JSON.stringify(tools, null, 2));
          return;
        }
        
        if (tools.length === 0) {
          console.log(chalk.yellow('No MCP tools found'));
          console.log(chalk.gray('Tip: Use `monkey mcp-tools connect <server>` to connect to an MCP server'));
          return;
        }
        
        console.log(chalk.cyan(`\nAvailable MCP Tools (${tools.length}):\n`));
        
        const table = new Table({
          head: ['Server', 'Tool Name', 'Description'],
          style: {
            head: ['cyan'],
          },
          colWidths: [20, 30, 50],
          wordWrap: true,
        });
        
        tools.forEach(tool => {
          table.push([
            chalk.green(tool.serverName),
            chalk.bold(tool.name),
            tool.description || chalk.gray('No description'),
          ]);
        });
        
        console.log(table.toString());
      } catch (error: any) {
        spinner.fail('Failed to list MCP tools');
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });
  
  // Connect to an MCP server
  mcpTools
    .command('connect <server>')
    .description('Connect to an MCP server')
    .option('-u, --url <url>', 'Server URL (for HTTP/SSE servers)')
    .option('-t, --type <type>', 'Server type (stdio, sse, http)', 'stdio')
    .option('-c, --command <command>', 'Command to start server (for stdio)')
    .option('-a, --args <args...>', 'Arguments for the command')
    .action(async (serverName, options) => {
      const spinner = ora(`Connecting to ${serverName}...`).start();
      
      try {
        const manager = getMCPManager();
        const config = loadMCPConfig();
        
        // Check if server is already configured
        let serverConfig = config.servers.find(s => s.name === serverName);
        
        if (!serverConfig) {
          // Create new server configuration
          if (options.type === 'stdio' && !options.command) {
            spinner.fail('Stdio server requires --command option');
            return;
          }
          if ((options.type === 'sse' || options.type === 'http') && !options.url) {
            spinner.fail('HTTP/SSE server requires --url option');
            return;
          }
          
          serverConfig = {
            name: serverName,
            type: options.type,
            command: options.command,
            args: options.args,
            url: options.url,
            enabled: true,
          };
          
          config.servers.push(serverConfig);
          saveMCPConfig(config);
        }
        
        // Register and connect
        manager.registerServer(serverConfig);
        await manager.connect(serverName);
        
        spinner.succeed(`Connected to ${chalk.green(serverName)}`);
        
        // Show available tools
        const tools = manager.getAllTools().filter(t => t.serverName === serverName);
        if (tools.length > 0) {
          console.log(chalk.cyan(`\nAvailable tools (${tools.length}):`));
          tools.forEach(tool => {
            console.log(`  • ${chalk.bold(tool.name)}: ${tool.description || 'No description'}`);
          });
        }
      } catch (error: any) {
        spinner.fail(`Failed to connect to ${serverName}`);
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });
  
  // Disconnect from an MCP server
  mcpTools
    .command('disconnect <server>')
    .description('Disconnect from an MCP server')
    .action(async (serverName) => {
      const spinner = ora(`Disconnecting from ${serverName}...`).start();
      
      try {
        const manager = getMCPManager();
        
        if (!manager.isConnected(serverName)) {
          spinner.warn(`${serverName} is not connected`);
          return;
        }
        
        await manager.disconnect(serverName);
        spinner.succeed(`Disconnected from ${chalk.gray(serverName)}`);
      } catch (error: any) {
        spinner.fail(`Failed to disconnect from ${serverName}`);
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });
  
  // Execute an MCP tool
  mcpTools
    .command('call <tool>')
    .description('Execute an MCP tool')
    .option('-a, --args <json>', 'Tool arguments as JSON string')
    .option('-s, --server <name>', 'Server name (if tool name is ambiguous)')
    .option('-j, --json', 'Output as JSON')
    .action(async (toolName, options) => {
      const spinner = ora(`Executing ${toolName}...`).start();
      
      try {
        const manager = getMCPManager();
        
        // Parse arguments
        const args = options.args ? JSON.parse(options.args) : {};
        
        // Load and connect to configured servers if not already connected
        const config = loadMCPConfig();
        for (const serverConfig of config.servers) {
          if (serverConfig.enabled !== false && !manager.isConnected(serverConfig.name)) {
            try {
              manager.registerServer(serverConfig);
              await manager.connect(serverConfig.name);
            } catch (error) {
              // Continue if connection fails
            }
          }
        }
        
        // Execute the tool
        const result = await manager.executeTool(toolName, args, options.server);
        
        spinner.stop();
        
        if (options.json) {
          console.log(JSON.stringify(result, null, 2));
          return;
        }
        
        if (result.isError) {
          console.log(chalk.red(`✗ Tool execution failed`));
          result.content.forEach(item => {
            if (item.type === 'text' && item.text) {
              console.log(chalk.red(item.text));
            }
          });
        } else {
          console.log(chalk.green(`✓ Tool executed successfully\n`));
          result.content.forEach(item => {
            if (item.type === 'text' && item.text) {
              console.log(item.text);
            } else if (item.data) {
              console.log(item.data);
            }
          });
        }
      } catch (error: any) {
        spinner.fail(`Failed to execute ${toolName}`);
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });
  
  // Show connected servers
  mcpTools
    .command('status')
    .description('Show status of MCP servers')
    .action(async () => {
      try {
        const manager = getMCPManager();
        const config = loadMCPConfig();
        
        if (config.servers.length === 0) {
          console.log(chalk.yellow('No MCP servers configured'));
          console.log(chalk.gray('Tip: Use `monkey mcp-tools connect <server>` to add a server'));
          return;
        }
        
        console.log(chalk.cyan('\nMCP Server Status:\n'));
        
        const table = new Table({
          head: ['Server', 'Type', 'Status', 'Tools'],
          style: {
            head: ['cyan'],
          },
        });
        
        for (const serverConfig of config.servers) {
          const isConnected = manager.isConnected(serverConfig.name);
          const tools = manager.getAllTools().filter(t => t.serverName === serverConfig.name);
          
          table.push([
            serverConfig.name,
            serverConfig.type,
            isConnected ? chalk.green('Connected') : chalk.gray('Disconnected'),
            tools.length.toString(),
          ]);
        }
        
        console.log(table.toString());
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });
  
  return mcpTools;
}
