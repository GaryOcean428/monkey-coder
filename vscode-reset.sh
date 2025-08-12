#!/bin/bash
# VS Code Troubleshooting Script

echo "🔧 VS Code Performance Reset Script"
echo "=================================="

# Kill any running VS Code processes
echo "1. Stopping VS Code processes..."
pkill -f "code-insiders" || echo "No VS Code Insiders processes found"
pkill -f "code" || echo "No VS Code processes found"

# Clear extension host cache
echo "2. Clearing extension cache..."
rm -rf ~/.vscode-insiders/CachedExtensions
rm -rf ~/.vscode-insiders/logs
rm -rf ~/.vscode-insiders/CachedData

# Clear workspace cache
echo "3. Clearing workspace cache..."
rm -rf ~/.config/Code\ -\ Insiders/CachedData
rm -rf ~/.config/Code\ -\ Insiders/logs

# Clear TypeScript cache
echo "4. Clearing TypeScript cache..."
rm -rf node_modules/.cache
find . -name "*.tsbuildinfo" -delete
find . -name ".eslintcache" -delete

# Clear Copilot cache
echo "5. Clearing Copilot cache..."
rm -rf ~/.config/github-copilot

echo "6. Performance tips:"
echo "   - Restart VS Code after running this script"
echo "   - Try disabling/re-enabling Copilot extension if issues persist"
echo "   - Use Ctrl+Shift+P -> 'Developer: Reload Window' for soft restart"
echo "   - Use Ctrl+` to open/close terminal panel"

echo "✅ Reset complete! Now restart VS Code."