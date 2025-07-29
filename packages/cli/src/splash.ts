import fs from 'fs';
import path from 'path';
import chalk from 'chalk';
import { fileURLToPath } from 'url';
import { ConfigManager } from './config.js';

// ES module equivalent of __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const MONKEY_ASCII = `                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
[38;5;183m                                _a                                                                 
                            _-*  /__@                                                              
                       __="      "  }         [38;5;173m;gg   ag;  _ggg_  gg   gg gg   gg ;ggggg gg   gg     
                     [38;5;183m_F            /          [38;5;173m[@@   @@| @@@@@@g @@B  @g @@  &@  [@@@@@ [@, [@'     
                   [38;5;183m_"               ",        [38;5;173m[@@; ;@@| @@  [@@ @@@  @g @@ ,@N  [@      @B @@      
                  [38;5;183m/                   ,       [38;5;173m[@@@ @@@| @@  [@@ @@@1 @g @@ @@   [@      [@_@'      
                 [38;5;183m,      ___           '       [38;5;173m[@h@u@M@| @@  [@@ @@B@_@g @@@@'   [@ggg    @@@       
              [38;5;183m___[    a@@@@@g_  _g@@g, 1_     [38;5;173m[@ @@@ @| @@  [@@ @@ @@@g @@B@g   [@@@@    9@F       
             [38;5;183m8   "   @@BBB@@@@g@@@@BBB ""f    [38;5;173m[@ [@' @| @@  [@@ @@ [@@g @@ @@,  [@       [@|       
            [38;5;183m[ ,_                          |   [38;5;173m[@  @  @| @@  [@@ @@  @@g @@  @@  [@       [@|       
            [38;5;183m[ g t   'g                 !, '   [38;5;173m[@  W  @| @@@@@@N @@  @@g @@  [@l [@@@@@   [@|       
            [38;5;183m' @;     g        ,g       ['[    [38;5;173m'=  '  ='  <==="  ==  '=* ==   == "=====   "='       
             [38;5;183mo[  t   ',      _@@L      &_                                                          
              [@  ,    *__gg" "@""@B"  W                                                           
                4m@,     ,@@gg,[ ggg  ,        [38;5;154m_gg  ,gg_   ggg,  ;gg;  ;gg,                        
                   [38;5;183m}     @@@@@@@/@@@, N        [38;5;154m@    [| @   @ [g  [[_   [1_}                        
                   [38;5;183mg    [@@@@@@@@@@@@ [        [38;5;154m@__  [1_@   @_[g  [[_   [T"@   g   g   g            
                   [38;5;183m'    @@P"   __     [        [38;5;154m"""   "*"   """   """"  "' "   "   "   "            
                    [38;5;183m\\,  "  _@@@@@@@N  '                                                            
              [38;5;208mf@L     [38;5;183mL   @@@@@@@@W  "                                                             
               [38;5;208m'@@,    [38;5;183mt,  f@@@@@F  ?                                                              
                 [38;5;208m[@L     [38;5;183mo_   '   _"                                                               
                 [38;5;208m_@F       [38;5;183m"=___m"                                                                 
                [38;5;208m@@                                                                                 
              _@P                                                                                  
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   
                                                                                                   [0m
`;

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