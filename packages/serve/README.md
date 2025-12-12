# @monkey-coder/serve

Static file server package for serving the Monkey Coder frontend application.

## Overview

This package provides a lightweight static file server used to serve the Next.js static export build in production environments.

## Usage

The serve binary is used in the deployment process to serve the static frontend files:

```bash
serve -s out -l $PORT --no-clipboard
```

## Configuration

Server configuration is managed through `serve.json` at the project root.

## Deployment

This package is used in Railway deployment via the `railpack.json` configuration:

```json
{
  "deploy": {
    "startCommand": "npx serve -s out -l $PORT --no-clipboard"
  }
}
```

## Environment Variables

- `PORT`: The port to bind to (provided by Railway in production)

## Features

- Serves static files efficiently
- Supports SPA routing with proper fallbacks
- Configurable via `serve.json`
- Lightweight and fast

## Dependencies

See `package.json` for the full list of dependencies.
