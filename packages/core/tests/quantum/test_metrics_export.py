import json
import os
from pathlib import Path

from monkey_coder.quantum.performance_metrics import (
    PerformanceMetricsCollector,
    MetricType,
)


def test_quantum_metrics_export_creates_artifact(tmp_path):
    """
    Generate a lightweight quantum metrics artifact for CI baselining.

    This test simulates a few routing/provider/cache metrics and writes a JSON
    artifact to artifacts/quantum/metrics.json for CI upload and comparison.
    """
    collector = PerformanceMetricsCollector(enable_real_time_monitoring=False)

    # Simulate a few data points (small & fast)
    collector.record_metric(MetricType.EXECUTION_TIME, 0.42, metadata={"provider": "openai", "model": "gpt-4.1"})
    collector.record_metric(MetricType.EXECUTION_TIME, 0.38, metadata={"provider": "anthropic", "model": "claude-3.5"})
    collector.record_metric(MetricType.QUALITY_SCORE, 0.88, metadata={"provider": "openai"})
    collector.record_metric(MetricType.QUALITY_SCORE, 0.84, metadata={"provider": "anthropic"})
    collector.record_metric(MetricType.CACHE_PERFORMANCE, 1.0, metadata={"response_time": 0.05})
    collector.record_metric(MetricType.CACHE_PERFORMANCE, 0.0, metadata={"response_time": 0.15})

    # Update aggregated summary before export
    collector._update_aggregated_metrics()

    export = collector.export_metrics(time_window=None)

    # Ensure output directory and write artifact
    out_dir = Path("artifacts/quantum")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "metrics.json"

    with out_file.open("w", encoding="utf-8") as f:
        json.dump(export, f, ensure_ascii=False, indent=2)

    # Basic assertions
    assert out_file.exists(), "metrics.json artifact was not created"
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert "metrics" in data and "summary" in data, "exported metrics missing keys"
