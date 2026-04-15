"""
Guardrail: orange availability must not diverge between
- the chart truth-state/heading (app uses verification flag)
- the market snapshot line (also uses verification flag)

This test enforces the canonical source of truth: outputs["verification"]["market_implied_orange_available"],
and requires it to align with whether the chart helper actually provides an orange curve.
"""

from __future__ import annotations

import unittest

from src.viz.implied_lab_derive import derive_lab_outputs


class TestOrangeAvailabilityAlignment(unittest.TestCase):
    def _minimal_market_data(self) -> dict:
        prices = [80_000.0, 90_000.0, 100_000.0, 110_000.0, 120_000.0]
        pdf_raw = [0.01, 0.03, 0.04, 0.03, 0.01]
        return {
            "forward": 100_000.0,
            "vol": 0.6,
            "T_years": 0.1,
            "dist": {"prices": prices, "pdf_raw": pdf_raw},
            "put_by_k": {},
            "call_by_k": {},
            "call_marks": [],
        }

    def test_orange_unavailable_when_insufficient_calls(self) -> None:
        md = self._minimal_market_data()
        md["call_marks"] = [
            {"strike": 90_000.0, "mark_btc": 0.2},
            {"strike": 100_000.0, "mark_btc": 0.15},
        ]  # < 3 marks → orange unavailable
        state = {
            "expiry_str": "TEST",
            "mode": "exact_strikes",
            "qty": 1,
            "strikes_exact": {"k1": 100_000.0, "k2": 100_000.0, "k3": 100_000.0, "k4": 100_000.0},
            "payoff_targets": {"body_left": 0.0, "body_right": 0.0, "left_wing": 0.0, "right_wing": 0.0},
            "legs_enabled": {"use_k1": False, "use_k2": False, "use_k3": False, "use_k4": False},
            "reverse": False,
            "polarity": {"long_k1": False, "long_k2": True, "long_k3": True, "long_k4": False},
            "net_pnl_mode": False,
            "user_belief": {"enabled": False, "center_usd": 100_000.0, "width": 0.2},
        }
        out = derive_lab_outputs(state, md)
        ver = out.get("verification") or {}
        ch = out.get("chart_helpers") or {}
        self.assertFalse(ver.get("market_implied_orange_available"))
        self.assertFalse(bool(ch.get("market_pct")))


if __name__ == "__main__":
    unittest.main()

