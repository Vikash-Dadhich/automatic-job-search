"""Benchmark package — peer comparison for a target job."""

from benchmark.engine import (
    BenchmarkReport,
    BenchmarkSummary,
    build_benchmark,
    profile_to_peer_data,
    run_benchmark,
)

__all__ = [
    "BenchmarkReport",
    "BenchmarkSummary",
    "build_benchmark",
    "profile_to_peer_data",
    "run_benchmark",
]
