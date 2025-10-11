import path from 'path';
import { fileURLToPath } from 'url';

import sharp from 'sharp';
import termImg from 'term-img';
import chalk from 'chalk';

import { getOptimalImageDimensions, TerminalCapabilities } from './terminal-capabilities.js';

// ES module equivalent of __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Graphics protocol implementations for different terminals
 */
export class GraphicsProtocols {
  private static logoPath = path.join(__dirname, '..', '..', '..', 'web', 'public', 'splash.png');
  private static fallbackLogoPath = path.join(__dirname, '..', 'assets', 'splash.png');

  /**
   * Display image using term-img (most compatible)
   */
  static async renderWithTermImg(): Promise<string> {
    try {
      const logoPath = await this.getLogoPath();
      const dimensions = getOptimalImageDimensions();
      
      // Resize image for optimal terminal display
      const resizedBuffer = await sharp(logoPath)
        .resize(dimensions.width * 2, dimensions.height * 4) // Higher resolution for better quality
        .png()
        .toBuffer();

      // Use term-img to render
      const imageString = termImg(resizedBuffer, { 
        width: dimensions.width,
        height: dimensions.height,
        fallback: this.renderUnicodeArt
      });

      return imageString;
    } catch (error) {
      console.error('term-img rendering failed:', error);
      return this.renderUnicodeArt();
    }
  }

  /**
   * Display image using Kitty graphics protocol
   */
  static async renderWithKitty(): Promise<string> {
    try {
      const logoPath = await this.getLogoPath();
      const dimensions = getOptimalImageDimensions();
      
      const imageBuffer = await sharp(logoPath)
        .resize(dimensions.width * 8, dimensions.height * 16) // High resolution for Kitty
        .png()
        .toBuffer();

      const base64Data = imageBuffer.toString('base64');
      
      // Kitty graphics protocol escape sequence
      const kittySequence = `\x1b_Ga=T,f=100,s=${dimensions.width * 8},v=${dimensions.height * 16};${base64Data}\x1b\\`;
      
      return kittySequence + '\n';
    } catch (error) {
      console.error('Kitty protocol rendering failed:', error);
      return this.renderUnicodeArt();
    }
  }

  /**
   * Display image using iTerm2 inline images
   */
  static async renderWithITerm2(): Promise<string> {
    try {
      const logoPath = await this.getLogoPath();
      const dimensions = getOptimalImageDimensions();
      
      const imageBuffer = await sharp(logoPath)
        .resize(dimensions.width * 4, dimensions.height * 8)
        .png()
        .toBuffer();

      const base64Data = imageBuffer.toString('base64');
      
      // iTerm2 inline image protocol
      const iterm2Sequence = `\x1b]1337;File=inline=1;width=${dimensions.width}ch;height=${dimensions.height}ch:${base64Data}\x07`;
      
      return iterm2Sequence + '\n';
    } catch (error) {
      console.error('iTerm2 rendering failed:', error);
      return this.renderUnicodeArt();
    }
  }

  /**
   * Display image using Sixel graphics
   */
  static async renderWithSixel(): Promise<string> {
    try {
      const logoPath = await this.getLogoPath();
      const dimensions = getOptimalImageDimensions();
      
      // For now, fall back to Unicode art as Sixel conversion is complex
      // In a full implementation, you'd use a library like node-sixel or implement conversion
      console.warn('Sixel rendering not yet implemented, falling back to Unicode art');
      return this.renderUnicodeArt();
    } catch (error) {
      console.error('Sixel rendering failed:', error);
      return this.renderUnicodeArt();
    }
  }

  /**
   * Create enhanced Unicode art representation
   */
  static renderUnicodeArt(): string {
    const colors = {
      cyan: chalk.hex('#00cec9'),
      orange: chalk.hex('#ff7675'),
      yellow: chalk.hex('#fdcb6e'),
      purple: chalk.hex('#a29bfe'),
      green: chalk.hex('#00b894')
    };

    // Enhanced Unicode art using block characters and Braille patterns
    return `
${colors.cyan('    ████████')} ${colors.orange('██')} ${colors.yellow('██████████')} ${colors.purple('██')} ${colors.green('██')}
${colors.cyan('  ██')}        ${colors.orange('██')} ${colors.yellow('██')}        ${colors.purple('██')} ${colors.green('██')}
${colors.cyan('██')}   ${colors.orange('████')}   ${colors.yellow('██')}   ${colors.purple('██████')}   ${colors.green('██')}
${colors.cyan('██')}  ${colors.orange('██  ██')}  ${colors.yellow('██')}  ${colors.purple('██    ██')}  ${colors.green('██')}
${colors.cyan('██')} ${colors.orange('██    ██')} ${colors.yellow('██')} ${colors.purple('██      ██')} ${colors.green('██')}
${colors.cyan('████')}      ${colors.orange('████')}      ${colors.yellow('████')}      ${colors.green('████')}

${colors.cyan.bold('    ███    ███  ████████  ██████   ██   ██ ███████ ██    ██')}
${colors.cyan.bold('    ████  ████ ██     ██ ██    ██ ██  ██  ██       ██  ██')}
${colors.cyan.bold('    ██ ████ ██ ██     ██ ██    ██ █████   █████     ████')}
${colors.cyan.bold('    ██  ██  ██ ██     ██ ██    ██ ██  ██  ██         ██')}
${colors.cyan.bold('    ██      ██  ████████   ██████  ██   ██ ███████    ██')}

${colors.orange.bold('     ██████  ████████  ████████  ███████ ██████')}
${colors.orange.bold('     ██      ██     ██ ██     ██ ██      ██   ██')}
${colors.orange.bold('     ██      ██     ██ ██     ██ █████   ██████')}
${colors.orange.bold('     ██      ██     ██ ██     ██ ██      ██   ██')}
${colors.orange.bold('     ██████  ████████  ████████  ███████ ██   ██')}
`;
  }

  /**
   * Create Braille pattern art (high resolution)
   */
  static renderBrailleArt(): string {
    // Braille patterns offer 2x4 pixel resolution per character
    const brailleArt = `
⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⡇⠀⢀⣀⣤⣤⣤⣶⣶⣶⣶⣶⣶⣤⣤⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⡇⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⡇⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿
`;

    return chalk.cyan(brailleArt);
  }

  /**
   * Get the path to the logo file, with fallback
   */
  private static async getLogoPath(): Promise<string> {
    try {
      // Try web public directory first
      await sharp(this.logoPath).metadata();
      return this.logoPath;
    } catch {
      try {
        // Try CLI assets directory
        await sharp(this.fallbackLogoPath).metadata();
        return this.fallbackLogoPath;
      } catch {
        throw new Error('splash.png not found in expected locations');
      }
    }
  }

  /**
   * Render using the best available protocol for given capabilities
   */
  static async renderOptimal(protocol: string): Promise<string> {
    switch (protocol) {
      case 'term-img':
        return await this.renderWithTermImg();
      case 'kitty':
        return await this.renderWithKitty();
      case 'iterm2':
        return await this.renderWithITerm2();
      case 'sixel':
        return await this.renderWithSixel();
      case 'unicode':
        return this.renderUnicodeArt();
      case 'braille':
        return this.renderBrailleArt();
      default:
        return this.renderUnicodeArt();
    }
  }
}