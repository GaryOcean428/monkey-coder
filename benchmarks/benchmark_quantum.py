#!/usr/bin/env python
"""Baseline benchmarking harness for quantum & execution latency.

Usage:
  python benchmarks/benchmark_quantum.py --runs 5 --parallel true \
      --output benchmarks/results/BASELINE.json

Outputs JSON with structure:
{
  "timestamp": "2025-08-21T12:34:56Z",
  "config": {"runs": 5, "parallel": true},
  "metrics": {
      "execution_latencies_ms": [...],
      "mean_latency_ms": 0.0,
      "p95_latency_ms": 0.0,
      "cache_hits": 0,
      "cache_misses": 0
  },
  "environment": {"python": "3.11.4", "commit": "<git-sha>"}
}

This is intentionally light weight; it exercises the QuantumExecutor with a
fixed task to establish a pre-caching baseline. Later phases can extend with
multiple prompt categories, varied sizes, and provider/model selection routing.
"""

from __future__ import annotations
import argparse
import asyncio
import json
import os
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Ensure core package import when run from repo root
sys.path.append(str(Path(__file__).resolve().parent.parent / 'packages' / 'core'))

from monkey_coder.core.quantum_executor import QuantumExecutor  # type: ignore


def _git_sha() -> str:
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    except Exception:  # pragma: no cover
        return "unknown"


def _p95(values: List[float]) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    idx = int(len(sorted_vals) * 0.95) - 1
    idx = max(0, min(idx, len(sorted_vals) - 1))
    return sorted_vals[idx]


async def run_once(executor: QuantumExecutor, task: str, parallel: bool) -> Dict[str, Any]:
    import time
    start = time.perf_counter()
    result = await executor.execute(task, parallel_futures=parallel)
    end = time.perf_counter()
    latency_ms = (end - start) * 1000.0
    # Attempt to inspect cache stats if available
    cache_hits = getattr(getattr(executor, '_result_cache', None), 'hits', 0)
    cache_misses = getattr(getattr(executor, '_result_cache', None), 'misses', 0)
    return {
        'latency_ms': latency_ms,
        'cache_hits': cache_hits,
        'cache_misses': cache_misses,
        'result_confidence': result.get('confidence', 0.0) if isinstance(result, dict) else None,
    }


async def main() -> None:
    parser = argparse.ArgumentParser(description='Quantum execution baseline benchmark')
    parser.add_argument('--runs', type=int, default=5, help='Number of execution iterations')
    parser.add_argument('--parallel', type=str, default='true', help='Enable quantum parallel superposition (true/false)')
    parser.add_argument('--task', type=str, default='Refactor a Python function for clarity', help='Benchmark task prompt')
    parser.add_argument('--output', type=str, default='benchmarks/results/BASELINE.json', help='Output JSON path')
    args = parser.parse_args()

    parallel = args.parallel.lower() not in ('0', 'false', 'no')

    # Disable result cache for pure baseline unless explicitly enabled
    if os.getenv('ENABLE_RESULT_CACHE', '0') in ('0', 'false', 'False'):
        pass
    else:
        os.environ['ENABLE_RESULT_CACHE'] = '0'

    executor = QuantumExecutor()

    latencies: List[float] = []
    cache_hits_last = cache_misses_last = 0
    run_details = []

    for _ in range(args.runs):
        detail = await run_once(executor, args.task, parallel)
        latencies.append(detail['latency_ms'])
        cache_hits_last = detail['cache_hits']
        cache_misses_last = detail['cache_misses']
        run_details.append(detail)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'config': {
            'runs': args.runs,
            'parallel': parallel,
            'task': args.task,
        },
        'metrics': {
            'execution_latencies_ms': latencies,
            'mean_latency_ms': statistics.mean(latencies) if latencies else 0.0,
            'p95_latency_ms': _p95(latencies),
            'cache_hits': cache_hits_last,
            'cache_misses': cache_misses_last,
        },
        'runs': run_details,
        'environment': {
            'python': sys.version.split()[0],
            'commit': _git_sha(),
        }
    }

    with output_path.open('w') as f:
        json.dump(data, f, indent=2)
    print(f"Benchmark written to {output_path}")


if __name__ == '__main__':
    asyncio.run(main())
