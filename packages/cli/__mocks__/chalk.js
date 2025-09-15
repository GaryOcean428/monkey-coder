// Mock chalk for Jest testing
const chalk = {
  red: (str) => str,
  green: (str) => str,
  blue: (str) => str,
  yellow: (str) => str,
  magenta: (str) => str,
  cyan: (str) => str,
  white: (str) => str,
  gray: (str) => str,
  grey: (str) => str,
  bold: (str) => str,
  dim: (str) => str,
  italic: (str) => str,
  underline: (str) => str,
  strikethrough: (str) => str,
  reset: (str) => str,
  inverse: (str) => str,
  bgRed: (str) => str,
  bgGreen: (str) => str,
  bgBlue: (str) => str,
  bgYellow: (str) => str,
  bgMagenta: (str) => str,
  bgCyan: (str) => str,
  bgWhite: (str) => str,
  blackBright: (str) => str,
  redBright: (str) => str,
  greenBright: (str) => str,
  yellowBright: (str) => str,
  blueBright: (str) => str,
  magentaBright: (str) => str,
  cyanBright: (str) => str,
  whiteBright: (str) => str,
};

// Chain methods for compatibility
Object.keys(chalk).forEach(key => {
  if (typeof chalk[key] === 'function') {
    Object.keys(chalk).forEach(innerKey => {
      if (typeof chalk[innerKey] === 'function') {
        chalk[key][innerKey] = chalk[innerKey];
      }
    });
  }
});

module.exports = chalk;
module.exports.default = chalk;