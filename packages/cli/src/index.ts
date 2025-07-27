/**
 * Monkey Coder CLI - Main entry point
 * 
 * This package provides a command-line interface for the Monkey Coder
 * AI-powered code generation and analysis platform.
 */

export { MonkeyCoderAPIClient } from './api-client.js';
export { ConfigManager } from './config.js';
export * from './types.js';
export * from './utils.js';

// Re-export for convenience
export default './cli.js';
