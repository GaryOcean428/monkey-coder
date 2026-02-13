# NEXT TASKS (Rolling 30-Day Horizon)

Generated: 2025-08-21

Source Documents:
- `docs/roadmap.md`
- `docs/roadmap/current-development.md`
- `docs/roadmap/rfc/0001-caching-performance.md`
- `docs/roadmap/implementation-reality-check.md`
- `docs/adr/ADR-0002-persistent-context-store.md`

## Priority Legend
- P0 – Must land before other roadmap advances (quality/reliability gates)
- P1 – Core feature enablement / performance foundations
- P2 – Scaling, polish, extension readiness

---
## P0 (Days 1–7)

<!-- markdownlint-disable MD013 -->

| ID | Task | Description | Acceptance Criteria | Source |
|----|------|-------------|---------------------|--------|
| P0-1 | CI Workflow Enforcement | Add unified workflow: drift, tests, coverage, lint | Gates block PR; thresholds recorded | roadmap Near-Term |
| P0-2 | Dependency Drift Guard | Wire `check_python_deps_sync.sh` into CI | CI fails on drift; README updated | delivered section |
| P0-3 | Quantum Metrics Wiring | Counters/timers: latency, branches, collapse strategy | Metrics endpoint returns non-zero sample | metrics note |
| P0-4 | Cache Stats Exposure | Surface `/API/v1/cache/stats` + Prometheus counters | Hit/miss + counters visible | RFC 0001 |
| P0-5 | Context Claim Reconciliation | Annotate/remove legacy advanced context claims | All outdated claims updated | ADR 0002 / ADR 0003 |
| P0-6 | Markdown Lint Policy | Decide compliance vs selective disable | Policy doc + CI lint job stable | roadmap Near-Term |
| P0-7 | RFC 0001 Acceptance | Move Draft → Accepted (or notes) | Status header updated w/ date | RFC 0001 |

<!-- markdownlint-enable MD013 -->

## P1 (Weeks 2–4)

| ID | Task | Description | Acceptance Criteria | Source |
|----|------|-------------|---------------------|--------|
| P1-1 | Caching Phase 1 | Routing + result caches (flags, TTL, LRU) | Hits increment; toggle off clean | RFC 0001 P1 |
| P1-2 | Caching Ph 2–3 | Routing + latency_saved; ≥10% latency cut | Benchmark artifact ≥10% | RFC 0001 P2–3 |
| P1-3 | Benchmark Harness | Synthetic latency & cost suite | JSON baseline produced | RFC goals |
| P1-4 | Quantum SLO Definition | p95 latency + hit & collapse SLOs | SLO doc in repo & CI link | current-dev addendum |
| P1-5 | Context Decision | ADR 0003: rebuild, defer, de-scope | ADR merged + roadmap sync | roadmap+ADR 0002/0003 |
| P1-6 | Coverage & Badges | Coverage + test badges in docs | Badges present & update | current-dev |
| P1-7 | Auth Parity | Cookie + bearer regression tests | Both flows covered & green | backlog |

## P2 (Weeks 4–8)

| ID | Task | Description | Acceptance Criteria | Source |
|----|------|-------------|---------------------|--------|
| P2-1 | Caching Ph 4–5 | Observability polish + extension seams | Prometheus metrics + plug-in docs | RFC 0001 P4–5 |
| P2-2 | Token & Cost Tracking | Capture tokens for cost & savings | Cost metrics + tests | RFC Open Q1 |
| P2-3 | Drift Sampling | Sample recompute to detect mismatch | Report & alert threshold | RFC Open Q2 |
| P2-4 | Persistent Context | Adapter + migration feature flag | Tests pass swap adapters | ADR 0003 future |
| P2-5 | Docs Hygiene Automation | Tab & H1 hook | Pre-commit rejects issues | friction lesson |
| P2-6 | SLO Regression Guard | CI soft-fails on drift % | CI logs show gating | metrics plan |

## Open Questions & Decisions Log

| Topic | Question | Target Resolution |
|-------|----------|-------------------|
| Context Layer | Rebuild advanced persistent + semantic now or defer? | ADR 0003 (P1 window) |
| Token Metrics | Capture at execution or infer post-hoc? | Before Caching Phase 3 completion |
| Routing Drift | Introduce sampling now or after caches stable? | Start design in P2 |
| Markdown Policy | Strict compliance vs curated ignores | End of P0 |

## Metrics & SLO Draft (To Refine)
- p95 execution latency (no cache): Baseline TBD → Target -25%
- Cache hit ratio (routing): Target ≥40% by Phase 3
- Cache hit ratio (result): Target ≥20% early; ≥35% after optimizations
- Latency saved (aggregate): Publish cumulative counter & per-request delta
- Routing decision determinism drift: <2% sampled divergence

## Artifacts To Produce
- `benchmarks/BASELINE-<date>.JSON`
- `docs/metrics/SLOs.md`
- `scripts/verify_docs.sh` (hygiene checks)
- ADR 0003 (context decision)
- RFC 0001 status update

## Governance Hooks
- Every RFC status change must update this file within same PR.
- Each ADR referencing a deferred capability must link back here until resolved.
- CI job "roadmap-sync" (future) can diff NEXT_TASKS vs open issues for drift.

---
Maintainers: Update Generated date whenever materially changing priorities.
