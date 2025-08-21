"""Optional context metrics instrumentation.

Provides Prometheus counters/gauges when prometheus_client is installed.
Falls back to no-op functions otherwise so callers can import safely.
"""
from __future__ import annotations

try:
    from prometheus_client import Counter, Gauge
    _PROM = True
except ImportError:  # pragma: no cover - optional dependency
    _PROM = False

if _PROM:
    _CONTEXT_CONVERSATIONS = Gauge(
        "context_active_conversations",
        "Number of active in-memory conversations",
    )
    _CONTEXT_MESSAGES = Gauge(
        "context_total_messages",
        "Total messages across all active conversations",
    )
    _CONTEXT_EVICTIONS = Counter(
        "context_evictions_total",
        "Number of context evictions (LRU/timeouts)",
    )
    _CONTEXT_CONVERSATIONS_CREATED = Counter(
        "context_conversations_created_total",
        "Number of conversations created",
    )

    def set_conversations(v: int):  # noqa: D401
        _CONTEXT_CONVERSATIONS.set(v)

    def set_messages(v: int):  # noqa: D401
        _CONTEXT_MESSAGES.set(v)

    def inc_evictions(n: int = 1):  # noqa: D401
        _CONTEXT_EVICTIONS.inc(n)

    def inc_conversations(n: int = 1):  # noqa: D401
        _CONTEXT_CONVERSATIONS_CREATED.inc(n)
else:
    def set_conversations(v: int):  # noqa: D401
        pass

    def set_messages(v: int):  # noqa: D401
        pass

    def inc_evictions(n: int = 1):  # noqa: D401
        pass

    def inc_conversations(n: int = 1):  # noqa: D401
        pass

__all__ = [
    "set_conversations",
    "set_messages",
    "inc_evictions",
    "inc_conversations",
]
