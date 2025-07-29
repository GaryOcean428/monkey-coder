import fs from 'fs';
import path from 'path';
import chalk from 'chalk';
import { fileURLToPath } from 'url';

// ES module equivalent of __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Displays a splash screen with ASCII art.
 *
 * @param {boolean} [suppress=false] - Optional flag to suppress the splash screen.
 */
import { ConfigManager } from './config.js';

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
    if (/\[/.test(art)) {
        console.log(art);
    } else {
        console.log(chalk.yellow(art));
    }
  } catch (error) {
    // If the art file is missing or there's an error, just do nothing.
    // The splash screen is not critical.
  }
}
