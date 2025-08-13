[← Back to Roadmap Index](../roadmap.md)

## Current Development 🚧

### Post-Merge Update (2025-08-08)

- Quantum Routing Engine branch merged into main; conflicts resolved.
  - Preserved protected packages/core/monkey_coder/models.py from HEAD.
  - Normalized .gitignore and removed committed Next.js build artifacts (.next/, out/).
  - Integrated commits from copilot/fix-29 (DQN training pipeline, tests) and resolved overlaps in quantum modules.
  - Consolidated branches: only main remains locally and on origin.
- Workspace state
  - Yarn 4.9.2 install successful across workspaces.
  - ESLint v9 migration warnings for root/cli/sdk (missing eslint.config.js); web lints clean but suggests adding Next.js ESLint plugin.
  - Tests: web workspace lacks Jest/Vitest test runner; CLI has one failing expectation in __tests__/install.test.ts regarding CI log message; Python core installs editable and test infra is present.

#### Follow-ups Implemented (2025-08-08, later)

- P0 Testing and CI gate (Completed)
  - Web: Migrated to next/jest with jsdom; added jest.setup.ts and file mocks; fixed Vitest-based test to Jest with TS-safe guards.
  - CLI: Postinstall CI detection message standardized; CLI install tests pass.
  - Monorepo: yarn test runs across workspaces; SDK has no tests but exits 0.
- CI pipeline (Completed)
  - Added .github/workflows/ci.yml with Node (Yarn 4) and Python (pytest) jobs.
  - CI now uploads coverage and JUnit artifacts for Node (CLI/Web/SDK) and Python core.
  - Added quantum test subset JUnit artifact to track quantum routing health.
- ESLint (Completed)
  - Root flat eslint.config.js to address v9 migration warnings; excludes web (Next-managed lint).
  - Flat configs for CLI and SDK with @typescript-eslint; lint scripts updated for TS.

#### Next Steps (updated, prioritized)

P0 (Quality gates & reliability)
- Enforce coverage thresholds in CI:
  - Jest: Configure coverageThreshold in web/cli to prevent regressions.
  - Pytest: Add --cov-fail-under baseline in Python core when metrics stabilize.
- CI annotations:
  - Add a GitHub summary step (e.g., dorny/test-reporter) to render uploaded JUnit files for quick triage.
- Flakiness watch:
  - Introduce a retry-once strategy in CI for known flaky suites (if any emerge) with reporting.

P1 (Quantum & metrics hardening)
- Quantum metrics baseline:
  - Extend core tests to output performance metrics; archive artifacts per run for time-series trend analysis.
  - Define SLOs for quantum routing latency and success rates; alert on regressions (GitHub PR checks).
- Expand Python tests:
  - Add integration tests covering router_integration and collapse strategies under load-mocked scenarios.

P1 (Product & security backlog)
- Backend cookie auth parity:
  - Complete server-side httpOnly cookie handling and component migration to new auth system (as tracked in roadmap).
- Stripe integration & dashboard:
  - Progress web Stripe flows and user dashboard features (payments, usage, API keys).

P2 (DX & docs)
- Add JUnit and coverage badges in README/docs.
- Add contributor guide for running tests locally and interpreting CI artifacts.
- Improve Next ESLint rules in web once flat-config compatibility is confirmed.

#### Immediate Next Steps (prioritized)

1) P0 Testing and CI gate
   - Add test runner to web (Jest + @testing-library/react or Vitest) and provide "test" script.
   - Fix CLI postinstall CI-mode path: either log "CI environment detected" when process.env.CI is set or update the test to assert the new output, while still verifying no network calls.
   - Add GitHub Actions workflow to run lint/tests for all workspaces (yarn workspaces foreach -A) and pytest for packages/core; block merges on red.

2) P0 ESLint v9 migration
   - Add eslint.config.js to root, packages/cli, and packages/sdk (or pin ESLint v8 temporarily).
   - In web, enable @next/eslint-plugin-next in config.

3) P1 Quantum validation
   - Run and stabilize quantum tests in packages/core/tests/quantum (experience_buffer, dqn_agent, training_pipeline) in CI; record baseline metrics.

4) P1 DX hardening
   - Ensure .gitignore includes .next/ and out/ in all relevant paths; add typecheck scripts in web/cli/sdk; ensure scripts don’t fail when a workspace has no tests.
