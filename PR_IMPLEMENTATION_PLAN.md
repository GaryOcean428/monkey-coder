# PR Implementation Plan - Repository Holistic Improvements

## Overview
This plan addresses the findings from the comprehensive repository audit, implementing critical security fixes, deployment improvements, and code quality enhancements through a series of focused commits.

## Commit Sequence (Conventional Commit Format)

### Phase 1: Critical Security & Deployment Fixes 🔴

#### 1. `security(config): replace hard-coded secrets with environment variables`
**Scope:** Root, packages/core, packages/web  
**Priority:** CRITICAL  
**Changes:**
- Remove hard-coded `SECRET_KEY` and `NEXTAUTH_SECRET` values
- Add proper environment variable fallbacks
- Update `.env.example` files

**Files:**
- `.env.example` (create)
- `packages/core/monkey_coder/config/env_config.py`
- `packages/web/.env.example` (update)
- `railpack.json` (remove hard-coded values)

#### 2. `security(cors): fix wildcard CORS configuration for production`
**Scope:** packages/core  
**Priority:** CRITICAL  
**Changes:**
- Replace `allow_origins: ["*"]` with specific domains
- Add environment-based CORS configuration
- Implement Railway domain support

**Files:**
- `packages/core/monkey_coder/config/cors.py`
- `packages/core/monkey_coder/app/main.py`

#### 3. `deploy(railway): implement proper inter-service communication`
**Scope:** railpack.json, packages/core  
**Priority:** CRITICAL  
**Changes:**
- Use Railway domain variables for service URLs
- Configure WebSocket SSL support
- Add proper health check endpoints

**Files:**
- `railpack.json`
- `packages/core/monkey_coder/config/railway_config.py` (create)

### Phase 2: Code Quality & Build System 🟡

#### 4. `build(typescript): enable strict mode across all packages`
**Scope:** packages/cli, packages/web, packages/sdk  
**Priority:** HIGH  
**Changes:**
- Update `tsconfig.json` files to enable strict mode
- Fix type errors revealed by strict mode
- Add consistent ESLint configuration

**Files:**
- `packages/cli/tsconfig.json`
- `packages/web/tsconfig.json`
- `packages/sdk/tsconfig.json`
- `eslint.config.js` (update)

#### 5. `style(python): add Black and Ruff configuration`
**Scope:** packages/core, root  
**Priority:** HIGH  
**Changes:**
- Add `pyproject.toml` configuration for Black and Ruff
- Create pre-commit hooks for Python formatting
- Format existing Python code

**Files:**
- `pyproject.toml` (update)
- `.pre-commit-config.yaml` (create)
- Python files in `packages/core/` (format)

#### 6. `refactor(core): split large main.py into modular components`
**Scope:** packages/core  
**Priority:** HIGH  
**Changes:**
- Split 3200+ line `main.py` into focused modules
- Create separate files for routes, middleware, startup
- Maintain backward compatibility

**Files:**
- `packages/core/monkey_coder/app/main.py` (reduce to <200 lines)
- `packages/core/monkey_coder/app/routes/` (create module)
- `packages/core/monkey_coder/app/middleware/` (create module)
- `packages/core/monkey_coder/app/startup.py` (create)

### Phase 3: Testing Infrastructure 🟢

#### 7. `test(core): implement comprehensive pytest configuration`
**Scope:** packages/core, root  
**Priority:** MEDIUM  
**Changes:**
- Set up pytest with async support
- Add test database configuration
- Create test fixtures for common scenarios

**Files:**
- `packages/core/pytest.ini`
- `packages/core/conftest.py`
- `packages/core/tests/` (create directory structure)

#### 8. `test(integration): add API endpoint integration tests`
**Scope:** tests/  
**Priority:** MEDIUM  
**Changes:**
- Create integration test suite
- Add tests for authentication flow
- Add tests for core orchestration endpoints

**Files:**
- `tests/integration/` (create)
- `tests/integration/test_auth_flow.py`
- `tests/integration/test_orchestration.py`

#### 9. `test(e2e): implement Cypress for web UI testing`
**Scope:** packages/web  
**Priority:** MEDIUM  
**Changes:**
- Add Cypress configuration
- Create basic user journey tests
- Add CI integration for E2E tests

**Files:**
- `packages/web/cypress.config.js`
- `packages/web/cypress/e2e/` (create)
- `.github/workflows/e2e-tests.yml` (create)

### Phase 4: Documentation & Development Experience 📚

#### 10. `docs(setup): create comprehensive AGENTS.md guide`
**Scope:** root  
**Priority:** MEDIUM  
**Changes:**
- Create detailed setup and development guide
- Include Railway deployment instructions
- Add troubleshooting section

**Files:**
- `AGENTS.md` (create)

#### 11. `docs(packages): add README files for all packages`
**Scope:** packages/*  
**Priority:** MEDIUM  
**Changes:**
- Create package-specific README files
- Document APIs and usage patterns
- Add development setup instructions

**Files:**
- `packages/cli/README.md`
- `packages/core/README.md`
- `packages/web/README.md`
- `packages/sdk/README.md`

#### 12. `ci(quality): implement automated code quality checks`
**Scope:** .github/workflows  
**Priority:** MEDIUM  
**Changes:**
- Add GitHub Actions for linting and testing
- Implement security scanning
- Add dependency vulnerability checks

**Files:**
- `.github/workflows/quality-checks.yml`
- `.github/workflows/security-scan.yml`

## Implementation Order Rationale

1. **Security First**: Critical security vulnerabilities pose immediate risk
2. **Deployment Stability**: Railway configuration issues block production deployments
3. **Code Quality**: Foundation for maintainable development
4. **Testing**: Ensures reliability as codebase grows
5. **Documentation**: Improves developer experience and onboarding

## Risk Assessment

### Low Risk Changes:
- Documentation updates
- Linting configuration
- Test additions

### Medium Risk Changes:
- TypeScript strict mode (may reveal type errors)
- Python formatting (large diff but safe)

### High Risk Changes:
- CORS configuration changes (could break frontend)
- Secret management changes (requires environment setup)
- Main.py refactoring (complex dependencies)

## Rollback Strategy

Each commit includes:
- Clear commit message with scope
- Backwards compatibility where possible
- Environment variable fallbacks
- Configuration validation

Critical changes include environment variable fallbacks to prevent service interruption.

## Testing Strategy

Before each commit:
1. Run existing test suites
2. Validate Railway deployment configuration
3. Test health endpoints
4. Verify environment variable handling

## Deployment Checklist

After implementation:
- [ ] Railway environment variables configured
- [ ] CORS origins updated for production
- [ ] Health checks responding correctly
- [ ] Security headers active
- [ ] Performance monitoring functional

This plan provides a systematic approach to implementing the audit recommendations while minimizing risk and maintaining service availability.