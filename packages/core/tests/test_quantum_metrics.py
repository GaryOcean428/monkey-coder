from monkey_coder.monitoring import quantum_performance as qp


def test_routing_timer_context_manager():
    with qp.routing_timer() as t:
        pass
    assert t._start is None  # stopped


def test_execution_timer_context_manager():
    with qp.execution_timer() as t:
        pass
    assert t._start is None


def test_strategy_and_error_counters_noop_safe():
    # Should not raise even if prometheus not installed
    qp.inc_strategy("provider:model")
    qp.inc_execution_error("SomeError")


def test_get_summary_structure():
    summary = qp.get_summary()
    assert "has_prometheus" in summary
    assert "routing_latency_buckets" in summary
