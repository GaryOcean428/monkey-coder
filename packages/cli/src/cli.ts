#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import { version } from '../package.json';

const program = new Command();

program
  .name('monkey-coder')
  .description('Monkey Coder CLI - AI-powered code generation and analysis')
  .version(version);

program
  .command('generate')
  .description('Generate code using Qwen3-Coder')
  .argument('<prompt>', 'Code generation prompt')
  .option('-l, --language <lang>', 'Target programming language', 'typescript')
  .option('-o, --output <file>', 'Output file path')
  .action((prompt, options) => {
    console.log(chalk.green('🚀 Generating code...'));
    console.log(chalk.blue(`Prompt: ${prompt}`));
    console.log(chalk.yellow(`Language: ${options.language}`));
    if (options.output) {
      console.log(chalk.yellow(`Output: ${options.output}`));
    }
    // TODO: Implement code generation logic
  });

program
  .command('analyze')
  .description('Analyze existing code')
  .argument('<file>', 'File to analyze')
  .option('-t, --type <type>', 'Analysis type', 'quality')
  .action((file, options) => {
    console.log(chalk.green('🔍 Analyzing code...'));
    console.log(chalk.blue(`File: ${file}`));
    console.log(chalk.yellow(`Analysis type: ${options.type}`));
    // TODO: Implement code analysis logic
  });

program.parse();
