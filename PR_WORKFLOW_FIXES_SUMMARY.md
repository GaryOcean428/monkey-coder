# PR Workflow Fixes Summary

## Overview
This PR fixes critical issues in GitHub Actions workflows and test infrastructure that were causing PR checks to fail.

## Issues Fixed

### 1. Build Validation Workflow Failures
**Problem:** Tests in `packages/cli/__tests__/tasks.test.ts` were failing with:
```
TypeError: A dynamic import callback was invoked without --experimental-vm-modules
```

**Root Cause:** The `listr2` package uses dynamic imports that require Node.js experimental VM modules flag.

**Solution:**
- Added `--experimental-vm-modules` flag to all test scripts in `packages/cli/package.json`
- Updated `jest.config.cjs` to include `listr2` in `transformIgnorePatterns`
- Fixed `jest.setup.ts` to remove `jest.retryTimes()` which is incompatible with experimental-vm-modules

**Result:** ✅ All 6 tests in tasks.test.ts now pass successfully

### 2. Auto-Publish Workflow Failures
**Problem:** Workflow failed with:
```
error This project's package.json defines "packageManager": "yarn@4.9.2". 
However the current global version of Yarn is 1.22.22.
```

**Root Cause:** Missing `corepack enable` and `corepack prepare` steps before using yarn.

**Solution:**
- Added `corepack enable && corepack prepare yarn@4.9.2 --activate` to all Node.js jobs
- Applied to both `publish-npm-cli` and `publish-npm-sdk` jobs

**Result:** ✅ Yarn version mismatch resolved

### 3. Publish Workflow Issues
**Problem:** Similar yarn version mismatch and incorrect install command.

**Root Cause:** 
- Missing proper corepack setup
- Using `--mode=update-lockfile` instead of `--immutable`

**Solution:**
- Added complete corepack setup: `corepack enable && corepack prepare yarn@4.9.2 --activate`
- Changed install command to `yarn install --immutable`

**Result:** ✅ Consistent with other workflows

### 4. Build Validation Workflow
**Problem:** Incomplete corepack setup.

**Solution:**
- Updated to use full command: `corepack enable && corepack prepare yarn@4.9.2 --activate`

**Result:** ✅ Consistent with other workflows

## Files Changed

### Workflow Files
1. `.github/workflows/auto-publish.yml`
   - Added corepack enable to `publish-npm-cli` job
   - Added corepack enable to `publish-npm-sdk` job

2. `.github/workflows/publish.yml`
   - Added complete corepack setup
   - Fixed yarn install command

3. `.github/workflows/build-validation.yml`
   - Updated corepack enable command

### Test Configuration Files
4. `packages/cli/jest.config.cjs`
   - Added `listr2` to transformIgnorePatterns
   - Added testRunner configuration

5. `packages/cli/package.json`
   - Updated test scripts to use `node --experimental-vm-modules`
   - Applied to: test, test:watch, test:coverage

6. `packages/cli/jest.setup.ts`
   - Removed incompatible `jest.retryTimes()` call
   - Added console log for CI environment

## Test Results

### Before Fixes
- ❌ tasks.test.ts: 4 tests failed with dynamic import errors
- ❌ Build Validation: Failing due to test errors
- ❌ Auto-Publish: Failing due to yarn version mismatch

### After Fixes
- ✅ tasks.test.ts: All 6 tests passing
- ✅ Build Validation: Test infrastructure fixed
- ✅ Auto-Publish: Yarn version properly configured
- ✅ All workflows have consistent corepack setup

## Verification

Run locally:
```bash
# Enable corepack
corepack enable && corepack prepare yarn@4.9.2 --activate

# Install dependencies
yarn install --immutable

# Run CLI tests
cd packages/cli
yarn test __tests__/tasks.test.ts
```

Expected output:
```
Test Suites: 1 passed, 1 total
Tests:       6 passed, 6 total
```

## Related Workflows

These workflows are now properly configured:
- ✅ CI (ci.yml) - Already had correct setup
- ✅ Policy (policy.yml) - Already had corepack steps
- ✅ Railway Deployment Testing - No changes needed
- ✅ Preflight System Limits - No changes needed

## Notes

1. The `--experimental-vm-modules` flag is required for any package using dynamic imports
2. All workflows using yarn must have the complete corepack setup
3. The `jest.retryTimes()` API is not available when using experimental-vm-modules
4. Some other tests may still fail but those are pre-existing issues unrelated to the workflow configuration

## Recommendations

1. Consider migrating away from `listr2` if possible to avoid experimental flags
2. Ensure all new workflows include proper corepack setup
3. Add a workflow template or shared action for Node.js setup to ensure consistency

