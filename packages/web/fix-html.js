const fs = require('fs');
const path = require('path');

// Read the HTML file
const htmlPath = path.join(__dirname, 'out', 'index.html');
let html = fs.readFileSync(htmlPath, 'utf8');

// Fix 1: Remove fetchpriority="low" attributes
html = html.replace(/fetchpriority="low"/g, '');

// Fix 2: Remove all inline style attributes from any element
html = html.replace(/ style="[^"]*"/g, '');

// Fix 3: Remove manifest link
html = html.replace(/<link rel="manifest" href="\/site\.webmanifest"[^>]*>/g, '');

// Fix 4: Remove apple-touch-icon link
html = html.replace(/<link rel="apple-touch-icon" href="\/android-chrome-192x192\.png"[^>]*>/g, '');

// Write the fixed HTML back
fs.writeFileSync(htmlPath, html);

console.log('HTML file fixed successfully!');
