/**
 * Configuration schemas for Monkey Coder CLI
 * Defines the structure and validation for .monkey-coder.json config files
 */

import { z } from 'zod';

/**
 * Permission configuration for local tools execution
 * Controls which files and commands are allowed/denied
 */
export const PermissionConfigSchema = z.object({
  allowedPaths: z.array(z.string()).default(['./**/*']),
  deniedPaths: z.array(z.string()).default([
    '**/.env*',
    '**/.git/**',
    '**/node_modules/**',
    '**/*.pem',
    '**/*.key',
  ]),
  allowedCommands: z.array(z.string()).default([
    'ls *', 'cat *', 'head *', 'tail *',
    'git status', 'git diff *', 'git log *',
    'npm list *', 'yarn info *',
  ]),
  deniedCommands: z.array(z.string()).default([
    'rm -rf /*', 'sudo *', 'chmod 777 *',
  ]),
  requireApproval: z.boolean().default(true),
  maxFileSize: z.number().default(10 * 1024 * 1024), // 10MB
  timeout: z.number().default(30000), // 30 seconds
});

export type PermissionConfig = z.infer<typeof PermissionConfigSchema>;

/**
 * MCP server configuration
 * Defines how to connect to Model Context Protocol servers
 */
export const MCPServerConfigSchema = z.object({
  name: z.string(),
  type: z.enum(['stdio', 'sse', 'http']),
  command: z.string().optional(),
  args: z.array(z.string()).optional(),
  url: z.string().optional(),
  enabled: z.boolean().default(true),
});

export type MCPServerConfig = z.infer<typeof MCPServerConfigSchema>;

/**
 * MCP configuration section
 * Lists all MCP servers to connect to
 */
export const MCPConfigSchema = z.object({
  servers: z.array(MCPServerConfigSchema).default([]),
});

export type MCPConfig = z.infer<typeof MCPConfigSchema>;

/**
 * Agent configuration section
 * Defines default behavior for the AI agent
 */
export const AgentConfigSchema = z.object({
  defaultProvider: z.enum(['openai', 'anthropic', 'google']).default('anthropic'),
  defaultModel: z.string().default('claude-sonnet-4-5-20250929'),
  maxIterations: z.number().default(10),
  autoApprove: z.boolean().default(false),
  sandbox: z.enum(['none', 'basic', 'docker']).default('basic'),
});

export type AgentConfig = z.infer<typeof AgentConfigSchema>;

/**
 * Root configuration schema
 * This is the complete structure of a .monkey-coder.json file
 */
export const MonkeyCoderConfigSchema = z.object({
  version: z.literal(1).default(1),
  permissions: PermissionConfigSchema.default({}),
  mcp: MCPConfigSchema.default({}),
  agent: AgentConfigSchema.default({}),
});

export type MonkeyCoderConfig = z.infer<typeof MonkeyCoderConfigSchema>;
