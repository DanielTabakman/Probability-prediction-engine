"""
Tiny performance helpers for Streamlit instrumentation.

Keep this module pure-Python so tests can import it safely.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass
class PerfLog:
    start_s: float = field(default_factory=time.perf_counter)
    timings_ms: dict[str, float] = field(default_factory=dict)

    def mark_ms(self, label: str, elapsed_ms: float) -> None:
        # Last-write-wins for repeated labels on rerun.
        self.timings_ms[str(label)] = float(elapsed_ms)

    def total_ms(self) -> float:
        return (time.perf_counter() - self.start_s) * 1000.0


@contextmanager
def timed(perf: PerfLog, label: str):
    t0 = time.perf_counter()
    try:
        yield
    finally:
        perf.mark_ms(label, (time.perf_counter() - t0) * 1000.0)

