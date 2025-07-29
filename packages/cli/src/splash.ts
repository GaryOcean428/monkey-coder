import fs from 'fs';
import path from 'path';
import chalk from 'chalk';
import { fileURLToPath } from 'url';
import { ConfigManager } from './config.js';

// ES module equivalent of __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const MONKEY_ASCII = `
                    ╭─────────────────────────────────────────────────────────╮
                    │                                                         │
                    │                       .-"-.                             │
                    │                      /     \\                            │
                    │                     | () () |                           │
                    │                      \\  ^  /                            │
                    │                       |||||                             │
                    │                       |||||                             │
                    │                                                         │
                    │        ████████╗    ███╗   ███╗ ██████╗ ███╗   ██╗    │
                    │        ╚══██╔══╝    ████╗ ████║██╔═══██╗████╗  ██║    │
                    │           ██║       ██╔████╔██║██║   ██║██╔██╗ ██║    │  
                    │           ██║       ██║╚██╔╝██║██║   ██║██║╚██╗██║    │
                    │           ██║       ██║ ╚═╝ ██║╚██████╔╝██║ ╚████║    │
                    │           ╚═╝       ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝    │
                    │                                                         │
                    │           ██╗  ██╗███████╗██╗   ██╗                    │
                    │           ██║ ██╔╝██╔════╝╚██╗ ██╔╝                    │
                    │           █████╔╝ █████╗   ╚████╔╝                     │
                    │           ██╔═██╗ ██╔══╝    ╚██╔╝                      │
                    │           ██║  ██╗███████╗   ██║                       │ 
                    │           ╚═╝  ╚═╝╚══════╝   ╚═╝                       │
                    │                                                         │
                    │     ██████╗ ██████╗ ██████╗ ███████╗██████╗            │
                    │    ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗           │
                    │    ██║     ██║   ██║██║  ██║█████╗  ██████╔╝           │
                    │    ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗           │
                    │    ╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║           │
                    │     ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝           │
                    │                                                         │
                    │        🐒  AI-Powered Development Toolkit  🚀           │
                    │                                                         │
                    ╰─────────────────────────────────────────────────────────╯
`;

function printColorizedSplash(): void {
  console.clear();
  console.log('');
  
  const lines = MONKEY_ASCII.split('\n');
  
  for (const line of lines) {
    if (!line) {
      console.log('');
      continue;
    }
    
    // Color the monkey face
    if (line.includes('.-"-.') || line.includes('/     \\') || line.includes('| () () |') || 
        line.includes('\\  ^  /') || line.includes('|||||')) {
      console.log(chalk.yellow.bold(line));
    }
    // Color the "MONKEY" text - T, M, O, N, K, E, Y
    else if (line.includes('████████╗') || line.includes('╚══██╔══╝') || line.includes('██║')) {
      if (line.includes('███╗   ███╗') || line.includes('████╗ ████║') || line.includes('██╔████╔██║') || 
          line.includes('██║╚██╔╝██║') || line.includes('██║ ╚═╝ ██║')) {
        console.log(chalk.cyan.bold(line));
      } else if (line.includes('██████╗') || line.includes('██╔═══██╗') || line.includes('██║   ██║') || 
                 line.includes('╚██████╔╝')) {
        console.log(chalk.blue.bold(line));
      } else if (line.includes('███╗   ██╗') || line.includes('████╗  ██║') || line.includes('██╔██╗ ██║') || 
                 line.includes('██║╚██╗██║') || line.includes('██║ ╚████║')) {
        console.log(chalk.green.bold(line));
      } else {
        console.log(chalk.cyan.bold(line));
      }
    }
    // Color the "KEY" text
    else if (line.includes('██╗  ██╗') || line.includes('███████╗') || line.includes('██╗   ██╗') ||
             line.includes('██║ ██╔╝') || line.includes('██╔════╝') || line.includes('╚██╗ ██╔╝') ||
             line.includes('█████╔╝') || line.includes('█████╗') || line.includes('╚████╔╝') ||
             line.includes('██╔═██╗') || line.includes('██╔══╝') || line.includes('╚██╔╝') ||
             line.includes('██║  ██╗') || line.includes('███████╗') || line.includes('██║')) {
      console.log(chalk.yellow.bold(line));
    }
    // Color the "CODER" text
    else if (line.includes('██████╗ ██████╗ ██████╗ ███████╗██████╗') ||
             line.includes('██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗') ||
             line.includes('██║     ██║   ██║██║  ██║█████╗  ██████╔╝') ||
             line.includes('╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║') ||
             line.includes('╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝')) {
      console.log(chalk.magenta.bold(line));
    }
    // Color the tagline
    else if (line.includes('🐒  AI-Powered Development Toolkit  🚀')) {
      console.log(chalk.rgb(255, 165, 0).bold(line)); // Orange color
    }
    // Default border and spacing
    else {
      console.log(chalk.gray(line));
    }
  }
  
  // Add status information
  console.log(chalk.dim('                           Phase 1 Complete • Phase 2 Ready'));
  console.log(chalk.dim('                           Quantum routing engine ready to load...'));
  console.log('');
  console.log(chalk.green('                           ✓ Ready to code with AI!'));
  console.log('');
}

/**
 * Displays an enhanced splash screen with colorized ASCII art.
 *
 * @param {boolean} [suppress=false] - Optional flag to suppress the splash screen.
 */
export function printSplashSync(suppress = false): void {
  const config = new ConfigManager();
  if (
    suppress ||
    !process.stdout.isTTY ||
    process.env.MONKEY_CLI_NO_SPLASH || process.env.MONKEY_CODER_NO_SPLASH ||
    !config.getShowSplash()
  ) {
    return;
  }

  try {
    printColorizedSplash();
  } catch (error) {
    // If there's an error, fall back to simple text
    console.log(chalk.yellow('🐒 Monkey Coder CLI - AI-Powered Development Toolkit 🚀'));
    console.log('');
  }
}

/**
 * Legacy function for backward compatibility - displays basic splash screen.
 *
 * @param {boolean} [suppress=false] - Optional flag to suppress the splash screen.
 */
export function printSplash(suppress = false): void {
  const config = new ConfigManager();
  if (
    suppress ||
    !process.stdout.isTTY ||
    process.env.MONKEY_CLI_NO_SPLASH || process.env.MONKEY_CODER_NO_SPLASH ||
    !config.getShowSplash()
  ) {
    return;
  }

  try {
    const artFile = path.join(__dirname, 'ascii-art.txt');
    const art = fs.readFileSync(artFile, 'utf8');

    // Simple check to see if there are ANSI escape codes already
    if (/\[/.test(art)) {
        console.log(art);
    } else {
        console.log(chalk.yellow(art));
    }
  } catch (error) {
    // If the art file is missing or there's an error, just do nothing.
    // The splash screen is not critical.
  }
}