"""Tests for Sprint 004 width_vol candidate strip payload builder."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.viz.belief_disagreement_hints import belief_disagreement_hints_payload
from src.viz.implied_lab_provenance import build_width_vol_candidate_strip_payload


class TestWidthVolCandidateStrip(unittest.TestCase):
    def test_none_when_not_width_vol(self) -> None:
        pl = belief_disagreement_hints_payload(
            center_usd=90_000.0,
            market_peak=95_000.0,
            sigma_user=0.10,
            sigma_mkt=0.10,
            shape_gap_strength="Low",
            market_reference_kind="market-implied",
        )
        self.assertEqual(pl["category_id"], "directional")
        v = {
            "verification_summary": {"disagreement_category_id": pl["category_id"]},
            "belief_disagreement": pl["belief_disagreement"],
            "density": {"market_implied": {"breeden_litzenberger": "computed"}},
        }
        self.assertIsNone(build_width_vol_candidate_strip_payload(v))

    def test_payload_when_width_vol(self) -> None:
        pl = belief_disagreement_hints_payload(
            center_usd=100_000.0,
            market_peak=100_000.0,
            sigma_user=0.15,
            sigma_mkt=0.10,
            shape_gap_strength="Moderate",
            market_reference_kind="market-implied",
        )
        self.assertEqual(pl["category_id"], "width_vol")
        v = {
            "verification_summary": {"disagreement_category_id": "width_vol"},
            "belief_disagreement": pl["belief_disagreement"],
            "density": {"market_implied": {"breeden_litzenberger": "computed"}},
        }
        out = build_width_vol_candidate_strip_payload(v)
        self.assertIsNotNone(out)
        assert out is not None
        self.assertIn("width", out["anomaly_md"].lower())
        self.assertIn("why flagged", out["why_md"].lower())
        self.assertIn("moderate", out["confidence_md"].lower())
        self.assertIn("trust", out["trust_artifact_md"].lower())
        self.assertIn("expression families", out["expression_families_md"].lower())
        self.assertIn("falsification", out["falsification_md"].lower())

    def test_skipped_breeden_trust_line(self) -> None:
        pl = belief_disagreement_hints_payload(
            center_usd=100_000.0,
            market_peak=100_000.0,
            sigma_user=0.15,
            sigma_mkt=0.10,
            shape_gap_strength="Low",
            market_reference_kind="market-implied",
        )
        v = {
            "verification_summary": {"disagreement_category_id": "width_vol"},
            "belief_disagreement": pl["belief_disagreement"],
            "density": {
                "market_implied": {
                    "breeden_litzenberger": "skipped",
                    "skip_reason": "Fewer than 3 call marks (test).",
                }
            },
        }
        out = build_width_vol_candidate_strip_payload(v)
        self.assertIsNotNone(out)
        assert out is not None
        self.assertIn("fewer than 3", out["trust_artifact_md"].lower())


if __name__ == "__main__":
    unittest.main()
