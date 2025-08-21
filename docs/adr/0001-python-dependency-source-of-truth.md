# ADR 0001: Python Dependency Source of Truth

## Status
Proposed (2025-08-21)

## Context
Historically the project used `requirements.in`/`requirements.txt` as pinned dependency artifacts.
We have adopted `uv` with a `pyproject.toml` to define Python dependencies declaratively and
perform fast, reproducible resolution. We retain `requirements.txt` for compatibility with some
deployment surfaces and developer expectations, but risk drift if both are manually edited.

## Decision
1. `pyproject.toml` (tool.uv section) is the single authoritative source for Python dependency
	specifications (top-level direct deps + optional groups).
2. `requirements.txt` is treated as a compiled, derived artifact produced by
	`uv pip compile pyproject.toml -o requirements.txt` (or `scripts/check_python_deps_sync.sh --fix`).
3. Direct edits to `requirements.txt` are prohibited; CI will fail if drift is detected.
4. `requirements.in` will be phased out after a 2-week deprecation window (kept read-only meantime).
5. Documentation (README + CONTRIBUTING) will point contributors to modify only `pyproject.toml`
	and run the sync script locally before committing.

## Rationale
- Eliminates dual maintenance overhead and inconsistent resolutions.
- Enables faster resolver performance and modern packaging features via `uv`.
- Keeps compatibility with tooling expecting a `requirements.txt` lock while avoiding manual errors.

## Consequences
- Contributors must have `uv` installed (document bootstrap instructions).
- Pip install paths referencing `requirements.txt` remain valid but must not be manually changed.
- CI complexity increases slightly (drift check job) but catches errors early.

## Alternatives Considered
- Solely using `requirements.txt`: Limits modern build backends and dependency grouping.
- Solely using `pyproject.toml` (dropping `requirements.txt`): Breaks some existing deploy scripts
	and third-party integration expectations today.
- Maintaining `requirements.in` + compile: Adds an unnecessary layer now that `pyproject.toml` is canonical.

## Implementation Plan
1. (Done) Add `pyproject.toml` with dependencies.
2. (Done) Add drift detection script `scripts/check_python_deps_sync.sh`.
3. (Planned) Create CI job: run drift check (fail on differences), then run tests.
4. (Planned) Update README + add CONTRIBUTING section referencing this ADR.
5. (Planned) After deprecation date, delete `requirements.in` (unless still needed by external
	consumers) and update this ADR to Accepted.

## Acceptance Criteria
- CI fails on deliberate divergence between `pyproject.toml` and `requirements.txt`.
- Developer docs instruct editing only `pyproject.toml`.
- No direct commits modify `requirements.txt` without corresponding `pyproject.toml` change + regeneration.

## Future Follow-ups
- Evaluate generating separate production vs. dev extras constraint files if image size optimization becomes a priority.
- Add automated weekly dependency freshness report (e.g., `uv pip outdated`).

## References
- `uv` project: [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)
- Internal script: `scripts/check_python_deps_sync.sh`
