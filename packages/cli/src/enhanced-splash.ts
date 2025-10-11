import chalk from 'chalk';
import boxen from 'boxen';

import { ConfigManager } from './config.js';
import { detectTerminalCapabilities, getBestGraphicsProtocol } from './terminal-capabilities.js';
import { GraphicsProtocols } from './graphics-protocols.js';

/**
 * Enhanced splash screen system with multi-tier graphics support
 */
export class EnhancedSplash {
  private static cache: Map<string, string> = new Map();

  /**
   * Render the splash screen using the best available graphics protocol
   */
  static async renderSplash(force = false): Promise<void> {
    const config = new ConfigManager();
    
    // Check if splash should be suppressed
    if (
      !force && (
        !process.stdout.isTTY ||
        process.env.MONKEY_CLI_NO_SPLASH || 
        process.env.MONKEY_CODER_NO_SPLASH ||
        !config.getShowSplash()
      )
    ) {
      return;
    }

    try {
      // Clear screen for clean display
      console.clear();
      console.log('');

      // Detect capabilities and get best protocol
      const capabilities = detectTerminalCapabilities();
      const bestProtocol = getBestGraphicsProtocol();
      
      // Check cache first
      const cacheKey = `${bestProtocol}-${capabilities.width}x${capabilities.height}`;
      let splashContent = this.cache.get(cacheKey);
      
      if (!splashContent) {
        // Render with best available protocol
        splashContent = await GraphicsProtocols.renderOptimal(bestProtocol);
        
        // Cache the result
        this.cache.set(cacheKey, splashContent);
      }

      // Display the logo
      console.log(splashContent);

      // Add branding and tips
      this.renderBranding();
      this.renderTips();

    } catch (error) {
      console.error('Enhanced splash rendering failed:', error);
      // Fallback to simple splash
      this.renderFallbackSplash();
    }
  }

  /**
   * Render the branding section
   */
  private static renderBranding(): void {
    const brandingBox = boxen(
      chalk.cyan.bold('🐒 MONKEY CODER') + '\n' +
      chalk.yellow('AI-Powered Development Toolkit') + '\n' +
      chalk.dim('v' + process.env.npm_package_version || '1.0.0'),
      {
        padding: 1,
        margin: { top: 1, bottom: 0, left: 2, right: 2 },
        borderStyle: 'round',
        borderColor: 'cyan',
        backgroundColor: 'black'
      }
    );
    
    console.log(brandingBox);
  }

  /**
   * Render helpful tips
   */
  private static renderTips(): void {
    const tips = [
      '💡 Ask questions, implement features, or run analysis',
      '🎯 Be specific for the best results', 
      '📚 Use --help for command information',
      '🚀 Try: monkey implement "create a REST API"'
    ];

    console.log(chalk.dim('\n  Quick Start Tips:'));
    tips.forEach(tip => {
      console.log(chalk.dim(`  ${tip}`));
    });
    console.log('');
  }

  /**
   * Fallback splash for when enhanced rendering fails
   */
  private static renderFallbackSplash(): void {
    console.log(chalk.yellow.bold('🐒 Monkey Coder CLI'));
    console.log(chalk.cyan('AI-Powered Development Toolkit'));
    console.log('');
    console.log(chalk.dim('Ready to help with your development tasks!'));
    console.log('');
  }

  /**
   * Display terminal capabilities information (debug)
   */
  static displayCapabilities(): void {
    const capabilities = detectTerminalCapabilities();
    const bestProtocol = getBestGraphicsProtocol();
    
    console.log(chalk.bold.cyan('Terminal Capabilities:'));
    console.log(`  Protocol: ${chalk.yellow(bestProtocol)}`);
    console.log(`  True Color: ${capabilities.trueColor ? chalk.green('✓') : chalk.red('✗')}`);
    console.log(`  Unicode: ${capabilities.unicode ? chalk.green('✓') : chalk.red('✗')}`);
    console.log(`  term-img: ${capabilities.termImg ? chalk.green('✓') : chalk.red('✗')}`);
    console.log(`  Kitty: ${capabilities.kitty ? chalk.green('✓') : chalk.red('✗')}`);
    console.log(`  iTerm2: ${capabilities.iterm2 ? chalk.green('✓') : chalk.red('✗')}`);
    console.log(`  Sixel: ${capabilities.sixel ? chalk.green('✓') : chalk.red('✗')}`);
    console.log(`  Dimensions: ${capabilities.width}x${capabilities.height}`);
    console.log('');
  }

  /**
   * Test rendering with a specific protocol
   */
  static async testProtocol(protocol: string): Promise<void> {
    console.log(chalk.cyan(`Testing ${protocol} protocol:`));
    console.log('');
    
    try {
      const result = await GraphicsProtocols.renderOptimal(protocol);
      console.log(result);
      console.log(chalk.green(`✓ ${protocol} rendering successful`));
    } catch (error) {
      console.log(chalk.red(`✗ ${protocol} rendering failed:`, error));
    }
    console.log('');
  }

  /**
   * Clear the splash cache
   */
  static clearCache(): void {
    this.cache.clear();
  }
}

/**
 * Legacy compatibility function - enhanced version
 */
export async function printEnhancedSplash(suppress = false): Promise<void> {
  await EnhancedSplash.renderSplash(!suppress);
}

/**
 * Synchronous version for backward compatibility
 */
export function printEnhancedSplashSync(suppress = false): void {
  // Use async version but don't wait
  EnhancedSplash.renderSplash(!suppress).catch(error => {
    console.error('Splash rendering error:', error);
  });
}