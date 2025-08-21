# RFC 0001: Caching & Performance Layer (Phase 2.4 Foundations)

## Status
Draft (2025-08-21)

## Context
Phase 2.4 targets latency reduction, cost efficiency, and stability of model routing &
execution. Current system re-computes routing decisions and re-executes identical or
near-identical prompts without reuse. No formal caching layer or invalidation policy
exists. Performance instrumentation is nascent (quantum metrics skeleton present,
no live counters wired yet).

## Goals
1. Reduce average end-to-end task latency (target: -25%)
2. Lower aggregate model invocation cost (target: -15%)
3. Improve routing determinism & transparency (traceable reuse decisions)
4. Provide observability KPIs: cache hit ratio, reuse latency delta, staleness

## Non-Goals
- Persistent distributed cache implementation (initial phase in-memory)
- Premature semantic similarity fuzzy matching (will design extension points)
- Token-level partial response reuse

## Scope (Initial Increment)
- In-memory multi-tier cache abstraction
  - Layer 1: Routing decision cache (keyed by normalized request features)
  - Layer 2: Execution result cache (keyed by prompt+persona+model signature)
- TTL + size-based eviction (LRU with max entries + optional time-based expiry)
- Deterministic normalization pipeline for cache keys (whitespace, persona config hashing)
- Metrics surface: hits, misses, evictions, stale revalidations, latency saved estimate
- Configuration toggles (env flags): ENABLE_RESULT_CACHE, CACHE_TTL_SECONDS, CACHE_MAX_ENTRIES

## Out of Scope (Future Extensions)
- Cross-instance shared cache (Redis/KeyDB)
- Semantic embedding similarity fallback
- Partial result hydration / streaming chunk cache
- Provider-specific adaptive TTL tuning

## Key Data Structures

```python
class CacheEntry(BaseModel):
  key: str
  value: Any
  created_at: float
  latency_ms: float  # original compute time (for savings estimate)
  model: str
  persona: str
```

## API Sketch

```python
class ResultCache(Protocol):
  def get(self, key: str) -> Optional[CacheEntry]: ...
  def set(self, key: str, value: Any, meta: Dict[str, Any]) -> CacheEntry: ...
  def stats(self) -> Dict[str, Any]: ...
```

Routing integration:

```python
with qp.routing_timer():
  cache_key = routing_cache.normalized_key(request)
  if (entry := routing_cache.get(cache_key)):
    metrics.inc_routing_cache_hit()
    return entry.value
  decision = compute_decision(request)
  routing_cache.set(cache_key, decision, meta)
  return decision
```

## Invalidation Strategy

| Scenario | Action |
|----------|--------|
| Persona config changed | Invalidate keys referencing persona hash |
| Model deprecation | Purge entries for model id |
| TTL expiry | Lazy eviction on access |
| Capacity pressure | LRU eviction |

## Metrics

| Metric | Type | Description |
|--------|------|-------------|
| result_cache_hits_total | Counter | Successful reused execution results |
| result_cache_misses_total | Counter | Requests requiring fresh execution |
| routing_cache_hits_total | Counter | Cached routing decisions used |
| routing_cache_misses_total | Counter | Routing recomputed |
| cache_evictions_total | Counter | Entries removed (LRU/TTL/manual) |
| cache_latency_saved_ms_total | Counter | Accumulated latency avoided |
| cache_current_entries | Gauge | Active entries (all tiers) |

## Observability & Exposure
- Extend `/metrics/performance` JSON with `cache` section (already present) augmented to include hit ratios & savings
- Prometheus exposition (counters/gauges) via new metrics file `monitoring/cache_metrics.py`
- Add `GET /api/v1/cache/stats` lightweight JSON endpoint (parallel to context metrics)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Stale data returned after model update | Incorrect outputs | Include model & persona hash in key; purge on change |
| Memory growth from large results | OOM risk | Enforce max size & per-entry size threshold |
| Over-normalization causing collisions | Wrong reuse | Include structured hashing (SHA256 of canonical JSON) |
| Latency overhead in key generation | Diminished gains | Micro-benchmark & optimize canonicalization |
| Premature complexity (distributed) | Schedule slip | Keep initial scope in-memory only |

## Open Questions
1. Do we record token savings (requires token count at execution time)?
2. Should routing cache be probabilistically sampled to detect drift vs. current scoring logic?
3. Provide manual purge admin endpoint early or defer?

## Phased Plan

| Phase | Deliverable | Exit Criteria |
|-------|-------------|---------------|
| 0 | RFC Acceptance | Stakeholders sign off; scope frozen |
| 1 | In-memory caching infra | Hit/miss counters, basic eviction, env toggles |
| 2 | Routing cache integration | Latency saved counter > 0 on benchmark suite |
| 3 | Execution cache integration | Demonstrated >10% latency reduction on representative workload |
| 4 | Observability polish | Prometheus metrics, JSON endpoint, docs updated |
| 5 | Extension readiness | Interface seams allow plug-in for Redis + semantic extension |

## Acceptance Criteria
- Cache layer can be toggled off cleanly (no side-effects)
- ≥10% latency reduction on synthetic benchmark suite after Phase 3
- Metrics exposed in both JSON and Prometheus formats
- Documented invalidation triggers and admin procedures
- No correctness regressions in test suite when cache enabled

## Decision Timeline
Target acceptance: before starting Phase 2.4 coding. If not accepted within 14
days, revalidate assumptions with updated performance baselines.

## Appendix: Key Generation (Draft)
Canonical form: JSON dump of ordered dict:

```json
{
  "prompt": "<trimmed>\n<normalized-whitespace>",
  "persona": "<persona_hash>",
  "model": "gpt-4.1",
  "features": {"stream": false, "temperature": 0.7}
}
```

Hash: `sha256(canonical_json)`

---

Feedback welcome via PR review comments. After acceptance, create implementation tickets and update backlog sections accordingly.
