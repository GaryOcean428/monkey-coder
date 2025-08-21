# Benchmarks

Initial lightweight benchmarking harness for quantum execution performance.

## Scripts
- `benchmark_quantum.py` – Runs a simple latency loop against `QuantumExecutor`.

## Usage

<!-- markdownlint-disable MD013 -->
```bash
python benchmarks/benchmark_quantum.py \
	--runs 10 \
	--parallel true \
	--task "Optimize a Python function for readability" \
	--output benchmarks/results/BASELINE.JSON
```
<!-- markdownlint-enable MD013 -->

## Notes
- Disables result cache to establish an uncompromised baseline.
- Future phases: add routing decision metrics, cache-enabled comparison, token usage.
