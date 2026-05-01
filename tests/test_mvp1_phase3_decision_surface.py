"""MVP1 Phase 3 decision surface — precedence + verification payload wiring."""

from __future__ import annotations

import unittest

from src.viz.implied_lab_provenance import build_verification_payload
from src.viz.mvp1_phase3_decision_surface import build_mvp1_phase3_decision_surface


def _substrate(**kwargs: object) -> dict:
    base = {
        "trust_gate_state": "usable",
        "trust_state": "ok",
        "width_gap_label": "market_too_wide",
        "horizon_years": 0.1,
        "materiality_ratio": 1.5,
        "classification_note": "",
    }
    base.update(kwargs)
    return base


class TestMvp1Phase3DecisionSurface(unittest.TestCase):
    def test_step1_invalid_gate_no_trade(self) -> None:
        ds = build_mvp1_phase3_decision_surface(
            mvp1_benchmark_substrate=_substrate(trust_gate_state="invalid"),
            belief_disagreement=None,
        )
        assert ds is not None
        self.assertEqual(ds["primary_output_state"], "no_trade")
        self.assertEqual(ds["decision_precedence_step"], 1)
        self.assertIsNotNone(ds["no_trade_reasoning"])

    def test_step2_degraded_no_trade(self) -> None:
        ds = build_mvp1_phase3_decision_surface(
            mvp1_benchmark_substrate=_substrate(trust_state="degraded", trust_gate_state="degraded"),
            belief_disagreement=None,
        )
        assert ds is not None
        self.assertEqual(ds["primary_output_state"], "no_trade")
        self.assertEqual(ds["decision_precedence_step"], 2)

    def test_step3_mixed_unclear_watch(self) -> None:
        ds = build_mvp1_phase3_decision_surface(
            mvp1_benchmark_substrate=_substrate(width_gap_label="mixed_unclear"),
            belief_disagreement=None,
        )
        assert ds is not None
        self.assertEqual(ds["primary_output_state"], "watch_only")
        self.assertEqual(ds["decision_precedence_step"], 3)

    def test_step3_trace_mixed_watch(self) -> None:
        ds = build_mvp1_phase3_decision_surface(
            mvp1_benchmark_substrate=_substrate(width_gap_label="market_too_wide"),
            belief_disagreement={
                "classification_trace": {"category_id": "mixed", "shape_gap_strength": "Moderate"},
            },
        )
        assert ds is not None
        self.assertEqual(ds["primary_output_state"], "watch_only")
        self.assertEqual(ds["decision_precedence_step"], 3)

    def test_step4_insufficient_materiality_no_trade(self) -> None:
        ds = build_mvp1_phase3_decision_surface(
            mvp1_benchmark_substrate=_substrate(width_gap_label="insufficient_materiality"),
            belief_disagreement=None,
        )
        assert ds is not None
        self.assertEqual(ds["primary_output_state"], "no_trade")
        self.assertEqual(ds["decision_precedence_step"], 4)

    def test_step5_marginal_shape_low_watch(self) -> None:
        ds = build_mvp1_phase3_decision_surface(
            mvp1_benchmark_substrate=_substrate(),
            belief_disagreement={
                "classification_trace": {"category_id": "width_vol", "shape_gap_strength": "Low"},
            },
        )
        assert ds is not None
        self.assertEqual(ds["primary_output_state"], "watch_only")
        self.assertEqual(ds["decision_precedence_step"], 5)

    def test_step6_candidate(self) -> None:
        ds = build_mvp1_phase3_decision_surface(
            mvp1_benchmark_substrate=_substrate(),
            belief_disagreement={
                "classification_trace": {"category_id": "width_vol", "shape_gap_strength": "Moderate"},
            },
        )
        assert ds is not None
        self.assertEqual(ds["primary_output_state"], "candidate")
        self.assertEqual(ds["decision_precedence_step"], 6)
        self.assertIsNone(ds["no_trade_reasoning"])

    def test_verification_payload_fields(self) -> None:
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
        ds = v.get("mvp1_phase3_decision_surface")
        self.assertIsInstance(ds, dict)
        assert isinstance(ds, dict)
        self.assertIn(ds["primary_output_state"], ("candidate", "watch_only", "no_trade"))
        self.assertIn("explanation_plain", ds)
        self.assertIn("confidence_tier", ds)
        self.assertIn("expression_family_mapping", ds)
        self.assertIn("falsification_plain", ds)
        self.assertIn("review_horizon", ds)


if __name__ == "__main__":
    unittest.main()
