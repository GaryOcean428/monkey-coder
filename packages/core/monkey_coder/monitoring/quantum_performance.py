"""Quantum performance metrics instrumentation skeleton.

Provides lightweight counters/histograms for routing and execution latency,
strategy selection distribution, and error tracking. Falls back to no-op when
`prometheus_client` is not installed so imports are always safe.

Intended to be extended as Phase 2.2/2.3 optimization work proceeds.
"""
from __future__ import annotations
from typing import Dict, Any
import time

try:  # Optional dependency
    from prometheus_client import Counter, Histogram
    _PROM = True
except ImportError:  # pragma: no cover - optional
    _PROM = False

_ROUTING_LATENCY_BUCKETS = (
    0.001, 0.005, 0.01, 0.02, 0.05,
    0.1, 0.2, 0.5, 1.0, 2.0,
)

if _PROM:
    _ROUTING_LATENCY = Histogram(
        "quantum_routing_latency_seconds",
        "Time to produce a routing decision (persona + model)",
        buckets=_ROUTING_LATENCY_BUCKETS,
    )
    _EXECUTION_LATENCY = Histogram(
        "quantum_execution_latency_seconds",
        "Task execution latency (model invocation end-to-end)",
        buckets=_ROUTING_LATENCY_BUCKETS,
    )
    _STRATEGY_SELECTIONS = Counter(
        "quantum_strategy_selection_total",
        "Count of strategy selections by name",
        labelnames=("strategy",),
    )
    _EXECUTION_ERRORS = Counter(
        "quantum_execution_errors_total",
        "Number of execution errors by type",
        labelnames=("error_type",),
    )
else:  # No-op fallbacks
    _ROUTING_LATENCY = None
    _EXECUTION_LATENCY = None
    _STRATEGY_SELECTIONS = None
    _EXECUTION_ERRORS = None


def observe_routing_latency(seconds: float):
    if _ROUTING_LATENCY:
        _ROUTING_LATENCY.observe(seconds)


def observe_execution_latency(seconds: float):
    if _EXECUTION_LATENCY:
        _EXECUTION_LATENCY.observe(seconds)


def inc_strategy(strategy: str):
    if _STRATEGY_SELECTIONS:
        _STRATEGY_SELECTIONS.labels(strategy=strategy).inc()


def inc_execution_error(error_type: str):
    if _EXECUTION_ERRORS:
        _EXECUTION_ERRORS.labels(error_type=error_type).inc()


class _Timer:
    def __init__(self, cb):
        self._cb = cb
        self._start = time.perf_counter()

    def stop(self):
        if self._start is not None:
            elapsed = time.perf_counter() - self._start
            self._cb(elapsed)
            self._start = None
            return elapsed
        return 0.0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop()


def routing_timer():
    """Context manager to time routing decisions."""
    return _Timer(observe_routing_latency)


def execution_timer():
    """Context manager to time execution latency."""
    return _Timer(observe_execution_latency)


def get_summary() -> Dict[str, Any]:  # Minimal stub (Prometheus pulls raw detail separately)
    return {
        "has_prometheus": _PROM,
        "routing_latency_buckets": list(_ROUTING_LATENCY_BUCKETS),
    }


__all__ = [
    "observe_routing_latency",
    "observe_execution_latency",
    "inc_strategy",
    "inc_execution_error",
    "routing_timer",
    "execution_timer",
    "get_summary",
]
