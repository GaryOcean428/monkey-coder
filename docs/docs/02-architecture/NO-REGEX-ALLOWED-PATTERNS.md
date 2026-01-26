# Allowed Regex Patterns - Documentation

This document lists all regex patterns currently allowed in the codebase under the no-regex-by-default policy.

## Policy Overview

Regex is **disallowed by default**. Exceptions are granted only for:
1. Trivial, fully-anchored literals (max 30 chars, no quantifiers that could backtrack)
2. Validation use cases where no standard library exists
3. Compile-time constants only (never dynamic construction)
4. Patterns with no catastrophic backtracking risk

## Allowed Patterns

### packages/web/src/lib/validation.ts

#### Username Validation
```typescript
/^[a-zA-Z0-9_]+$/
```
- **Purpose:** Validate username contains only alphanumeric characters and underscores
- **Justification:** Simple character class, anchored, no backtracking risk
- **Type:** Validation
- **Location:** Line 44

#### Name Validation
```typescript
/^[a-zA-Z\s\-']+$/
```
- **Purpose:** Validate name contains only letters, spaces, hyphens, and apostrophes
- **Justification:** Simple character class, anchored, no backtracking risk
- **Type:** Validation
- **Location:** Line 111

#### Password Strength Checks
```typescript
/[A-Z]/      // Uppercase letter
/[a-z]/      // Lowercase letter
/\d/         // Digit
/[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/  // Special character
```
- **Purpose:** Check password contains required character types
- **Justification:** Simple character class checks, no anchoring needed, no backtracking risk
- **Type:** Validation
- **Location:** Lines 68-71

### packages/web/src/components/ui/password-strength.tsx

#### Password Strength Indicators
```typescript
/[A-Z]/      // Has uppercase
/[a-z]/      // Has lowercase
/\d/         // Has digit
/[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/  // Has special character
```
- **Purpose:** Check password strength criteria for UI indicators
- **Justification:** Same as validation.ts, simple character class checks
- **Type:** Validation/UI
- **Location:** Lines 19-22

### packages/web/src/constants/colors.ts

#### Hex Color Validation
```typescript
/^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/
```
- **Purpose:** Validate hex color format (#RGB or #RRGGBB)
- **Justification:** Anchored, exact length alternatives, no backtracking risk
- **Type:** Validation
- **Location:** Line 5 (approximate)

## Replaced Patterns (No Longer in Use)

### Email Validation (REPLACED)
```typescript
// OLD (REMOVED - had super-linear backtracking issue):
/^[^\s@]+@[^\s@]+\.[^\s@]+$/

// NEW (using validator library):
import validator from 'validator';
validator.isEmail(email)
```
- **Reason for replacement:** Super-linear backtracking vulnerability
- **Replacement:** `validator.isEmail()` from validator package
- **Locations:** validation.ts, live-code-generator.tsx

### Phone Number Sanitization (REPLACED)
```typescript
// OLD (REMOVED):
phone.replace(/\D/g, '')

// NEW (using string methods):
phone.split('').filter(char => char >= '0' && char <= '9').join('')
```
- **Reason for replacement:** No-regex-by-default policy prefers string methods
- **Replacement:** String filter method
- **Locations:** validation.ts

### Time Digit Extraction (REPLACED)
```typescript
// OLD (REMOVED):
estimatedTime.replace(/\D/g, '')

// NEW (using string methods):
estimatedTime.split('').filter(char => char >= '0' && char <= '9').join('')
```
- **Reason for replacement:** No-regex-by-default policy prefers string methods
- **Replacement:** String filter method
- **Locations:** live-code-generator.tsx

## Testing Requirements

All allowed regex patterns should have:

1. **Unit tests** covering:
   - Valid inputs (positive cases)
   - Invalid inputs (negative cases)
   - Edge cases (empty, very long, special characters)

2. **Property-based tests** (recommended with fast-check):
   ```typescript
   import fc from 'fast-check';
   
   fc.assert(fc.property(fc.string(), (input) => {
     const result = validateUsername(input);
     // Should never throw or hang
     return typeof result === 'string' || result === undefined;
   }));
   ```

3. **Performance tests** (for patterns used in hot paths):
   - Ensure no exponential time complexity
   - Test with large inputs (10KB+)

## Review Process

When adding a new regex pattern:

1. **Open PR** with justification in description
2. **Document here** in this file
3. **Add tests** (unit + property-based)
4. **Get approval** from maintainers
5. **Add inline comment** in code referencing this document

## Maintenance

This document should be updated whenever:
- A regex pattern is added
- A regex pattern is removed
- A regex pattern is modified
- An exception is granted

Last updated: 2025-10-21
