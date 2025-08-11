# Next Tasks (Actionable Backlog) – August 2025

This document enumerates the immediate, concrete tasks derived from the updated roadmap (docs/roadmap.md). Each task includes clear acceptance criteria, suggested owners, and references.

## Priority P0 – Quality Gates & Reliability

1) Enforce Coverage Thresholds in CI (Jest + Pytest)
- Description:
  - Configure Jest coverageThreshold for packages/web and packages/cli.
  - Configure Pytest to fail under an agreed baseline with --cov-fail-under for packages/core.
- Acceptance Criteria:
  - Web (Jest): coverageThreshold set in jest config; CI fails when lines/branches fall below baseline.
  - CLI (Jest): coverageThreshold set similarly.
  - Core (Pytest): --cov-fail-under=<N> added to CI; baseline recorded in docs.
- Owner: QA + Repo Maintainer
- Refs: .github/workflows/ci.yml; packages/web/jest.config.js; packages/cli/jest config or package.json scripts.

2) CI Annotations – Test Summaries from JUnit
- Description:
  - Add a CI step to parse uploaded JUnit artifacts and post summary annotations on PRs.
- Acceptance Criteria:
  - On each CI run, a summary comment (or job summary) displays suite/test pass/fail counts with pointers to artifacts.
- Suggested Tools:
  - dorny/test-reporter (GH Action) or similar.
- Owner: DevOps
- Refs: .github/workflows/ci.yml; JUnit artifacts already uploaded.

3) Flakiness Watch (Retries + Reporting)
- Description:
  - Add one retry for flaky suites and capture flake metrics.
- Acceptance Criteria:
  - CI config supports a single retry for known flaky paths; a nightly job logs any tests that required retries.
- Owner: QA/DevOps
- Refs: Jest reporters; GH Actions strategy matrix (optional).

## Priority P1 – Quantum & Metrics Hardening

4) Quantum Metrics Baseline & Trend Reporting
- Description:
  - Extend core quantum tests to emit performance counters (latency, success rates, score distributions) to JSON/CSV artifacts.
  - Add a CI artifact retention and a simple script to compare current vs. last baseline (regression alert).
- Acceptance Criteria:
  - packages/core tests output metrics.json (or CSV) with key KPIs.
  - A comparison report is generated in CI; non-blocking initially, later used as a soft gate.
- Owner: Core Team (Python)
- Refs: packages/core/tests/quantum/*; .github/workflows/ci.yml (artifact upload).

5) Expand Python Integration Tests
- Description:
  - Add integration tests around router_integration and collapse strategies under load-mocked scenarios.
- Acceptance Criteria:
  - New tests in packages/core/tests/integration cover typical quantum strategies; no TF dependency required.
- Owner: Core Team
- Refs: packages/core/tests/test_phase2_quantum_routing.py; quantum modules.

## Priority P1 – Product & Security Backlog

6) Backend httpOnly Cookie Parity
- Description:
  - Implement server-side httpOnly cookie handling in FastAPI endpoints to match frontend migration (auth.ts, auth-context.tsx).
- Acceptance Criteria:
  - Login/refresh endpoints set/clear appropriate httpOnly cookies; security flags correct; tests added.
- Owner: Backend
- Refs: packages/core/monkey_coder/app/main.py; packages/core/monkey_coder/auth/enhanced_cookie_auth.py; docs/SECURITY_IMPLEMENTATION_SUMMARY.md.

7) Component Auth Migration (Web)
- Description:
  - Migrate all components to new auth system consistently (remove legacy token reads).
- Acceptance Criteria:
  - No usage of localStorage for tokens; all protected routes/components work under cookie-based session.
- Owner: Frontend
- Refs: packages/web/src/lib/auth.ts; packages/web/src/lib/auth-context.tsx.

8) Stripe Integration & Dashboard (Web)
- Description:
  - Implement Stripe customer portal access and basic checkout session flows.
- Acceptance Criteria:
  - Checkout/subscribe flow + test keys working in dev; initial dashboard pages showing subscription status and usage.
- Owner: Frontend + Backend (if backend endpoints needed)
- Refs: packages/web/src/app/pricing/page.tsx; backend endpoints (if planned).

## Priority P2 – DX & Documentation

9) Add Coverage & JUnit Badges
- Description:
  - Surface coverage in README/docs and show latest CI run status badges.
- Acceptance Criteria:
  - README shows total coverage for Node and Python; JUnit badge or CI summary badge visible.
- Owner: Docs/DevOps

10) Contributor Guide for CI Artifacts
- Description:
  - Document how to run tests locally and interpret CI artifacts (coverage/JUnit/quantum metrics).
- Acceptance Criteria:
  - New/updated docs page with step-by-step instructions; links to CI job sections and artifacts.
- Owner: Docs
- Refs: docs/; .github/workflows/ci.yml.

11) Tighten Next ESLint Rules (Web)
- Description:
  - Upgrade to a flat ESLint config compatible with Next plugin when stable or enhance eslint-config-next usage; align rules with team standards.
- Acceptance Criteria:
  - Agreed set of rules enabled; CI lint stricter but actionable.
- Owner: Frontend
- Refs: packages/web (ESLint config and scripts).

---

## Proposed Sprint Plan (2 Weeks)

- Week 1:
  - P0-1: Coverage thresholds (Jest/Pytest) + CI summary annotations
  - P1-4: Quantum metrics baseline artifacts + CI upload
  - P1-5: Python integration tests extension

- Week 2:
  - P1-6/7: Backend cookie parity + component migration
  - P1-8: Stripe flows skeleton + dashboard MVP
  - P2-9/10/11: Badges + contributor docs + ESLint rules tightening (time-permitting)

---

## Acceptance Review Checklist

- CI fails on insufficient coverage thresholds (after baselines agreed).
- CI produces summary annotations from JUnit for Node & Python.
- Quantum metrics artifacts uploaded per CI run; comparison script attached.
- httpOnly cookie parity in backend verified with tests; frontend components migrated.
- Stripe MVP flows functional in dev with test keys; dashboard renders subscription state.
- Docs updated for contributors; coverage badges visible in README.
