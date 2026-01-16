/**
 * MCP Client - Model Context Protocol integration for local tool execution
 * 
 * Provides a unified interface for connecting to MCP servers (both local stdio
 * and remote HTTP), discovering tools, and executing them with proper error handling.
 */

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { SSEClientTransport } from '@modelcontextprotocol/sdk/client/sse.js';
import { z } from 'zod';
import { spawn, ChildProcess } from 'child_process';
import { EventEmitter } from 'events';

// Types
export interface MCPServerConfig {
  name: string;
  type: 'stdio' | 'sse' | 'http';
  command?: string;
  args?: string[];
  env?: Record<string, string>;
  url?: string;
  timeout?: number;
  enabled?: boolean;
}

export interface MCPTool {
  name: string;
  description?: string;
  inputSchema: Record<string, unknown>;
  serverName: string;
}

export interface MCPResource {
  uri: string;
  name: string;
  description?: string;
  mimeType?: string;
  serverName: string;
}

export interface ToolExecutionResult {
  success: boolean;
  content: Array<{
    type: string;
    text?: string;
    data?: string;
    mimeType?: string;
  }>;
  isError?: boolean;
}

export interface MCPClientEvents {
  'server:connected': (serverName: string) => void;
  'server:disconnected': (serverName: string, error?: Error) => void;
  'server:error': (serverName: string, error: Error) => void;
  'tool:executed': (serverName: string, toolName: string, result: ToolExecutionResult) => void;
}

/**
 * MCP Client Manager - manages connections to multiple MCP servers
 */
export class MCPClientManager extends EventEmitter {
  private clients: Map<string, Client> = new Map();
  private processes: Map<string, ChildProcess> = new Map();
  private configs: Map<string, MCPServerConfig> = new Map();
  private tools: Map<string, MCPTool[]> = new Map();
  private resources: Map<string, MCPResource[]> = new Map();

  constructor() {
    super();
  }

  /**
   * Register an MCP server configuration
   */
  registerServer(config: MCPServerConfig): void {
    this.configs.set(config.name, config);
  }

  /**
   * Connect to an MCP server
   */
  async connect(serverName: string): Promise<void> {
    const config = this.configs.get(serverName);
    if (!config) {
      throw new Error(`Server configuration not found: ${serverName}`);
    }

    if (this.clients.has(serverName)) {
      return; // Already connected
    }

    const client = new Client(
      { name: 'monkey-coder-cli', version: '1.6.0' },
      { capabilities: { tools: {}, resources: {} } }
    );

    let transport;

    if (config.type === 'stdio') {
      if (!config.command) {
        throw new Error(`Stdio server requires command: ${serverName}`);
      }

      const childProcess = spawn(config.command, config.args || [], {
        env: { ...process.env, ...config.env },
        stdio: ['pipe', 'pipe', 'pipe'],
      });

      this.processes.set(serverName, childProcess);

      childProcess.on('error', (error) => {
        this.emit('server:error', serverName, error);
      });

      childProcess.on('exit', (code) => {
        this.clients.delete(serverName);
        this.processes.delete(serverName);
        this.emit('server:disconnected', serverName, 
          code !== 0 ? new Error(`Process exited with code ${code}`) : undefined
        );
      });

      // Redirect stderr for debugging (don't mix with JSON-RPC)
      childProcess.stderr?.on('data', (data) => {
        console.error(`[MCP:${serverName}] ${data.toString()}`);
      });

      transport = new StdioClientTransport({
        command: config.command,
        args: config.args,
        env: config.env,
      });
    } else if (config.type === 'sse' || config.type === 'http') {
      if (!config.url) {
        throw new Error(`HTTP/SSE server requires URL: ${serverName}`);
      }

      transport = new SSEClientTransport(new URL(config.url));
    } else {
      throw new Error(`Unknown transport type: ${config.type}`);
    }

    await client.connect(transport);
    this.clients.set(serverName, client);

    // Discover tools and resources
    await this.discoverCapabilities(serverName);

    this.emit('server:connected', serverName);
  }

  /**
   * Disconnect from an MCP server
   */
  async disconnect(serverName: string): Promise<void> {
    const client = this.clients.get(serverName);
    if (client) {
      await client.close();
      this.clients.delete(serverName);
    }

    const proc = this.processes.get(serverName);
    if (proc) {
      proc.kill();
      this.processes.delete(serverName);
    }

    this.tools.delete(serverName);
    this.resources.delete(serverName);
    this.emit('server:disconnected', serverName);
  }

  /**
   * Disconnect from all servers
   */
  async disconnectAll(): Promise<void> {
    const servers = Array.from(this.clients.keys());
    await Promise.all(servers.map(s => this.disconnect(s)));
  }

  /**
   * Discover tools and resources from a connected server
   */
  private async discoverCapabilities(serverName: string): Promise<void> {
    const client = this.clients.get(serverName);
    if (!client) return;

    try {
      // Discover tools
      const toolsResponse = await client.listTools();
      const tools: MCPTool[] = toolsResponse.tools.map(t => ({
        name: t.name,
        description: t.description,
        inputSchema: t.inputSchema as Record<string, unknown>,
        serverName,
      }));
      this.tools.set(serverName, tools);

      // Discover resources
      const resourcesResponse = await client.listResources();
      const resources: MCPResource[] = resourcesResponse.resources.map(r => ({
        uri: r.uri,
        name: r.name,
        description: r.description,
        mimeType: r.mimeType,
        serverName,
      }));
      this.resources.set(serverName, resources);
    } catch (error) {
      console.error(`Failed to discover capabilities for ${serverName}:`, error);
    }
  }

  /**
   * Get all available tools across all connected servers
   */
  getAllTools(): MCPTool[] {
    const allTools: MCPTool[] = [];
    for (const tools of this.tools.values()) {
      allTools.push(...tools);
    }
    return allTools;
  }

  /**
   * Get all available resources across all connected servers
   */
  getAllResources(): MCPResource[] {
    const allResources: MCPResource[] = [];
    for (const resources of this.resources.values()) {
      allResources.push(...resources);
    }
    return allResources;
  }

  /**
   * Find a tool by name (returns first match)
   */
  findTool(toolName: string): MCPTool | undefined {
    for (const tools of this.tools.values()) {
      const tool = tools.find(t => t.name === toolName);
      if (tool) return tool;
    }
    return undefined;
  }

  /**
   * Execute a tool
   */
  async executeTool(
    toolName: string,
    args: Record<string, unknown>,
    serverName?: string
  ): Promise<ToolExecutionResult> {
    // Find the tool
    let tool: MCPTool | undefined;
    let targetServer: string;

    if (serverName) {
      const serverTools = this.tools.get(serverName);
      tool = serverTools?.find(t => t.name === toolName);
      targetServer = serverName;
    } else {
      tool = this.findTool(toolName);
      targetServer = tool?.serverName || '';
    }

    if (!tool) {
      return {
        success: false,
        content: [{ type: 'text', text: `Tool not found: ${toolName}` }],
        isError: true,
      };
    }

    const client = this.clients.get(targetServer);
    if (!client) {
      return {
        success: false,
        content: [{ type: 'text', text: `Server not connected: ${targetServer}` }],
        isError: true,
      };
    }

    try {
      const result = await client.callTool({ name: toolName, arguments: args });

      const executionResult: ToolExecutionResult = {
        success: !result.isError,
        content: result.content as ToolExecutionResult['content'],
        isError: result.isError,
      };

      this.emit('tool:executed', targetServer, toolName, executionResult);
      return executionResult;
    } catch (error) {
      const errorResult: ToolExecutionResult = {
        success: false,
        content: [{ type: 'text', text: `Tool execution failed: ${error}` }],
        isError: true,
      };

      this.emit('tool:executed', targetServer, toolName, errorResult);
      return errorResult;
    }
  }

  /**
   * Read a resource
   */
  async readResource(uri: string, serverName?: string): Promise<string> {
    let targetServer: string | undefined = serverName;

    if (!targetServer) {
      // Find server that has this resource
      for (const [server, resources] of this.resources.entries()) {
        if (resources.some(r => r.uri === uri)) {
          targetServer = server;
          break;
        }
      }
    }

    if (!targetServer) {
      throw new Error(`Resource not found: ${uri}`);
    }

    const client = this.clients.get(targetServer);
    if (!client) {
      throw new Error(`Server not connected: ${targetServer}`);
    }

    const result = await client.readResource({ uri });
    
    // Extract text content
    const textContent = result.contents
      .filter(c => c.text)
      .map(c => c.text)
      .join('\n');

    return textContent;
  }

  /**
   * Check if a server is connected
   */
  isConnected(serverName: string): boolean {
    return this.clients.has(serverName);
  }

  /**
   * Get list of connected servers
   */
  getConnectedServers(): string[] {
    return Array.from(this.clients.keys());
  }

  /**
   * Get server configuration
   */
  getServerConfig(serverName: string): MCPServerConfig | undefined {
    return this.configs.get(serverName);
  }

  /**
   * Get all registered server configurations
   */
  getAllServerConfigs(): MCPServerConfig[] {
    return Array.from(this.configs.values());
  }
}

// Built-in server configurations
export const BUILTIN_SERVERS: MCPServerConfig[] = [
  {
    name: 'filesystem',
    type: 'stdio',
    command: 'npx',
    args: ['-y', '@modelcontextprotocol/server-filesystem', process.cwd()],
    enabled: true,
  },
  {
    name: 'git',
    type: 'stdio',
    command: 'npx',
    args: ['-y', '@modelcontextprotocol/server-git', '--repository', process.cwd()],
    enabled: false,
  },
  {
    name: 'memory',
    type: 'stdio',
    command: 'npx',
    args: ['-y', '@modelcontextprotocol/server-memory'],
    enabled: false,
  },
];

// Singleton instance
let defaultManager: MCPClientManager | null = null;

export function getMCPManager(): MCPClientManager {
  if (!defaultManager) {
    defaultManager = new MCPClientManager();
    
    // Register built-in servers
    for (const config of BUILTIN_SERVERS) {
      defaultManager.registerServer(config);
    }
  }
  return defaultManager;
}

export async function closeMCPManager(): Promise<void> {
  if (defaultManager) {
    await defaultManager.disconnectAll();
    defaultManager = null;
  }
}
