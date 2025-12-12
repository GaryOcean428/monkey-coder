# @monkey-coder/shared-utils

Shared utility functions used across Monkey Coder services.

## Overview

This package contains common utilities that are shared between the frontend and backend services, promoting DRY principles and code reuse.

## Contents

### Logger (`logger.ts`)
- Centralized logging utilities
- Consistent log formatting across services
- Support for different log levels

### Validation (`validation.ts`)
- Common validation functions
- Reusable validation rules
- Type-safe validation utilities

## Usage

```typescript
import { logger, validateEmail } from '@monkey-coder/shared-utils';

// Use logger
logger.info('Application started');

// Use validation
const isValid = validateEmail('user@example.com');
```

## Installation

This package is part of the Monkey Coder monorepo and is managed via Yarn workspaces.

```bash
yarn workspace @monkey-coder/shared-utils build
```

## Development

### Building

```bash
yarn build
```

### Testing

```bash
yarn test
```

## TypeScript

This package is written in TypeScript with strict mode enabled (inherited from root tsconfig.json).

## Dependencies

See `package.json` for the full list of dependencies.
