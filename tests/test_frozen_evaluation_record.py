"""Frozen evaluation record builder."""

from __future__ import annotations

import unittest

from src.viz.frozen_evaluation_record import build_frozen_evaluation_record, summary_line_for_record


class TestFrozenEvaluationRecord(unittest.TestCase):
    def test_classifier_and_benchmark(self) -> None:
        v = {
            "mvp1_decision": {
                "data_quality": "usable",
                "primary_output_state": "watch_only",
                "classification_label": "aligned",
                "materiality": {
                    "materiality_rule_version": "mvp1_v0_provisional",
                    "market_width_1sigma_move_pct": 12.0,
                    "benchmark_width_1sigma_move_pct": 11.5,
                    "m_ratio": 1.1,
                },
            },
            "verification_summary": {
                "as_of_utc": "2026-01-02T00:00:00Z",
                "disagreement_category_id": "aligned",
                "primary_output_state": "watch_only",
            },
            "density": {
                "reference_risk_neutral": {
                    "method": "Black–Scholes lognormal",
                    "forward_usd": 90_000.0,
                    "atm_iv_annual": 0.55,
                    "T_years": 0.25,
                    "grid_price_min_usd": 50_000.0,
                    "grid_price_max_usd": 150_000.0,
                    "grid_points": 100,
                }
            },
            "belief_disagreement": {"contract_schema_version": "bd-schema-x"},
        }
        r = build_frozen_evaluation_record(verification=v, expiry_str="1JAN26", operator_note="  hi  ")
        self.assertTrue(r["snapshot_id"])
        self.assertEqual(r["payload_schema_version"], "ppe_frozen_eval_v1")
        self.assertEqual(r["classifier_version"], "bd-schema-x")
        self.assertEqual(r["benchmark_witness"]["forward_usd"], 90_000.0)
        self.assertEqual(r["operator_note"], "hi")
        self.assertEqual(r["data_quality"], "usable")
        self.assertEqual(r["primary_output_state"], "watch_only")
        self.assertEqual(r["materiality_m_ratio"], 1.1)
        sl = summary_line_for_record(r)
        self.assertIn("aligned", sl)
