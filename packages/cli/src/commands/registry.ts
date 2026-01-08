/**
 * Command Registry for Hierarchical Command System
 * 
 * This module provides infrastructure for registering and managing
 * hierarchical commands with categories, subcommands, and aliases.
 */

import { Command } from 'commander';

export type CommandCategory = 'core' | 'git' | 'project' | 'config' | 'extension' | 'ai';

export interface CommandOption {
  flags: string;
  description: string;
  defaultValue?: any;
  required?: boolean;
}

export interface CommandExample {
  command: string;
  description: string;
}

export interface CommandDefinition {
  name: string;
  aliases?: string[];
  description: string;
  category: CommandCategory;
  subcommands?: CommandDefinition[];
  options?: CommandOption[];
  arguments?: Array<{
    name: string;
    description: string;
    required?: boolean;
    variadic?: boolean;
  }>;
  handler?: (...args: any[]) => Promise<void> | void;
  examples?: CommandExample[];
  hidden?: boolean;
}

/**
 * Command Registry manages hierarchical command structure
 */
export class CommandRegistry {
  private commands: Map<string, CommandDefinition> = new Map();
  private aliases: Map<string, string> = new Map();

  /**
   * Register a command definition
   */
  register(definition: CommandDefinition): void {
    this.commands.set(definition.name, definition);

    // Register aliases
    if (definition.aliases) {
      for (const alias of definition.aliases) {
        this.aliases.set(alias, definition.name);
      }
    }

    // Register subcommands recursively
    if (definition.subcommands) {
      for (const subcommand of definition.subcommands) {
        const fullName = `${definition.name}.${subcommand.name}`;
        this.commands.set(fullName, subcommand);

        // Register subcommand aliases
        if (subcommand.aliases) {
          for (const alias of subcommand.aliases) {
            this.aliases.set(`${definition.name}.${alias}`, fullName);
          }
        }
      }
    }
  }

  /**
   * Get command by name or alias
   */
  get(nameOrAlias: string): CommandDefinition | undefined {
    // Try direct lookup
    let command = this.commands.get(nameOrAlias);
    if (command) return command;

    // Try alias lookup
    const aliasedName = this.aliases.get(nameOrAlias);
    if (aliasedName) {
      return this.commands.get(aliasedName);
    }

    return undefined;
  }

  /**
   * Get all commands in a category
   */
  getByCategory(category: CommandCategory): CommandDefinition[] {
    return Array.from(this.commands.values()).filter(
      (cmd) => cmd.category === category
    );
  }

  /**
   * Build a Commander.js command from a definition
   */
  buildCommand(definition: CommandDefinition): Command {
    const command = new Command(definition.name);
    command.description(definition.description);

    // Add aliases
    if (definition.aliases && definition.aliases.length > 0) {
      command.aliases(definition.aliases);
    }

    // Add arguments
    if (definition.arguments) {
      for (const arg of definition.arguments) {
        const argName = arg.required
          ? `<${arg.name}>`
          : `[${arg.name}${arg.variadic ? '...' : ''}]`;
        command.argument(argName, arg.description);
      }
    }

    // Add options
    if (definition.options) {
      for (const opt of definition.options) {
        if (opt.defaultValue !== undefined) {
          command.option(opt.flags, opt.description, opt.defaultValue);
        } else {
          command.option(opt.flags, opt.description);
        }
      }
    }

    // Add examples to help
    if (definition.examples && definition.examples.length > 0) {
      const examplesText = definition.examples
        .map((ex) => `  $ ${ex.command}\n    ${ex.description}`)
        .join('\n\n');
      command.addHelpText('after', `\nExamples:\n${examplesText}`);
    }

    // Add handler
    if (definition.handler) {
      command.action(definition.handler);
    }

    // Add subcommands
    if (definition.subcommands) {
      for (const subDef of definition.subcommands) {
        const subCommand = this.buildCommand(subDef);
        command.addCommand(subCommand);
      }
    }

    // Hide if marked as hidden (Commander v14 doesn't have hide() method)
    if (definition.hidden) {
      // Use hideHelp() or set as not shown in help
      command.configureHelp({ visibleCommands: () => [] });
    }

    return command;
  }

  /**
   * Get all registered commands
   */
  getAll(): CommandDefinition[] {
    return Array.from(this.commands.values());
  }

  /**
   * Get all registered aliases
   */
  getAliases(): Map<string, string> {
    return new Map(this.aliases);
  }
}

/**
 * Global command registry instance
 */
export const commandRegistry = new CommandRegistry();
