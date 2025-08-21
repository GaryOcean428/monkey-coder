# Metrics & SLOs (Initial Draft)

Generated: 2025-08-21
Status: Draft (to be refined after first benchmark + cache integration)

## Purpose
Establish a shared vocabulary and preliminary targets for performance, caching,
and quantum execution metrics. Targets are provisional until at least two
benchmark cycles have been collected (baseline + post-caching).

## Key Metrics

| Domain | Metric | Type | Description | Notes |
|--------|--------|------|-------------|-------|
| Execution | mean_latency_ms | Gauge | Mean execution latency (ms) | From benchmark JSON |
| Execution | p95_latency_ms | Gauge | 95th percentile latency | From benchmark JSON |
| Caching | cache_hits_total | Counter | Total cache hits (all tiers) | Planned Prometheus |
| Caching | cache_misses_total | Counter | Total cache misses | Planned Prometheus |
| Caching | cache_hit_ratio | Gauge | hits / (hits + misses) | Derived calc |
| Quantum | quantum_states_evaluated | Gauge | States evaluated per exec | Executor metadata |
| Quantum | quantum_collapse_confidence | Gauge | Confidence of chosen state | Executor metadata |
| Quantum | quantum_branch_latency_ms | Histogram | Per-branch latency | Future phase |
| Routing | routing_decision_latency_ms | Histogram | Routing decision latency | Future phase |
| Cost | latency_saved_ms_total | Counter | Latency avoided via caching | Future (Phase 3+) |
| Cost | token_saved_estimate | Gauge | Estimated tokens avoided | Needs token tracking |

## Initial Targets (Provisional)

| Metric | Baseline (TBD) | Target Phase 3 | Rationale |
|--------|----------------|---------------|-----------|
| mean_latency_ms | Measure baseline | -25% vs baseline | Caching + reuse |
| p95_latency_ms | Measure baseline | -20% vs baseline | Reduce tail latency |
| cache_hit_ratio (routing) | 0% initial | ≥ 40% | Reuse goal |
| cache_hit_ratio (result) | 0% initial | ≥ 20% early; ≥ 35% later | Conservative start |
| latency_saved_ms_total | 0 | Increasing weekly | Effectiveness proxy |
| quantum_states_evaluated | Baseline | Stable or ↓ 10% | Pruning success |
| quantum_collapse_confidence | Baseline | +5 pp | Selection quality |

## Collection Sources

| Source | Format | Path | Notes |
|--------|--------|------|------|
| Benchmark Harness | JSON | benchmarks/results/*.JSON | Baseline & trend |
| API JSON (/api/v1/cache/stats) | JSON | Runtime endpoint | Cache observability |
| Quantum Executor | In-memory→metrics | Instrumentation hooks | Prometheus gauges |
| Future Prometheus Exporter | OpenMetrics | /metrics | Aggregated counters |

## Evaluation Cadence
- Weekly review of benchmark artifact trend lines
- SLO recalibration after enabling caches (Phase 3 acceptance criteria)
- Automatic alert condition (future): p95 latency regression > 15% vs prior week

## Open Items
- Define precise bucketing for histogram metrics (quantum branch & routing latency)
- Decide token accounting implementation to support cost metrics
- Determine acceptable confidence variance window for collapse decisions

## Change Process
1. Propose update via PR modifying this file
2. Include benchmark artifact diff or metric evidence
3. Tag with `metrics` label
4. Auto-check (future) ensures table structure intact

---
*This draft intentionally errs on the side of breadth; unimplemented metrics are marked Future to avoid accidental overstatement.*
