import { Command } from 'commander';

import { EnhancedSplash } from '../enhanced-splash.js';

export function createSplashTestCommand(): Command {
  const command = new Command('splash-test');

  command
    .description('Test and debug splash screen rendering capabilities')
    .option('-c, --capabilities', 'Show terminal capabilities')
    .option('-p, --protocol <protocol>', 'Test specific graphics protocol (term-img, kitty, iterm2, sixel, unicode, braille)')
    .option('-f, --force', 'Force splash display even if disabled')
    .action(async (options) => {
      if (options.capabilities) {
        EnhancedSplash.displayCapabilities();
      }

      if (options.protocol) {
        await EnhancedSplash.testProtocol(options.protocol);
      }

      if (options.force || (!options.capabilities && !options.protocol)) {
        await EnhancedSplash.renderSplash(options.force);
      }
    });

  return command;
}