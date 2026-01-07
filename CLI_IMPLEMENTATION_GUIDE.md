# Monkey Coder CLI - Technical Implementation Guide

## Overview

This guide provides detailed technical specifications for implementing the enhancements outlined in the CLI Feature Comparison document. It includes code samples, architecture patterns, and best practices.

---

## Table of Contents

1. [Command System Enhancement](#1-command-system-enhancement)
2. [Interactive UI Framework](#2-interactive-ui-framework)
3. [Extension System](#3-extension-system)
4. [Session Management](#4-session-management)
5. [Tool Execution & Safety](#5-tool-execution--safety)
6. [Git Integration](#6-git-integration)
7. [Configuration System](#7-configuration-system)
8. [Testing Infrastructure](#8-testing-infrastructure)

---

## 1. Command System Enhancement

### 1.1 Hierarchical Command Structure

**Current Structure:**
```typescript
// Flat command structure
program.command('implement')
program.command('analyze')
program.command('build')
program.command('test')
```

**Enhanced Structure:**
```typescript
// packages/cli/src/commands/registry.ts
export interface CommandDefinition {
  name: string;
  aliases?: string[];
  description: string;
  category: 'core' | 'git' | 'project' | 'config' | 'extension';
  subcommands?: CommandDefinition[];
  options?: CommandOption[];
  handler: CommandHandler;
  examples?: string[];
}

export const commandRegistry: CommandDefinition[] = [
  {
    name: 'repo',
    category: 'core',
    description: 'Manage repositories',
    subcommands: [
      {
        name: 'create',
        description: 'Create a new repository',
        options: [
          { name: 'name', required: true, description: 'Repository name' },
          { name: 'private', type: 'boolean', description: 'Make private' },
          { name: 'description', type: 'string', description: 'Description' }
        ],
        handler: repoCreateHandler,
        examples: [
          'monkey repo create my-project --private',
          'monkey repo create my-app --description "My app"'
        ]
      },
      {
        name: 'clone',
        description: 'Clone a repository',
        options: [
          { name: 'url', required: true, description: 'Repository URL' },
          { name: 'directory', type: 'string', description: 'Target directory' }
        ],
        handler: repoCloneHandler
      }
    ]
  },
  {
    name: 'git',
    category: 'git',
    description: 'Git operations',
    subcommands: [
      { name: 'commit', handler: gitCommitHandler },
      { name: 'branch', handler: gitBranchHandler },
      { name: 'status', handler: gitStatusHandler }
    ]
  }
];
```

### 1.2 Command Builder Pattern

```typescript
// packages/cli/src/commands/builder.ts
import { Command } from 'commander';

export class CommandBuilder {
  private program: Command;

  constructor(program: Command) {
    this.program = program;
  }

  registerCommands(definitions: CommandDefinition[]): void {
    for (const def of definitions) {
      this.registerCommand(def, this.program);
    }
  }

  private registerCommand(
    def: CommandDefinition,
    parent: Command
  ): Command {
    const cmd = parent
      .command(def.name)
      .description(def.description);

    // Add aliases
    if (def.aliases) {
      def.aliases.forEach(alias => cmd.alias(alias));
    }

    // Add options
    if (def.options) {
      def.options.forEach(opt => {
        const flags = this.buildOptionFlags(opt);
        cmd.option(flags, opt.description, opt.default);
      });
    }

    // Add examples
    if (def.examples) {
      cmd.addHelpText('after', '\nExamples:\n' + 
        def.examples.map(ex => `  ${ex}`).join('\n')
      );
    }

    // Register subcommands recursively
    if (def.subcommands) {
      def.subcommands.forEach(sub => 
        this.registerCommand(sub, cmd)
      );
    } else {
      // Leaf command - attach handler
      cmd.action(async (...args) => {
        try {
          await def.handler(...args);
        } catch (error) {
          this.handleError(error);
        }
      });
    }

    return cmd;
  }

  private buildOptionFlags(opt: CommandOption): string {
    const short = opt.short ? `-${opt.short}, ` : '';
    const long = `--${opt.name}`;
    const arg = opt.required ? ` <${opt.name}>` : 
                opt.type !== 'boolean' ? ` [${opt.name}]` : '';
    return short + long + arg;
  }

  private handleError(error: any): void {
    if (error instanceof UserError) {
      console.error(chalk.red(error.message));
      if (error.hint) {
        console.error(chalk.yellow(`Hint: ${error.hint}`));
      }
    } else {
      console.error(chalk.red('An unexpected error occurred:'));
      console.error(error);
    }
    process.exit(1);
  }
}
```

### 1.3 Alias System

```typescript
// packages/cli/src/commands/aliases.ts
export interface AliasDefinition {
  name: string;
  expansion: string;
  description?: string;
}

export class AliasManager {
  private aliases: Map<string, AliasDefinition>;
  private config: ConfigManager;

  constructor(config: ConfigManager) {
    this.config = config;
    this.aliases = new Map();
    this.loadAliases();
  }

  async add(name: string, expansion: string, description?: string): Promise<void> {
    // Validate alias name
    if (!this.isValidAliasName(name)) {
      throw new Error(`Invalid alias name: ${name}`);
    }

    // Validate expansion
    if (!this.isValidExpansion(expansion)) {
      throw new Error(`Invalid alias expansion: ${expansion}`);
    }

    const alias: AliasDefinition = { name, expansion, description };
    this.aliases.set(name, alias);
    
    await this.saveAliases();
    console.log(chalk.green(`✓ Alias '${name}' created`));
  }

  async remove(name: string): Promise<void> {
    if (!this.aliases.has(name)) {
      throw new Error(`Alias '${name}' not found`);
    }

    this.aliases.delete(name);
    await this.saveAliases();
    console.log(chalk.green(`✓ Alias '${name}' removed`));
  }

  list(): AliasDefinition[] {
    return Array.from(this.aliases.values());
  }

  expand(name: string): string | undefined {
    return this.aliases.get(name)?.expansion;
  }

  private async loadAliases(): Promise<void> {
    const config = await this.config.get('aliases', {});
    for (const [name, def] of Object.entries(config)) {
      this.aliases.set(name, def as AliasDefinition);
    }
  }

  private async saveAliases(): Promise<void> {
    const aliasesObj = Object.fromEntries(this.aliases);
    await this.config.set('aliases', aliasesObj);
  }

  private isValidAliasName(name: string): boolean {
    return /^[a-z][a-z0-9-]*$/i.test(name);
  }

  private isValidExpansion(expansion: string): boolean {
    // Check if expansion references existing command
    return expansion.length > 0;
  }
}

// Usage example
// monkey alias add co "pr checkout"
// monkey co 123  // Expands to: monkey pr checkout 123
```

---

## 2. Interactive UI Framework

### 2.1 Interactive Prompt System

```typescript
// packages/cli/src/ui/prompts.ts
import inquirer from 'inquirer';
import chalk from 'chalk';

export class InteractivePrompt {
  async confirm(message: string, defaultValue = false): Promise<boolean> {
    const { confirmed } = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'confirmed',
        message,
        default: defaultValue
      }
    ]);
    return confirmed;
  }

  async select<T>(
    message: string,
    choices: Array<{ name: string; value: T; description?: string }>
  ): Promise<T> {
    const { selected } = await inquirer.prompt([
      {
        type: 'list',
        name: 'selected',
        message,
        choices: choices.map(c => ({
          name: c.description ? 
            `${c.name} ${chalk.gray(c.description)}` : 
            c.name,
          value: c.value
        }))
      }
    ]);
    return selected;
  }

  async multiSelect<T>(
    message: string,
    choices: Array<{ name: string; value: T; checked?: boolean }>
  ): Promise<T[]> {
    const { selected } = await inquirer.prompt([
      {
        type: 'checkbox',
        name: 'selected',
        message,
        choices: choices.map(c => ({
          name: c.name,
          value: c.value,
          checked: c.checked || false
        }))
      }
    ]);
    return selected;
  }

  async input(
    message: string,
    options: {
      default?: string;
      validate?: (input: string) => boolean | string;
      transform?: (input: string) => string;
    } = {}
  ): Promise<string> {
    const { input } = await inquirer.prompt([
      {
        type: 'input',
        name: 'input',
        message,
        default: options.default,
        validate: options.validate,
        filter: options.transform
      }
    ]);
    return input;
  }

  async editor(message: string, defaultValue?: string): Promise<string> {
    const { content } = await inquirer.prompt([
      {
        type: 'editor',
        name: 'content',
        message,
        default: defaultValue
      }
    ]);
    return content;
  }

  async autocomplete<T>(
    message: string,
    source: (input: string) => Promise<Array<{ name: string; value: T }>>
  ): Promise<T> {
    const inquirerAutocomplete = require('inquirer-autocomplete-prompt');
    inquirer.registerPrompt('autocomplete', inquirerAutocomplete);

    const { selected } = await inquirer.prompt([
      {
        type: 'autocomplete',
        name: 'selected',
        message,
        source: async (_: any, input: string) => {
          const results = await source(input || '');
          return results.map(r => ({ name: r.name, value: r.value }));
        }
      }
    ]);
    return selected;
  }
}
```

### 2.2 Progress Indicators

```typescript
// packages/cli/src/ui/progress.ts
import ora, { Ora } from 'ora';
import chalk from 'chalk';

export class ProgressManager {
  private spinner?: Ora;
  private tasks: Map<string, { total: number; current: number }>;

  constructor() {
    this.tasks = new Map();
  }

  start(message: string): void {
    this.spinner = ora({
      text: message,
      color: 'cyan'
    }).start();
  }

  update(message: string): void {
    if (this.spinner) {
      this.spinner.text = message;
    }
  }

  succeed(message?: string): void {
    if (this.spinner) {
      this.spinner.succeed(message);
      this.spinner = undefined;
    }
  }

  fail(message?: string): void {
    if (this.spinner) {
      this.spinner.fail(message);
      this.spinner = undefined;
    }
  }

  warn(message: string): void {
    if (this.spinner) {
      this.spinner.warn(message);
      this.spinner = undefined;
    }
  }

  info(message: string): void {
    if (this.spinner) {
      this.spinner.info(message);
      this.spinner = undefined;
    }
  }

  startTask(id: string, total: number): void {
    this.tasks.set(id, { total, current: 0 });
    this.updateTaskProgress(id);
  }

  updateTask(id: string, current: number): void {
    const task = this.tasks.get(id);
    if (task) {
      task.current = current;
      this.updateTaskProgress(id);
    }
  }

  completeTask(id: string): void {
    const task = this.tasks.get(id);
    if (task) {
      task.current = task.total;
      this.updateTaskProgress(id);
      this.tasks.delete(id);
    }
  }

  private updateTaskProgress(id: string): void {
    const task = this.tasks.get(id);
    if (!task || !this.spinner) return;

    const percentage = Math.round((task.current / task.total) * 100);
    const bar = this.createProgressBar(percentage);
    this.spinner.text = `${id}: ${bar} ${percentage}%`;
  }

  private createProgressBar(percentage: number, width = 20): string {
    const filled = Math.round((percentage / 100) * width);
    const empty = width - filled;
    return chalk.green('█'.repeat(filled)) + 
           chalk.gray('░'.repeat(empty));
  }
}
```

### 2.3 Diff Viewer

```typescript
// packages/cli/src/ui/diff-viewer.ts
import chalk from 'chalk';
import { diffLines } from 'diff';

export class DiffViewer {
  async show(
    oldContent: string,
    newContent: string,
    options: {
      filename?: string;
      context?: number;
      interactive?: boolean;
    } = {}
  ): Promise<boolean> {
    const diff = diffLines(oldContent, newContent);
    
    console.log(chalk.bold(`\n${options.filename || 'Changes'}:\n`));
    
    let lineNumber = 1;
    for (const part of diff) {
      const color = part.added ? chalk.green :
                    part.removed ? chalk.red :
                    chalk.gray;
      
      const prefix = part.added ? '+ ' :
                     part.removed ? '- ' :
                     '  ';
      
      const lines = part.value.split('\n').filter(l => l);
      for (const line of lines) {
        console.log(color(`${prefix}${lineNumber.toString().padStart(4)} | ${line}`));
        if (!part.removed) lineNumber++;
      }
    }

    if (options.interactive) {
      const prompt = new InteractivePrompt();
      return await prompt.confirm('\nApply these changes?', true);
    }

    return true;
  }

  showSummary(
    files: Array<{ path: string; additions: number; deletions: number }>
  ): void {
    console.log(chalk.bold('\nSummary:\n'));
    
    for (const file of files) {
      const additions = chalk.green(`+${file.additions}`);
      const deletions = chalk.red(`-${file.deletions}`);
      console.log(`  ${file.path} ${additions} ${deletions}`);
    }

    const totalAdditions = files.reduce((sum, f) => sum + f.additions, 0);
    const totalDeletions = files.reduce((sum, f) => sum + f.deletions, 0);
    
    console.log(chalk.bold(
      `\nTotal: ${chalk.green(`+${totalAdditions}`)} ${chalk.red(`-${totalDeletions}`)}`
    ));
  }
}
```

---

## 3. Extension System

### 3.1 Extension Interface

```typescript
// packages/cli/src/extensions/types.ts
import { Command } from 'commander';

export interface Extension {
  name: string;
  version: string;
  description: string;
  author?: string;
  homepage?: string;
  
  // Lifecycle hooks
  activate?(context: ExtensionContext): Promise<void>;
  deactivate?(): Promise<void>;
  
  // Command contributions
  commands?: ExtensionCommand[];
  
  // Tool contributions
  tools?: ExtensionTool[];
  
  // Configuration
  config?: ExtensionConfig;
}

export interface ExtensionContext {
  // API access
  api: MonkeyCoderAPI;
  
  // Configuration
  config: ExtensionConfigManager;
  
  // Storage
  storage: ExtensionStorage;
  
  // Logging
  logger: Logger;
  
  // UI
  ui: {
    showMessage(message: string, type?: 'info' | 'warning' | 'error'): void;
    showProgress(title: string, task: () => Promise<void>): Promise<void>;
  };
}

export interface ExtensionCommand {
  name: string;
  description: string;
  usage?: string;
  options?: CommandOption[];
  handler: (args: any, options: any, context: ExtensionContext) => Promise<void>;
}

export interface ExtensionTool {
  name: string;
  description: string;
  inputSchema: {
    type: 'object';
    properties: Record<string, any>;
    required?: string[];
  };
  handler: (input: any, context: ExtensionContext) => Promise<any>;
  requiresApproval?: boolean;
}
```

### 3.2 Extension Manager

```typescript
// packages/cli/src/extensions/manager.ts
import { Extension, ExtensionContext } from './types';
import * as fs from 'fs-extra';
import * as path from 'path';

export class ExtensionManager {
  private extensions: Map<string, Extension>;
  private extensionsPath: string;
  private context: ExtensionContext;

  constructor(extensionsPath: string, context: ExtensionContext) {
    this.extensionsPath = extensionsPath;
    this.context = context;
    this.extensions = new Map();
  }

  async loadExtensions(): Promise<void> {
    const extensionDirs = await fs.readdir(this.extensionsPath);
    
    for (const dir of extensionDirs) {
      try {
        await this.loadExtension(dir);
      } catch (error) {
        console.error(`Failed to load extension ${dir}:`, error);
      }
    }
  }

  private async loadExtension(name: string): Promise<void> {
    const extensionPath = path.join(this.extensionsPath, name);
    const packageJsonPath = path.join(extensionPath, 'package.json');
    
    // Read package.json
    const packageJson = await fs.readJson(packageJsonPath);
    
    // Load extension module
    const mainFile = packageJson.main || 'index.js';
    const extensionModule = require(path.join(extensionPath, mainFile));
    
    const extension: Extension = extensionModule.default || extensionModule;
    
    // Validate extension
    this.validateExtension(extension);
    
    // Activate extension
    if (extension.activate) {
      await extension.activate(this.context);
    }
    
    // Store extension
    this.extensions.set(name, extension);
    
    console.log(chalk.green(`✓ Loaded extension: ${name}`));
  }

  async installExtension(nameOrPath: string): Promise<void> {
    const progress = new ProgressManager();
    progress.start(`Installing extension: ${nameOrPath}`);
    
    try {
      // Determine if it's a npm package or local path
      const isLocal = await fs.pathExists(nameOrPath);
      
      if (isLocal) {
        await this.installLocalExtension(nameOrPath);
      } else {
        await this.installNpmExtension(nameOrPath);
      }
      
      progress.succeed(`Extension installed: ${nameOrPath}`);
    } catch (error) {
      progress.fail(`Failed to install extension: ${error.message}`);
      throw error;
    }
  }

  async uninstallExtension(name: string): Promise<void> {
    const extension = this.extensions.get(name);
    if (!extension) {
      throw new Error(`Extension not found: ${name}`);
    }

    // Deactivate extension
    if (extension.deactivate) {
      await extension.deactivate();
    }

    // Remove from disk
    const extensionPath = path.join(this.extensionsPath, name);
    await fs.remove(extensionPath);

    // Remove from registry
    this.extensions.delete(name);

    console.log(chalk.green(`✓ Uninstalled extension: ${name}`));
  }

  listExtensions(): Extension[] {
    return Array.from(this.extensions.values());
  }

  getExtension(name: string): Extension | undefined {
    return this.extensions.get(name);
  }

  private validateExtension(extension: Extension): void {
    if (!extension.name) {
      throw new Error('Extension must have a name');
    }
    if (!extension.version) {
      throw new Error('Extension must have a version');
    }
  }

  private async installNpmExtension(packageName: string): Promise<void> {
    const { exec } = require('child_process');
    const { promisify } = require('util');
    const execAsync = promisify(exec);
    
    const targetPath = path.join(this.extensionsPath, packageName);
    
    // Create temp directory
    const tempDir = path.join(this.extensionsPath, '.temp');
    await fs.ensureDir(tempDir);
    
    try {
      // Install package
      await execAsync(`npm install ${packageName}`, { cwd: tempDir });
      
      // Move to extensions directory
      const installedPath = path.join(tempDir, 'node_modules', packageName);
      await fs.move(installedPath, targetPath);
      
      // Load the extension
      await this.loadExtension(packageName);
    } finally {
      // Cleanup temp directory
      await fs.remove(tempDir);
    }
  }

  private async installLocalExtension(sourcePath: string): Promise<void> {
    const packageJson = await fs.readJson(path.join(sourcePath, 'package.json'));
    const name = packageJson.name;
    const targetPath = path.join(this.extensionsPath, name);
    
    // Copy extension
    await fs.copy(sourcePath, targetPath);
    
    // Install dependencies
    const { exec } = require('child_process');
    const { promisify } = require('util');
    const execAsync = promisify(exec);
    
    await execAsync('npm install', { cwd: targetPath });
    
    // Load the extension
    await this.loadExtension(name);
  }
}
```

### 3.3 MCP Protocol Support

```typescript
// packages/cli/src/mcp/client.ts
export interface MCPServerConfig {
  name: string;
  command: string;
  args?: string[];
  env?: Record<string, string>;
  cwd?: string;
  timeout?: number;
  trust?: boolean;
}

export interface MCPTool {
  name: string;
  description: string;
  inputSchema: any;
  annotations?: {
    readOnly?: boolean;
    requiresApproval?: boolean;
  };
}

export class MCPClient {
  private servers: Map<string, MCPServerConnection>;

  constructor() {
    this.servers = new Map();
  }

  async connect(config: MCPServerConfig): Promise<void> {
    const connection = new MCPServerConnection(config);
    await connection.start();
    
    // Discover tools
    const tools = await connection.listTools();
    console.log(`Discovered ${tools.length} tools from ${config.name}`);
    
    this.servers.set(config.name, connection);
  }

  async disconnect(name: string): Promise<void> {
    const connection = this.servers.get(name);
    if (connection) {
      await connection.stop();
      this.servers.delete(name);
    }
  }

  async callTool(
    serverName: string,
    toolName: string,
    args: any
  ): Promise<any> {
    const connection = this.servers.get(serverName);
    if (!connection) {
      throw new Error(`MCP server not connected: ${serverName}`);
    }

    return await connection.callTool(toolName, args);
  }

  listServers(): string[] {
    return Array.from(this.servers.keys());
  }

  async listTools(serverName?: string): Promise<MCPTool[]> {
    if (serverName) {
      const connection = this.servers.get(serverName);
      return connection ? await connection.listTools() : [];
    }

    // List tools from all servers
    const allTools: MCPTool[] = [];
    for (const [name, connection] of this.servers) {
      const tools = await connection.listTools();
      // Prefix tool names with server name to avoid conflicts
      allTools.push(...tools.map(t => ({
        ...t,
        name: `${name}__${t.name}`
      })));
    }
    return allTools;
  }
}

class MCPServerConnection {
  private config: MCPServerConfig;
  private process?: ChildProcess;
  private tools: MCPTool[];

  constructor(config: MCPServerConfig) {
    this.config = config;
    this.tools = [];
  }

  async start(): Promise<void> {
    const { spawn } = require('child_process');
    
    this.process = spawn(this.config.command, this.config.args || [], {
      cwd: this.config.cwd,
      env: { ...process.env, ...this.config.env },
      stdio: ['pipe', 'pipe', 'pipe']
    });

    // Wait for server to be ready
    await this.waitForReady();
  }

  async stop(): Promise<void> {
    if (this.process) {
      this.process.kill();
      this.process = undefined;
    }
  }

  async listTools(): Promise<MCPTool[]> {
    const response = await this.sendRequest({
      jsonrpc: '2.0',
      id: 1,
      method: 'tools/list'
    });
    
    this.tools = response.result.tools;
    return this.tools;
  }

  async callTool(name: string, args: any): Promise<any> {
    const response = await this.sendRequest({
      jsonrpc: '2.0',
      id: 2,
      method: 'tools/call',
      params: {
        name,
        arguments: args
      }
    });
    
    return response.result;
  }

  private async sendRequest(request: any): Promise<any> {
    return new Promise((resolve, reject) => {
      if (!this.process) {
        reject(new Error('MCP server not started'));
        return;
      }

      const requestStr = JSON.stringify(request) + '\n';
      this.process.stdin?.write(requestStr);

      const timeout = setTimeout(() => {
        reject(new Error('MCP request timeout'));
      }, this.config.timeout || 30000);

      this.process.stdout?.once('data', (data) => {
        clearTimeout(timeout);
        try {
          const response = JSON.parse(data.toString());
          if (response.error) {
            reject(new Error(response.error.message));
          } else {
            resolve(response);
          }
        } catch (error) {
          reject(error);
        }
      });
    });
  }

  private async waitForReady(): Promise<void> {
    // Send initialize request
    await this.sendRequest({
      jsonrpc: '2.0',
      id: 0,
      method: 'initialize',
      params: {
        protocolVersion: '1.0',
        capabilities: {},
        clientInfo: {
          name: 'monkey-coder-cli',
          version: '1.0.0'
        }
      }
    });
  }
}
```

---

## 4. Session Management

### 4.1 Session Storage

```typescript
// packages/cli/src/session/manager.ts
import * as fs from 'fs-extra';
import * as path from 'path';
import { v4 as uuidv4 } from 'uuid';

export interface Session {
  id: string;
  name?: string;
  created: Date;
  updated: Date;
  messages: Message[];
  context: SessionContext;
  checkpoints: Checkpoint[];
}

export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  metadata?: Record<string, any>;
}

export interface SessionContext {
  workingDirectory: string;
  gitBranch?: string;
  files: string[];
  memory: MemoryItem[];
  environment: Record<string, string>;
}

export interface MemoryItem {
  key: string;
  value: string;
  timestamp: Date;
}

export interface Checkpoint {
  id: string;
  timestamp: Date;
  description: string;
  fileStates: FileState[];
}

export interface FileState {
  path: string;
  content: string;
  mode: number;
}

export class SessionManager {
  private sessionsPath: string;
  private currentSession?: Session;

  constructor(sessionsPath: string) {
    this.sessionsPath = sessionsPath;
  }

  async createSession(name?: string): Promise<Session> {
    const session: Session = {
      id: uuidv4(),
      name,
      created: new Date(),
      updated: new Date(),
      messages: [],
      context: {
        workingDirectory: process.cwd(),
        gitBranch: await this.getCurrentGitBranch(),
        files: [],
        memory: [],
        environment: {}
      },
      checkpoints: []
    };

    await this.saveSession(session);
    this.currentSession = session;
    
    return session;
  }

  async loadSession(id: string): Promise<Session> {
    const sessionPath = path.join(this.sessionsPath, `${id}.json`);
    const session = await fs.readJson(sessionPath);
    
    // Restore dates
    session.created = new Date(session.created);
    session.updated = new Date(session.updated);
    session.messages = session.messages.map((m: any) => ({
      ...m,
      timestamp: new Date(m.timestamp)
    }));
    
    this.currentSession = session;
    return session;
  }

  async saveSession(session: Session): Promise<void> {
    session.updated = new Date();
    const sessionPath = path.join(this.sessionsPath, `${session.id}.json`);
    await fs.ensureDir(this.sessionsPath);
    await fs.writeJson(sessionPath, session, { spaces: 2 });
  }

  async listSessions(): Promise<Session[]> {
    await fs.ensureDir(this.sessionsPath);
    const files = await fs.readdir(this.sessionsPath);
    const sessions: Session[] = [];

    for (const file of files) {
      if (file.endsWith('.json')) {
        const sessionPath = path.join(this.sessionsPath, file);
        const session = await fs.readJson(sessionPath);
        sessions.push(session);
      }
    }

    return sessions.sort((a, b) => 
      new Date(b.updated).getTime() - new Date(a.updated).getTime()
    );
  }

  async deleteSession(id: string): Promise<void> {
    const sessionPath = path.join(this.sessionsPath, `${id}.json`);
    await fs.remove(sessionPath);
    
    if (this.currentSession?.id === id) {
      this.currentSession = undefined;
    }
  }

  async addMessage(
    role: 'user' | 'assistant' | 'system',
    content: string,
    metadata?: Record<string, any>
  ): Promise<void> {
    if (!this.currentSession) {
      throw new Error('No active session');
    }

    const message: Message = {
      role,
      content,
      timestamp: new Date(),
      metadata
    };

    this.currentSession.messages.push(message);
    await this.saveSession(this.currentSession);
  }

  async addMemory(key: string, value: string): Promise<void> {
    if (!this.currentSession) {
      throw new Error('No active session');
    }

    const memory: MemoryItem = {
      key,
      value,
      timestamp: new Date()
    };

    this.currentSession.context.memory.push(memory);
    await this.saveSession(this.currentSession);
  }

  async createCheckpoint(description: string): Promise<Checkpoint> {
    if (!this.currentSession) {
      throw new Error('No active session');
    }

    const files = this.currentSession.context.files;
    const fileStates: FileState[] = [];

    for (const filePath of files) {
      try {
        const content = await fs.readFile(filePath, 'utf-8');
        const stats = await fs.stat(filePath);
        fileStates.push({
          path: filePath,
          content,
          mode: stats.mode
        });
      } catch (error) {
        console.warn(`Failed to backup file: ${filePath}`);
      }
    }

    const checkpoint: Checkpoint = {
      id: uuidv4(),
      timestamp: new Date(),
      description,
      fileStates
    };

    this.currentSession.checkpoints.push(checkpoint);
    await this.saveSession(this.currentSession);

    return checkpoint;
  }

  async restoreCheckpoint(checkpointId: string): Promise<void> {
    if (!this.currentSession) {
      throw new Error('No active session');
    }

    const checkpoint = this.currentSession.checkpoints.find(
      c => c.id === checkpointId
    );

    if (!checkpoint) {
      throw new Error(`Checkpoint not found: ${checkpointId}`);
    }

    // Restore files
    for (const fileState of checkpoint.fileStates) {
      await fs.ensureDir(path.dirname(fileState.path));
      await fs.writeFile(fileState.path, fileState.content);
      await fs.chmod(fileState.path, fileState.mode);
    }

    console.log(chalk.green(`✓ Restored checkpoint: ${checkpoint.description}`));
  }

  getCurrentSession(): Session | undefined {
    return this.currentSession;
  }

  private async getCurrentGitBranch(): Promise<string | undefined> {
    try {
      const { exec } = require('child_process');
      const { promisify } = require('util');
      const execAsync = promisify(exec);
      
      const { stdout } = await execAsync('git branch --show-current');
      return stdout.trim();
    } catch {
      return undefined;
    }
  }
}
```

---

## 5. Tool Execution & Safety

### 5.1 Safe Tool Executor

```typescript
// packages/cli/src/tools/executor.ts
export interface ToolDefinition {
  name: string;
  description: string;
  inputSchema: any;
  handler: (input: any) => Promise<any>;
  safety: {
    readOnly: boolean;
    requiresApproval: boolean;
    dangerous: boolean;
  };
}

export class ToolExecutor {
  private tools: Map<string, ToolDefinition>;
  private sessionManager: SessionManager;
  private prompt: InteractivePrompt;

  constructor(sessionManager: SessionManager) {
    this.tools = new Map();
    this.sessionManager = sessionManager;
    this.prompt = new InteractivePrompt();
  }

  registerTool(tool: ToolDefinition): void {
    this.tools.set(tool.name, tool);
  }

  async executeTool(
    name: string,
    input: any,
    options: {
      autoApprove?: boolean;
      createCheckpoint?: boolean;
    } = {}
  ): Promise<any> {
    const tool = this.tools.get(name);
    if (!tool) {
      throw new Error(`Tool not found: ${name}`);
    }

    // Check if approval is needed
    if (tool.safety.requiresApproval && !options.autoApprove) {
      const approved = await this.requestApproval(tool, input);
      if (!approved) {
        throw new Error('Tool execution cancelled by user');
      }
    }

    // Create checkpoint before executing dangerous tools
    if (tool.safety.dangerous && options.createCheckpoint !== false) {
      await this.sessionManager.createCheckpoint(
        `Before executing ${tool.name}`
      );
    }

    try {
      // Execute tool
      const result = await tool.handler(input);
      return result;
    } catch (error) {
      // Log error
      console.error(chalk.red(`Tool execution failed: ${tool.name}`));
      console.error(error);
      throw error;
    }
  }

  private async requestApproval(
    tool: ToolDefinition,
    input: any
  ): Promise<boolean> {
    console.log(chalk.yellow(`\n⚠️  Tool execution requires approval:\n`));
    console.log(chalk.bold(`Tool: ${tool.name}`));
    console.log(`Description: ${tool.description}`);
    console.log(`\nInput:`);
    console.log(JSON.stringify(input, null, 2));

    if (tool.safety.dangerous) {
      console.log(chalk.red('\n⚠️  This tool can make dangerous changes!'));
    }

    return await this.prompt.confirm('\nProceed with execution?', false);
  }
}
```

### 5.2 Built-in Tools

```typescript
// packages/cli/src/tools/built-in/file-tools.ts
export const readFileTool: ToolDefinition = {
  name: 'read_file',
  description: 'Read contents of a file',
  inputSchema: {
    type: 'object',
    properties: {
      path: { type: 'string', description: 'File path to read' }
    },
    required: ['path']
  },
  handler: async (input: { path: string }) => {
    const content = await fs.readFile(input.path, 'utf-8');
    return { content, path: input.path };
  },
  safety: {
    readOnly: true,
    requiresApproval: false,
    dangerous: false
  }
};

export const writeFileTool: ToolDefinition = {
  name: 'write_file',
  description: 'Write content to a file',
  inputSchema: {
    type: 'object',
    properties: {
      path: { type: 'string', description: 'File path to write' },
      content: { type: 'string', description: 'Content to write' }
    },
    required: ['path', 'content']
  },
  handler: async (input: { path: string; content: string }) => {
    // Show diff before writing
    const diffViewer = new DiffViewer();
    let oldContent = '';
    
    if (await fs.pathExists(input.path)) {
      oldContent = await fs.readFile(input.path, 'utf-8');
    }

    const approved = await diffViewer.show(oldContent, input.content, {
      filename: input.path,
      interactive: true
    });

    if (approved) {
      await fs.ensureDir(path.dirname(input.path));
      await fs.writeFile(input.path, input.content);
      return { success: true, path: input.path };
    } else {
      throw new Error('File write cancelled by user');
    }
  },
  safety: {
    readOnly: false,
    requiresApproval: true,
    dangerous: false
  }
};

export const deleteFileTool: ToolDefinition = {
  name: 'delete_file',
  description: 'Delete a file',
  inputSchema: {
    type: 'object',
    properties: {
      path: { type: 'string', description: 'File path to delete' }
    },
    required: ['path']
  },
  handler: async (input: { path: string }) => {
    await fs.remove(input.path);
    return { success: true, path: input.path };
  },
  safety: {
    readOnly: false,
    requiresApproval: true,
    dangerous: true
  }
};

export const listFilesTool: ToolDefinition = {
  name: 'list_files',
  description: 'List files in a directory',
  inputSchema: {
    type: 'object',
    properties: {
      path: { type: 'string', description: 'Directory path' },
      recursive: { type: 'boolean', description: 'List recursively', default: false }
    },
    required: ['path']
  },
  handler: async (input: { path: string; recursive?: boolean }) => {
    const files: string[] = [];
    
    if (input.recursive) {
      const walk = async (dir: string) => {
        const entries = await fs.readdir(dir, { withFileTypes: true });
        for (const entry of entries) {
          const fullPath = path.join(dir, entry.name);
          if (entry.isDirectory()) {
            await walk(fullPath);
          } else {
            files.push(fullPath);
          }
        }
      };
      await walk(input.path);
    } else {
      const entries = await fs.readdir(input.path);
      files.push(...entries.map(e => path.join(input.path, e)));
    }
    
    return { files };
  },
  safety: {
    readOnly: true,
    requiresApproval: false,
    dangerous: false
  }
};
```

---

## 6. Git Integration

### 6.1 Git Manager

```typescript
// packages/cli/src/git/manager.ts
import simpleGit, { SimpleGit } from 'simple-git';

export class GitManager {
  private git: SimpleGit;

  constructor(workingDir: string = process.cwd()) {
    this.git = simpleGit(workingDir);
  }

  async isRepository(): Promise<boolean> {
    try {
      await this.git.revparse(['--git-dir']);
      return true;
    } catch {
      return false;
    }
  }

  async getCurrentBranch(): Promise<string> {
    const branch = await this.git.revparse(['--abbrev-ref', 'HEAD']);
    return branch.trim();
  }

  async getStatus(): Promise<{
    modified: string[];
    added: string[];
    deleted: string[];
    untracked: string[];
  }> {
    const status = await this.git.status();
    
    return {
      modified: status.modified,
      added: status.created,
      deleted: status.deleted,
      untracked: status.not_added
    };
  }

  async commit(message: string, files?: string[]): Promise<void> {
    if (files && files.length > 0) {
      await this.git.add(files);
    } else {
      await this.git.add('.');
    }
    
    await this.git.commit(message);
  }

  async createBranch(name: string, from?: string): Promise<void> {
    if (from) {
      await this.git.checkoutBranch(name, from);
    } else {
      await this.git.checkoutLocalBranch(name);
    }
  }

  async switchBranch(name: string): Promise<void> {
    await this.git.checkout(name);
  }

  async getDiff(
    options: {
      staged?: boolean;
      files?: string[];
    } = {}
  ): Promise<string> {
    const args: string[] = [];
    
    if (options.staged) {
      args.push('--staged');
    }
    
    if (options.files) {
      args.push('--', ...options.files);
    }
    
    return await this.git.diff(args);
  }

  async push(remote: string = 'origin', branch?: string): Promise<void> {
    if (!branch) {
      branch = await this.getCurrentBranch();
    }
    
    await this.git.push(remote, branch);
  }

  async pull(remote: string = 'origin', branch?: string): Promise<void> {
    if (!branch) {
      branch = await this.getCurrentBranch();
    }
    
    await this.git.pull(remote, branch);
  }

  async listBranches(): Promise<{
    local: string[];
    remote: string[];
    current: string;
  }> {
    const summary = await this.git.branch();
    
    return {
      local: summary.all.filter(b => !b.startsWith('remotes/')),
      remote: summary.all.filter(b => b.startsWith('remotes/')),
      current: summary.current
    };
  }

  async log(options: { maxCount?: number } = {}): Promise<any[]> {
    const log = await this.git.log({
      maxCount: options.maxCount || 10
    });
    
    return log.all;
  }
}
```

---

## 7. Configuration System

### 7.1 Hierarchical Configuration

```typescript
// packages/cli/src/config/hierarchical.ts
export class HierarchicalConfigManager {
  private configs: Map<string, any>;
  private paths: {
    global: string;
    local: string;
    project: string;
  };

  constructor() {
    this.configs = new Map();
    this.paths = {
      global: path.join(os.homedir(), '.monkey-coder', 'config.json'),
      local: path.join(process.cwd(), '.monkey-coder.json'),
      project: path.join(process.cwd(), '.monkey-coder', 'config.json')
    };
  }

  async load(): Promise<void> {
    // Load global config
    const globalConfig = await this.loadConfig(this.paths.global);
    this.configs.set('global', globalConfig);

    // Load local config
    const localConfig = await this.loadConfig(this.paths.local);
    this.configs.set('local', localConfig);

    // Load project config
    const projectConfig = await this.loadConfig(this.paths.project);
    this.configs.set('project', projectConfig);
  }

  get<T>(key: string, defaultValue?: T): T {
    // Priority: project > local > global
    const value = 
      this.getValue('project', key) ??
      this.getValue('local', key) ??
      this.getValue('global', key) ??
      defaultValue;

    return value as T;
  }

  async set(
    key: string,
    value: any,
    scope: 'global' | 'local' | 'project' = 'global'
  ): Promise<void> {
    const config = this.configs.get(scope) || {};
    this.setNestedValue(config, key, value);
    this.configs.set(scope, config);

    await this.saveConfig(this.paths[scope], config);
  }

  async unset(
    key: string,
    scope: 'global' | 'local' | 'project' = 'global'
  ): Promise<void> {
    const config = this.configs.get(scope) || {};
    this.deleteNestedValue(config, key);

    await this.saveConfig(this.paths[scope], config);
  }

  list(scope?: 'global' | 'local' | 'project'): Record<string, any> {
    if (scope) {
      return this.configs.get(scope) || {};
    }

    // Merge all configs (project > local > global)
    return {
      ...this.configs.get('global'),
      ...this.configs.get('local'),
      ...this.configs.get('project')
    };
  }

  private async loadConfig(path: string): Promise<any> {
    try {
      return await fs.readJson(path);
    } catch {
      return {};
    }
  }

  private async saveConfig(path: string, config: any): Promise<void> {
    await fs.ensureDir(path.dirname(path));
    await fs.writeJson(path, config, { spaces: 2 });
  }

  private getValue(scope: string, key: string): any {
    const config = this.configs.get(scope);
    if (!config) return undefined;

    const keys = key.split('.');
    let value = config;

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        return undefined;
      }
    }

    return value;
  }

  private setNestedValue(obj: any, key: string, value: any): void {
    const keys = key.split('.');
    const lastKey = keys.pop()!;

    let current = obj;
    for (const k of keys) {
      if (!(k in current) || typeof current[k] !== 'object') {
        current[k] = {};
      }
      current = current[k];
    }

    current[lastKey] = value;
  }

  private deleteNestedValue(obj: any, key: string): void {
    const keys = key.split('.');
    const lastKey = keys.pop()!;

    let current = obj;
    for (const k of keys) {
      if (!(k in current)) return;
      current = current[k];
    }

    delete current[lastKey];
  }
}
```

---

## 8. Testing Infrastructure

### 8.1 Command Testing Framework

```typescript
// packages/cli/__tests__/helpers/command-runner.ts
import { Command } from 'commander';

export class CommandTestRunner {
  private program: Command;
  private stdout: string[];
  private stderr: string[];

  constructor(program: Command) {
    this.program = program;
    this.stdout = [];
    this.stderr = [];
    this.captureOutput();
  }

  async run(args: string[]): Promise<{
    exitCode: number;
    stdout: string;
    stderr: string;
  }> {
    this.stdout = [];
    this.stderr = [];

    try {
      await this.program.parseAsync(['node', 'monkey', ...args]);
      return {
        exitCode: 0,
        stdout: this.stdout.join('\n'),
        stderr: this.stderr.join('\n')
      };
    } catch (error) {
      return {
        exitCode: 1,
        stdout: this.stdout.join('\n'),
        stderr: this.stderr.join('\n') + '\n' + error
      };
    }
  }

  private captureOutput(): void {
    const originalLog = console.log;
    const originalError = console.error;

    console.log = (...args: any[]) => {
      this.stdout.push(args.join(' '));
    };

    console.error = (...args: any[]) => {
      this.stderr.push(args.join(' '));
    };

    // Restore on process exit
    process.on('exit', () => {
      console.log = originalLog;
      console.error = originalError;
    });
  }
}

// Example test
describe('repo commands', () => {
  let runner: CommandTestRunner;

  beforeEach(() => {
    const program = createProgram();
    runner = new CommandTestRunner(program);
  });

  it('should create a repository', async () => {
    const result = await runner.run(['repo', 'create', 'test-repo']);
    
    expect(result.exitCode).toBe(0);
    expect(result.stdout).toContain('Repository created');
  });

  it('should show error for invalid name', async () => {
    const result = await runner.run(['repo', 'create', '']);
    
    expect(result.exitCode).toBe(1);
    expect(result.stderr).toContain('name is required');
  });
});
```

---

This implementation guide provides the foundation for building a world-class CLI. Each section can be expanded with additional features and refinements as needed.
