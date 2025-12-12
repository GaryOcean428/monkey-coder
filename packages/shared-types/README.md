# @monkey-coder/shared-types

Shared TypeScript types and interfaces used across Monkey Coder services.

## Overview

This package contains common type definitions that are shared between the frontend and backend services, ensuring type consistency and reducing duplication.

## Contents

### API Types (`api.ts`)
- Request/response type definitions
- API endpoint interfaces
- Error type definitions

### Common Types (`common.ts`)
- Shared data structures
- Common enums and constants
- Utility types

## Usage

```typescript
import type { APIResponse, User, ErrorResponse } from '@monkey-coder/shared-types';

// Use types in your code
function handleAPIResponse(response: APIResponse<User>) {
  // Implementation
}
```

## Installation

This package is part of the Monkey Coder monorepo and is managed via Yarn workspaces.

```bash
yarn workspace @monkey-coder/shared-types build
```

## Development

### Building

```bash
yarn build
```

### Type Checking

```bash
yarn typecheck
```

## TypeScript

This package is written in TypeScript with strict mode enabled (inherited from root tsconfig.json).

All types are properly documented with TSDoc comments for better IDE integration.

## Best Practices

1. **Keep types minimal**: Only include types that are truly shared across services
2. **Document thoroughly**: Use TSDoc comments to document all exported types
3. **Version carefully**: Changes to shared types may affect multiple services
4. **Use utility types**: Leverage TypeScript's utility types (Pick, Omit, etc.)

## Dependencies

This package has minimal dependencies to reduce coupling. See `package.json` for details.
