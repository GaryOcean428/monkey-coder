
import fs from 'fs';
import path from 'path';
import chalk from 'chalk';
import { fileURLToPath } from 'url';
import { ConfigManager } from './config.js';

// ES module equivalent of __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load the new splash art from assets/splashmonkey4.txt
function loadSplashArt(): string {
  try {
    const artPath = path.join(__dirname, '..', '..', 'assets', 'splashmonkey4.txt');
    let art = fs.readFileSync(artPath, 'utf8');
    
    // Process color template variables
    art = art.replace(/\${c1}/g, chalk.hex('#9ACD32')(''))  // Yellow-green
             .replace(/\${c2}/g, chalk.hex('#00BFFF')(''))  // Deep sky blue
             .replace(/\${c3}/g, chalk.hex('#FF6347')(''))  // Tomato
             .replace(/\${c4}/g, chalk.hex('#9370DB')(''));  // Medium purple
    
    // Remove the color definition line
    art = art.replace(/colors \d+ \d+ \d+ \d+\n/, '');
    
    return art;
  } catch (error) {
    // Fallback to original if file not found
    return `                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                _a                                                                 
                            _-*  /__@                                                              
                       __="      "  }         ;gg   ag;  _ggg_  gg   gg gg   gg ;ggggg gg   gg     
                     _F            /          [@@   @@| @@@@@@g @@B  @g @@  &@  [@@@@@ [@, [@'     
                   _"               ",        [@@; ;@@| @@  [@@ @@@  @g @@ ,@N  [@      @B @@      
                  /                   ,       [@@@ @@@| @@  [@@ @@@1 @g @@ @@   [@      [@_@'      
                 ,      ___           '       [@h@u@M@| @@  [@@ @@B@_@g @@@@'   [@ggg    @@@       
              ___[    a@@@@@g_  _g@@g, 1_     [@ @@@ @| @@  [@@ @@ @@@g @@B@g   [@@@@    9@F       
             8   "   @@BBB@@@@g@@@@BBB ""f    [@ [@' @| @@  [@@ @@ [@@g @@ @@,  [@       [@|       
            [ ,_                          |   [@  @  @| @@  [@@ @@  @@g @@  @@  [@       [@|       
            [ g t   'g                 !, '   [@  W  @| @@@@@@N @@  @@g @@  [@l [@@@@@   [@|       
            ' @;     g        ,g       ['[    '=  '  ='  <==="  ==  '=* ==   == "=====   "='       
             o[  t   ',      _@@L      &_                                                          
              [@  ,    *__gg" "@""@B"  W                                                           
                4m@,     ,@@gg,[ ggg  ,        _gg  ,gg_   ggg,  ;gg;  ;gg,                        
                   }     @@@@@@@/@@@, N        @    [| @   @ [g  [[_   [1_}                        
                   g    [@@@@@@@@@@@@ [        @__  [1_@   @_[g  [[_   [T"@   g   g   g            
                   '    @@P"   __     [        """   "*"   """   """"  "' "   "   "   "            
                    \\,  "  _@@@@@@@N  '                                                            
              f@L     L   @@@@@@@@W  "                                                             
               '@@,    t,  f@@@@@F  ?                                                              
                 [@L     o_   '   _"                                                               
                 _@F       "=___m"                                                                 
                @@                                                                                 
              _@P                                                                                  
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   `;
  }
}

const MONKEY_ASCII = loadSplashArt();

function printColorizedSplash(): void {
  console.clear();
  console.log('');
  
  // Print the ASCII art directly - it already contains ANSI color codes
  console.log(MONKEY_ASCII);
  
  // Add the MONKEY CODER branding similar to Gemini CLI style
  console.log(chalk.cyan.bold('     ███    ███  ██████  ███    ██ ██   ██ ███████ ██    ██'));
  console.log(chalk.cyan.bold('     ████  ████ ██    ██ ████   ██ ██  ██  ██       ██  ██'));
  console.log(chalk.cyan.bold('     ██ ████ ██ ██    ██ ██ ██  ██ █████   █████     ████'));
  console.log(chalk.cyan.bold('     ██  ██  ██ ██    ██ ██  ██ ██ ██  ██  ██         ██'));
  console.log(chalk.cyan.bold('     ██      ██  ██████  ██   ████ ██   ██ ███████    ██'));
  console.log('');
  console.log(chalk.green.bold('     ██████  ██████  ██████  ███████ ██████'));
  console.log(chalk.green.bold('     ██      ██    ██ ██   ██ ██      ██   ██'));
  console.log(chalk.green.bold('     ██      ██    ██ ██   ██ █████   ██████'));
  console.log(chalk.green.bold('     ██      ██    ██ ██   ██ ██      ██   ██'));
  console.log(chalk.green.bold('     ██████  ██████  ██████  ███████ ██   ██'));
  console.log('');
  
  // Add tips similar to Gemini CLI
  console.log(chalk.dim('Tips for getting started:'));
  console.log(chalk.dim('1. Ask questions, implement features, or run analysis.'));
  console.log(chalk.dim('2. Be specific for the best results.'));
  console.log(chalk.dim('3. Use /help for more information.'));
  console.log('');
}

/**
 * Displays an enhanced splash screen with colorized monkey ASCII art.
 * Features a beautiful hand-crafted monkey artwork with ANSI colors and
 * Gemini CLI-inspired branding.
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
