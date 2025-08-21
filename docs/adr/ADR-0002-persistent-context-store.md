# ADR 0002: Persistent Context Store Deferral

Date: 2025-08-21
Status: Accepted
Decision Type: Deferral / Architectural Direction

## Context
We currently rely on an in-memory `SimpleContextManager` (default) plus an optional feature-flagged
`AdvancedContextManager`. A durable store (Redis, Postgres, or a hybrid) would enable horizontal
scaling without sticky sessions, longer multi-turn continuity, richer analytics, and stronger
retention guarantees. Introducing that layer now would add infrastructure and operational complexity
while core routing, caching, and performance instrumentation are still being stabilized.

## Decision
Defer implementation of a persistent context store. Continue using in-memory context managers and
gate any persistence layer behind a feature flag until performance baselines and schema requirements
are well understood.

## Rationale
1. Operational Focus: Avoid provisioning and maintaining new stateful services before routing and
   quantum execution KPIs are solid.
2. Benchmark Integrity: Cache behavior and routing strategies are still evolving; sizing TTLs and
   indexes now would cause churn and rework.
3. Cognitive Load: Simplicity accelerates iteration on message metadata and API surface before
   schema hardening.

## Consequences
Positive:
- Faster delivery of observability and caching improvements.
- Reduced operational surface area (no new managed datastore yet).
- Flexible offline prototyping of schemas using replay data.

Negative:
- Context loss on process restarts or horizontal scaling events.
- Limited longitudinal analytics across long-lived sessions.
- Possible user confusion about conversational memory depth.

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Frontend or SDK assumes durability | Clearly document volatility and current guarantees |
| Scale-out causes context misses | Delay large scale-out or use sticky sessions until persistence ships |
| Scope creep of implicit context surface | Track in roadmap; add tests guarding expansion |

## Future Work (Acceptance Criteria)
1. Performance Baseline: Stable latency and throughput metrics post-cache integration.
2. Data Model Draft: Message schema (ids, roles, metadata, optional embeddings) and retention policy.
3. Storage Selection: Evaluate Redis (TTL + speed) vs Postgres (durability + analytics); consider a
   hybrid (Redis hot tier, Postgres archive tier).
4. Consistency Model: At-least-once append; idempotent writes via deterministic IDs (hash of session +
   index + content hash).
5. Migration Plan: Feature flag `ENABLE_PERSISTENT_CONTEXT`; dual-write shadow phase before cutover.
6. Observability: Expose context read/write latency, hit ratio vs in-memory fallback, and storage
   error metrics.

## Decision Owners
Core Architecture & Platform Observability working group.

## References
- ADR 0001: Dependency Source of Truth (dependency governance)
<!-- markdownlint-disable-next-line MD044 -->
- Cache registry stats endpoint path `/api/v1/cache/stats`
- Quantum performance metrics module

---
This ADR will be revisited once the above future work prerequisites are satisfied or earlier if
scaling pressure accelerates the need.
