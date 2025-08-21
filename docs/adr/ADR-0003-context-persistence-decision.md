# ADR 0003: Context Persistence & Semantic Search Decision

## Status
Accepted (2025-08-21)

## Decision
Defer implementation of a persistent database-backed context store and semantic
search layer until after Phase 2.4 (Caching & Performance foundations) unless a
critical user or reliability requirement emerges earlier. Current in-memory
`SimpleContextManager` remains the supported default with strengthened metrics
and clear capability disclosure.

## Context
Earlier documentation inconsistently asserted a “fully implemented persistent
context + semantic search system.” ADR 0002 clarified that only an in-memory
context manager is active. Meanwhile, performance, observability, and caching
investments (RFC 0001) deliver higher near-term ROI and unblock latency & cost
optimization work.

Implementing a durable store (models: Users, Sessions, Conversations, Messages)
and semantic embeddings search would introduce migration, token cost, infra,
and complexity overhead before baseline execution performance metrics and cache
reuse benefits are established.

## Forces / Considerations

| Force | Description | Weight |
|-------|-------------|--------|
| Performance Baseline Needed | Need uncontaminated latency data before adding DB roundtrips | High |
| Engineering Focus | Limited capacity; caching & metrics are gating future phases | High |
| Risk of Mismatch Claims | Must avoid overstating capabilities to community/users | High |
| Data Durability Value (Now) | Low active user volume; durability less urgent | Medium |
| Semantic Search Utility | More impactful once historical volume exists | Medium |
| Implementation Complexity | DB schema, migrations, embedding pipeline, eviction | Medium |
| Opportunity Cost | Would delay cache performance gains | High |

## Options Considered
1. Build full persistence + semantic search now.
2. Build minimal persistence (no semantic) now; semantic later.
3. Defer full persistence + semantic (chosen).
4. Remove context concept entirely until needed.

## Rationale
Option 3 maximizes near-term velocity on measurable performance wins while
reducing risk of premature architectural commitment. Option 2 still diverts
attention and yields limited user-visible gain at current scale. Option 1 adds
highest complexity/cost for least immediate impact. Option 4 harms developer &
user experience by regressing basic continuity.

## Scope (What We WILL Do Now)
- Maintain and monitor `SimpleContextManager`.
- Expose lightweight metrics via `/api/v1/context/metrics`.
- Document clearly that context is in-memory and ephemeral.
- Provide extension seam interface sketch for future persistence adapter.

## Out of Scope (Deferred)
- SQL/NoSQL schema and migration scripts.
- Embedding generation & vector index management.
- Semantic similarity ranking / relevance scoring.
- Cross-session long-horizon retrieval algorithms.
- Token-based cost accounting tied to stored history.

## Triggers for Reconsideration

| Trigger | Threshold Example | Action |
|---------|-------------------|--------|
| User Volume Growth | > 100 active weekly sessions needing continuity | Re-evaluate persistence priority |
| Feature Demand | ≥ 3 distinct user requests for persistent history | Draft persistence RFC |
| Compliance / Audit Need | Requirement to retain chat logs | Accelerate durable storage |
| Performance Plateau | Caching gains realized; context recreation bottleneck | Re-prioritize persistence |

## Metrics to Watch
- Context metric endpoint request frequency.
- Average session length (messages per session) – if rising steadily, persistence value increases.
- Support / issue reports referencing lost context.
- Cache hit ratios and latency savings (once implemented) – prerequisite for shifting focus.

## Future Implementation Sketch (Non-Binding)
1. Storage Adapter Interface

```python
class ContextStore(Protocol):
    async def save_message(self, session_id: str, message: Message) -> None: ...
    async def load_session(self, session_id: str) -> list[Message]: ...
    async def search(self, query: str, limit: int = 20) -> list[Message]: ...  # optional
```

1. Minimal Postgres schema (sessions, messages) with composite index on (session_id, created_at).
2. Optional embeddings table (message_id -> vector) behind feature flag.
3. Batched embedding generation job (async queue) to avoid request latency impact.
4. Eviction policy: time-based (e.g., 30-day retention) + size cap.

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Perception of over-claim | Trust erosion | Explicit disclaimers & ADR references in docs |
| Rediscovery of decision | Re-litigation overhead | Link ADR 0003 from roadmap & NEXT_TASKS |
| Drift when later implementing | Rework | Maintain interface sketch & keep tests modular |
| Engineering context loss | Slower future implementation | Capture rationale here & in future RFC |

## Related
- ADR 0002: Defers persistent context store (initial clarification)
- RFC 0001: Caching & Performance priorities precede persistence
- NEXT_TASKS: P1 item for this ADR creation & acknowledgment

## Status Tracking
Add a note in `docs/roadmap/NEXT_TASKS.md` if reconsideration triggers are met.

## Decision Review Date
Revisit no later than 2025-10-01 or upon earliest trigger.

---
*Adopted to preserve focus on performance and observability foundations before incurring persistence complexity.*
