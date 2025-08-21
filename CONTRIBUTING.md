# Contributing Guide

Welcome! This guide explains how to work effectively in the Monkey Coder monorepo.

## Repository Structure

Key areas:
- `packages/core` – Python orchestration engine
- `packages/cli` – CLI client
- `packages/sdk` – (future) language SDKs
- `packages/web` – Web UI (Next.js)
- `docs/` – Docusaurus documentation & roadmap
- `scripts/` – Tooling & maintenance scripts

## Prerequisites

- Node.js >= 20 (yarn 4 is auto via Corepack)
- Python 3.11+
- `uv` for Python dependency management (see ADR 0001)

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Dependency Policy (ADR 0001)

Python dependencies are defined ONLY in `pyproject.toml` at repo root.
`requirements.txt` is generated. Do not edit it manually.

To check or fix drift:

```bash
./scripts/check_python_deps_sync.sh         # detect
./scripts/check_python_deps_sync.sh --fix   # regenerate requirements.txt
```

Node dependencies are managed per workspace via `package.json` (JSON) with yarn workspaces.

## Install

```bash
yarn install
uv sync  # or: uv pip install -r requirements.txt (legacy)
```

## Common Scripts

```bash
yarn test            # Run all JS/TS tests
yarn test:coverage   # Coverage across workspaces
yarn lint            # ESLint across workspaces
yarn lint:md         # Markdown lint
yarn typecheck       # TypeScript type checks
```

Python tests:

```bash
cd packages/core
pytest
```

Quantum-only tests:

```bash
cd packages/core
pytest tests/quantum
```

## Feature Flags
- `ENABLE_CONTEXT_MANAGER` – toggle context subsystem
- `CONTEXT_MODE` – `simple` (current) / future `advanced`

## Adding Dependencies
Python:

```bash
uv add FastAPI  # example
./scripts/check_python_deps_sync.sh --fix
git add pyproject.toml requirements.txt
```

Node (workspace):

```bash
yarn workspace monkey-coder-cli add chalk
```

## Commit Convention
Use Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, etc.).
Group documentation updates logically (avoid noisy single-line commits unless urgent).

## CI Expectations
PRs must pass:
- Node lint, typecheck, tests with coverage >= threshold
- Python tests & (soon) coverage baseline
- Dependency drift check (pyproject vs requirements)
- Markdown lint (policy evolving; may be warning-only initially)

## Adding Quantum Metrics
Use helper context managers in `monitoring/quantum_performance.py`:

```python
from monkey_coder.monitoring import quantum_performance as qp
with qp.routing_timer():
    # routing decision
with qp.execution_timer():
    # execution path
qp.inc_strategy("epsilon_greedy")
```

## Reporting Issues
Open a GitHub issue with:
- Repro steps
- Expected vs actual
- Logs / stack traces
- Environment (Python & Node versions)

## Roadmap & Decisions
See `docs/roadmap/` and ADRs in `docs/adr/`.

## Style
- Python: type hints encouraged; prefer explicit over implicit.
- TS/JS: no `any` unless justified with comment.
- Keep functions small & testable.

## Documentation
Update relevant roadmap / ADR when changing architectural behavior.

## Fast Start (Suggested Flow)

```bash
git checkout -b feat/<short-topic>
yarn install && uv sync
make changes
yarn lint && yarn typecheck && yarn test:coverage
./scripts/check_python_deps_sync.sh
git commit -m "feat(core): short description"
git push -u origin feat/<short-topic>
```

Thanks for contributing!
