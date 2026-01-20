/**
 * Terminal capability detection utilities
 */

/**
 * Check if the terminal supports interactive features
 */
export function isInteractiveTerminal(): boolean {
  // Check if stdout is a TTY
  if (!process.stdout.isTTY) {
    return false;
  }

  // Check for CI/automation environments
  const ciEnvVars = [
    'CI',
    'CONTINUOUS_INTEGRATION',
    'GITHUB_ACTIONS',
    'GITLAB_CI',
    'CIRCLECI',
    'TRAVIS',
    'JENKINS_URL',
    'BUILDKITE',
  ];

  if (ciEnvVars.some((varName) => process.env[varName])) {
    return false;
  }

  // Check for dumb terminal
  if (process.env.TERM === 'dumb') {
    return false;
  }

  return true;
}

/**
 * Check if the terminal supports colors
 */
export function supportsColor(): boolean {
  if (!process.stdout.isTTY) {
    return false;
  }

  if (process.platform === 'win32') {
    // Windows 10+ supports ANSI colors
    return true;
  }

  if (process.env.COLORTERM === 'truecolor') {
    return true;
  }

  const term = process.env.TERM || '';
  if (term.includes('color') || term.includes('256')) {
    return true;
  }

  return false;
}

/**
 * Get terminal width (columns)
 */
export function getTerminalWidth(): number {
  return process.stdout.columns || 80;
}

/**
 * Get terminal height (rows)
 */
export function getTerminalHeight(): number {
  return process.stdout.rows || 24;
}

/**
 * Check if terminal supports Unicode
 */
export function supportsUnicode(): boolean {
  if (process.platform !== 'win32') {
    const env = process.env.LC_ALL || process.env.LC_CTYPE || process.env.LANG || '';
    return /utf-?8/i.test(env);
  }

  return true;
}

/**
 * Get appropriate spinner type based on terminal capabilities
 */
export function getSpinnerType(): 'dots' | 'line' | 'simple' {
  if (!isInteractiveTerminal()) {
    return 'simple';
  }

  if (supportsUnicode()) {
    return 'dots';
  }

  return 'line';
}
