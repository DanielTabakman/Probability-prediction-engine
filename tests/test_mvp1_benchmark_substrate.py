"""Tests for MVP1 Phase 1 benchmark substrate (widths + trust/degraded flags)."""

from __future__ import annotations

import math
import unittest

from src.viz.implied_lab_provenance import build_trust_strip_lines, build_verification_payload
from src.viz.mvp1_benchmark_substrate import (
    MVP1_BENCHMARK_ID,
    MVP1_BENCHMARK_VERSION,
    build_mvp1_benchmark_substrate,
)


class TestMvp1BenchmarkSubstrate(unittest.TestCase):
    def test_constants_frozen(self) -> None:
        self.assertEqual(MVP1_BENCHMARK_ID, "ppe_mvp1_lognormal_atm_iv")
        self.assertEqual(MVP1_BENCHMARK_VERSION, "1.0.0")

    def test_skipped_breeden_is_degraded(self) -> None:
        md = {
            "forward": 100_000.0,
            "vol": 0.8,
            "T_years": 0.25,
            "dist": {"prices": [90_000.0, 100_000.0, 110_000.0]},
        }
        b = build_mvp1_benchmark_substrate(
            market_data=md,
            market_pdf_raw=[],
            call_marks=[{"strike": 1.0}],
        )
        self.assertEqual(b["empirical_status"], "skipped")
        self.assertEqual(b["trust_state"], "degraded")
        self.assertIsNone(b["empirical_market_implied_sigma_ln"])

    def test_computed_empirical_is_ok(self) -> None:
        prices = [80_000.0 + i * 500.0 for i in range(40)]
        # Gaussian-ish bump centered mid-grid
        mid = 100_000.0
        raw = [math.exp(-0.5 * ((p - mid) / 8000.0) ** 2) for p in prices]
        md = {
            "forward": mid,
            "vol": 0.6,
            "T_years": 0.1,
            "dist": {"prices": prices},
        }
        marks = [{"strike": float(x), "mark_btc": 0.01} for x in (mid - 2000, mid, mid + 2000)]
        b = build_mvp1_benchmark_substrate(
            market_data=md,
            market_pdf_raw=raw,
            call_marks=marks,
        )
        self.assertEqual(b["empirical_status"], "computed")
        self.assertEqual(b["trust_state"], "ok")
        self.assertIsInstance(b["empirical_market_implied_sigma_ln"], float)
        self.assertGreater(float(b["empirical_market_implied_sigma_ln"]), 0.0)

    def test_trust_strip_includes_mvp1_when_verification_has_summary(self) -> None:
        md = {
            "forward": 99_000.0,
            "vol": 0.5,
            "T_years": 0.05,
            "dist": {"prices": [98_000.0, 99_000.0, 100_000.0]},
        }
        v = build_verification_payload(
            market_data=md,
            summary={"name": "—", "cost_usd": 0.0},
            strategy=None,
            overlay={"payoff_usd": []},
            market_pdf_raw=[],
            call_marks=[],
            belief_verification=None,
            belief_disagreement=None,
            lab_mode=None,
        )
        lines = build_trust_strip_lines(v)
        joined = "\n".join(lines)
        self.assertIn(MVP1_BENCHMARK_ID, joined)
        self.assertIn(MVP1_BENCHMARK_VERSION, joined)
        self.assertIsInstance(v.get("mvp1_benchmark_substrate"), dict)


if __name__ == "__main__":
    unittest.main()
