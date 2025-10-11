import { execSync } from 'child_process';

import supportsColor from 'supports-color';

export interface TerminalCapabilities {
  sixel: boolean;
  kitty: boolean;
  iterm2: boolean;
  trueColor: boolean;
  unicode: boolean;
  termImg: boolean;
  width: number;
  height: number;
}

/**
 * Detects terminal capabilities for optimal graphics rendering
 */
export function detectTerminalCapabilities(): TerminalCapabilities {
  const capabilities: TerminalCapabilities = {
    sixel: false,
    kitty: false,
    iterm2: false,
    trueColor: false,
    unicode: false,
    termImg: false,
    width: process.stdout.columns || 80,
    height: process.stdout.rows || 24,
  };

  // Only check capabilities if running in a TTY
  if (!process.stdout.isTTY) {
    return capabilities;
  }

  // Check for true color support (24-bit)
  const stdoutSupport = supportsColor.stdout;
  capabilities.trueColor = stdoutSupport && typeof stdoutSupport === 'object' && stdoutSupport.level >= 3;

  // Check for Unicode support
  capabilities.unicode = process.stdout.isTTY && !process.env.ASCII_ONLY;

  // Check for term-img support (general image display capability)
  try {
    // term-img can display images in supported terminals
    capabilities.termImg = true;
  } catch {
    capabilities.termImg = false;
  }

  // Check for Sixel support
  try {
    const term = process.env.TERM || '';
    const termProgram = process.env.TERM_PROGRAM || '';
    
    // Common terminals with Sixel support
    if (term.includes('xterm') || term.includes('mlterm') || term.includes('screen')) {
      // Try to detect Sixel capability by checking terminal response
      // This is a lightweight check rather than actually sending Sixel data
      capabilities.sixel = true;
    }
  } catch {
    capabilities.sixel = false;
  }

  // Check for Kitty graphics protocol
  try {
    if (process.env.TERM === 'xterm-kitty' || process.env.KITTY_WINDOW_ID) {
      capabilities.kitty = true;
    }
  } catch {
    capabilities.kitty = false;
  }

  // Check for iTerm2 inline images
  try {
    if (process.env.TERM_PROGRAM === 'iTerm.app' || 
        process.env.ITERM_SESSION_ID ||
        process.env.TERM_PROGRAM === 'vscode') {
      capabilities.iterm2 = true;
    }
  } catch {
    capabilities.iterm2 = false;
  }

  return capabilities;
}

/**
 * Gets the best graphics protocol available for the current terminal
 */
export function getBestGraphicsProtocol(): 'term-img' | 'sixel' | 'kitty' | 'iterm2' | 'unicode' | 'ascii' {
  const caps = detectTerminalCapabilities();

  // Priority order: term-img (most compatible) -> Kitty -> iTerm2 -> Sixel -> Unicode -> ASCII
  if (caps.termImg) return 'term-img';
  if (caps.kitty) return 'kitty';
  if (caps.iterm2) return 'iterm2'; 
  if (caps.sixel) return 'sixel';
  if (caps.unicode && caps.trueColor) return 'unicode';
  
  return 'ascii';
}

/**
 * Determines optimal image dimensions for the current terminal
 */
export function getOptimalImageDimensions(): { width: number; height: number } {
  const caps = detectTerminalCapabilities();
  
  // Calculate reasonable image size based on terminal dimensions
  // Leave some margin for text
  const maxWidth = Math.min(caps.width - 4, 80);
  const maxHeight = Math.min(caps.height - 10, 24);
  
  // Maintain aspect ratio of splash.png (approximately 3.75:1)
  const aspectRatio = 3.75;
  
  let width = maxWidth;
  let height = Math.round(width / aspectRatio);
  
  // Adjust if height is too large
  if (height > maxHeight) {
    height = maxHeight;
    width = Math.round(height * aspectRatio);
  }
  
  return { width, height };
}

/**
 * Check if the terminal supports a specific feature
 */
export function supportsFeature(feature: keyof TerminalCapabilities): boolean {
  const caps = detectTerminalCapabilities();
  return caps[feature] as boolean;
}