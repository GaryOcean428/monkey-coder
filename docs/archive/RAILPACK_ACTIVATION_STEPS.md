# Railpack Activation Steps

## Important: Railpack Configuration Requirements

Railpack is Railway's next-generation builder (successor to Nixpacks) currently in beta. It **CANNOT** be configured via `railway.toml` or `railway.json` files using the `builder` field.

## Manual Dashboard Configuration Steps

1. Go to Railway Dashboard → Your Project → monkey-coder service
2. Click "Settings" tab
3. Scroll to "Builds" section
4. Find "Builder" dropdown/toggle
5. Select "Railpack" (currently in Beta)
6. Click "Save" or "Apply"

**Note:** This CANNOT be done via railway.toml - must use dashboard UI

## Project Compatibility

Railpack supports: Node, Python, Go, PHP, Static HTML
✅ **Your project: Python monorepo with AI dependencies - SUPPORTED**

## Configuration Files

- `railpack.json` - Railpack-specific configuration (present in repo)
- Remove any `builder = "railpack"` lines from railway.toml (if present)
- Railpack uses its own JSON configuration format

## Expected Benefits

After enabling Railpack:
- 77% smaller Python images compared to Nixpacks
- Improved dependency caching with BuildKit integration
- Better cache hits across environments
- Faster builds for Python monorepo projects

## Troubleshooting

If you see "build.builder: Invalid input" error:
1. Check that no railway.toml contains `builder = "railpack"`
2. Enable Railpack via dashboard instead of config files
3. Ensure railpack.json uses proper schema