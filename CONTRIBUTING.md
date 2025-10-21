# Contributing to Monkey Coder

Thank you for your interest in contributing to Monkey Coder! This document outlines our development practices and guidelines.

## Table of Contents

- [Development Setup](#development-setup)
- [No-Regex-by-Default Policy](#no-regex-by-default-policy)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Commit Message Guidelines](#commit-message-guidelines)

## Development Setup

### Prerequisites

- **Node.js:** ≥20.0.0 (use Node 20 LTS recommended)
- **Python:** 3.12 (for core package)
- **Yarn:** 4.9.2 (managed via Corepack)
- **Git:** Latest stable version

### Setup Instructions

```bash
# 1. Clone the repository
git clone https://github.com/GaryOcean428/monkey-coder.git
cd monkey-coder

# 2. Enable Corepack and activate Yarn 4.9.2
corepack enable
corepack prepare yarn@4.9.2 --activate

# 3. Install dependencies
yarn install

# 4. Build all packages
yarn build

# 5. Run tests
yarn test

# 6. Start development server
yarn dev
```

For more detailed setup instructions, see [AGENTS.md](./AGENTS.md).

## No-Regex-by-Default Policy

**Use parsers and typed APIs. Regex only for tiny, anchored literals with no quantifiers.**

### Why This Policy?

Regular expressions are:
- **Brittle:** Small changes break them
- **Slow to review:** Hard to understand and verify
- **Often wrong:** Especially for parsing structured data (DOM/HTML/JSON/URLs/logs)
- **Security risks:** Vulnerable to ReDoS (catastrophic backtracking)

We standardize on **parsers and typed APIs** for all structured data.

### Policy Rules

#### ❌ Disallowed (must refactor)

- **DOM selection via regex** (use Playwright/Testing Library locators)
- **Parsing JSON/URLs/HTML/CSV/logs with regex**
- **Catch-all patterns** like `.*`, nested groups, lookbehinds
- **Backtracking-prone groups**
- **Dynamic RegExp construction:** `new RegExp(userInput)` or untrusted input in patterns

#### ✅ Allowed (narrow, anchored exceptions)

Regex is permitted **only** for:

1. **Trivial, fully-anchored literals** (max length 30, no quantifiers)
   - Examples:
     - `const STATUS = /^(OK|FAIL)$/;` ✓
     - `const CODE = /^[A-Z]{3}-\d{4}$/;` ✓ (exact length, no `+` or `*`)
     - `const HEX_COLOR = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/;` ✓
   
2. **Validation only** (not parsing) where no standard library exists

3. **Compile-time constants only** (never dynamic construction)

4. **Must be documented** in PR description with justification

5. **Prefer RE2-style engine** if available (safe, no backtracking)

### Preferred Replacements

#### JavaScript/TypeScript

| Instead of Regex | Use This |
|-----------------|----------|
| DOM selection | `page.getByRole()`, `page.getByTestId()`, Testing Library locators |
| URLs/query params | `new URL()`, `URLSearchParams` |
| JSON parsing | `JSON.parse()`, schema validation (Zod/Valibot) |
| HTML scraping | `DOMParser`, `cheerio`, server-side `linkedom` |
| CSV/TSV | `csv-parse`, `PapaParse` |
| Dates | `date-fns`, `luxon` |
| Paths/globs | `path` module, `fast-glob` |
| Email/phone/IBAN | `validator` package |
| String search | `includes()`, `startsWith()`, `endsWith()` |
| String extraction | `split()`, `substring()`, `slice()` |

#### Python

| Instead of Regex | Use This |
|-----------------|----------|
| URLs/query params | `urllib.parse` |
| JSON parsing | `json` module + `pydantic` validation |
| HTML scraping | `BeautifulSoup`, `lxml` |
| CSV parsing | `csv` module |
| Dates | `dateutil`, `pendulum` |
| Paths | `pathlib`, `glob` |
| If truly needed | `re2` package (safe engine), keep patterns tiny/anchored |

### Examples

#### ✅ Good: Using Standard APIs

```typescript
// URL parsing
const url = new URL(location.href);
const q = url.searchParams.get('q');

// JSON parsing
const data = JSON.parse(body);
const id = data.id;

// Email validation
import { isEmail } from 'validator';
if (isEmail(email)) { /* ... */ }

// DOM selection (Playwright)
await page.getByRole('button', { name: 'Submit' });
await page.getByTestId('submit-btn');

// String checks
if (str.includes('error')) { /* ... */ }
if (str.startsWith('prefix')) { /* ... */ }
```

#### ❌ Bad: Regex for Structured Data

```typescript
// DON'T: Regex for URL parsing
const q = location.href.match(/[?&]q=([^&]+)/)?.[1];

// DON'T: Regex for JSON
const id = body.match(/"id":"(\w+)"/)?.[1];

// DON'T: Regex for HTML scraping
const titles = html.match(/<h2>(.*?)<\/h2>/g);

// DON'T: Homegrown email validation
const isEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s);
```

#### ✅ Allowed Exception: Simple Validation

```typescript
// Password strength checks - ALLOWED (validation, anchored, literal)
const hasUppercase = /[A-Z]/.test(password);
const hasLowercase = /[a-z]/.test(password);
const hasDigit = /\d/.test(password);
const hasSpecial = /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(password);

// Username validation - ALLOWED (anchored, literal, no quantifiers risk)
const isValidUsername = /^[a-zA-Z0-9_]+$/.test(username);

// Hex color validation - ALLOWED (anchored, literal)
const isHexColor = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/.test(color);
```

### Adding a New Regex

If you must add a regex pattern:

1. **Justify in PR description:** Explain why no standard API or library works
2. **Keep it anchored:** Use `^` and `$` to prevent partial matches
3. **Keep it short:** Maximum 30 characters
4. **No lookbehind/lookahead:** These are slow and error-prone
5. **No backtracking risk:** Avoid nested groups, `.*`, or `(.*)+` patterns
6. **Add property-based tests:** Use `fast-check` to fuzz inputs

```typescript
import fc from 'fast-check';

// Property test for regex
fc.assert(fc.property(fc.string(), (input) => {
  // Function should never throw or hang
  const result = validateWithRegex(input);
  return typeof result === 'boolean';
}));
```

### Enforcement

The policy is enforced via:

1. **ESLint rules** (`eslint-plugin-regexp`)
   - Flags catastrophic backtracking patterns
   - Warns on `String.match()`, `.replace()`, `.search()` with regex
   - Errors on `new RegExp()` and nested groups

2. **Pre-commit hooks** (Husky)
   - Runs linting and type checking
   - Prevents commits with policy violations

3. **CI workflows** (GitHub Actions)
   - Fails PRs that violate the policy
   - Checks for forbidden regex patterns

## Code Style

### TypeScript/JavaScript

- Use **strict mode** with full type coverage
- Follow ESLint configuration
- Write unit tests for new features
- Use meaningful variable names
- Prefer `const` over `let`
- Use async/await over callbacks

### Python

- Follow **PEP 8** (enforced by Black)
- Use **type hints** for all functions
- Write **docstrings** for public APIs
- Use async/await for I/O operations

### Formatting

We use Prettier for JavaScript/TypeScript and Black for Python:

```bash
# Format all files
yarn format

# Check formatting
yarn format:check
```

## Testing

### Running Tests

```bash
# Run all tests
yarn test

# Run tests in watch mode
yarn test:watch

# Run tests with coverage
yarn test:coverage

# Test specific package
yarn workspace @monkey-coder/cli test
yarn workspace @monkey-coder/web test
```

### Writing Tests

- **TypeScript/JavaScript:** Use Jest + React Testing Library
- **Python:** Use pytest
- **Minimum coverage:** 70% for critical paths
- **Test file naming:** `*.test.ts` or `*.spec.ts`

Example test structure:

```typescript
import { describe, it, expect } from '@jest/globals';

describe('Feature', () => {
  it('should validate input correctly', () => {
    const result = validateInput('test');
    expect(result).toBe(true);
  });
});
```

## Pull Request Process

1. **Fork the repository** and create a feature branch
2. **Follow the no-regex policy** and coding standards
3. **Write tests** for new functionality
4. **Run linting:** `yarn lint:fix`
5. **Run tests:** `yarn test`
6. **Commit with conventional format:** `feat(scope): description`
7. **Push and create PR** with clear description
8. **Address review feedback**

### PR Checklist

- [ ] Tests pass locally (`yarn test`)
- [ ] Linting passes (`yarn lint`)
- [ ] Type checking passes (`yarn typecheck`)
- [ ] No regex violations (or documented exceptions)
- [ ] Documentation updated (if needed)
- [ ] Breaking changes documented
- [ ] Security implications reviewed

## Commit Message Guidelines

We use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Build process or auxiliary tool changes
- `perf`: Performance improvements

### Scopes

- `cli`: CLI package changes
- `core`: Python core package changes
- `web`: Web frontend changes
- `sdk`: SDK package changes
- `deploy`: Deployment configuration
- `docs`: Documentation

### Examples

```bash
feat(cli): add new command for code analysis
fix(web): resolve authentication redirect issue
docs(readme): update setup instructions
refactor(sdk): simplify API client initialization
test(cli): add property tests for validation functions
```

## Questions?

If you have questions about contributing, please:

1. Check the [AGENTS.md](./AGENTS.md) for detailed development guide
2. Search existing [GitHub Issues](https://github.com/GaryOcean428/monkey-coder/issues)
3. Open a new issue with the `question` label

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
