import chalk from 'chalk';

import { ConfigManager } from './config.js';
import { printEnhancedSplash, printEnhancedSplashSync } from './enhanced-splash.js';

/**
 * Simple fallback splash for when enhanced rendering fails
 */
function printFallbackSplash(): void {
  console.clear();
  console.log('');
  console.log(chalk.yellow.bold('🐒 Monkey Coder CLI - AI-Powered Development Toolkit 🚀'));
  console.log('');
  console.log(chalk.dim('Tips for getting started:'));
  console.log(chalk.dim('1. Ask questions, implement features, or run analysis.'));
  console.log(chalk.dim('2. Be specific for the best results.'));
  console.log(chalk.dim('3. Use --help for command information.'));
  console.log('');
}

/**
 * Main splash screen function - displays enhanced graphics when supported.
 * Falls back gracefully to simple text in unsupported terminals.
 * Uses term-img, Kitty graphics, iTerm2 images, or enhanced Unicode art.
 *
 * @param {boolean} [suppress=false] - Optional flag to suppress the splash screen.
 */
export function printSplashSync(suppress = false): void {
  const config = new ConfigManager();
  if (
    suppress ||
    !process.stdout.isTTY ||
    process.env.MONKEY_CLI_NO_SPLASH || 
    process.env.MONKEY_CODER_NO_SPLASH ||
    !config.getShowSplash()
  ) {
    return;
  }

  try {
    // Use enhanced splash with graphics support
    printEnhancedSplashSync(false);
  } catch (error) {
    // Ultimate fallback to simple text
    printFallbackSplash();
  }
}

/**
 * Async version of splash display with enhanced graphics
 */
export async function printSplashAsync(suppress = false): Promise<void> {
  const config = new ConfigManager();
  if (
    suppress ||
    !process.stdout.isTTY ||
    process.env.MONKEY_CLI_NO_SPLASH || 
    process.env.MONKEY_CODER_NO_SPLASH ||
    !config.getShowSplash()
  ) {
    return;
  }

  try {
    await printEnhancedSplash(false);
  } catch (_error) {
    printFallbackSplash();
  }
}

/**
 * Legacy function for backward compatibility - now uses enhanced splash
 */
export function printSplash(suppress = false): void {
  printSplashSync(suppress);
}

// Export enhanced splash utilities
export { EnhancedSplash } from './enhanced-splash.js';
export { detectTerminalCapabilities, getBestGraphicsProtocol } from './terminal-capabilities.js';
export { GraphicsProtocols } from './graphics-protocols.js';