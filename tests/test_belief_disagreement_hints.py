"""Tests for belief–market disagreement classification and contract payload."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.viz.belief_disagreement_hints import (
    CONTRACT_SCHEMA_VERSION,
    belief_disagreement_hints_payload,
    build_disagreement_scan_payload,
    classify_disagreement,
    width_band_from_sigmas,
)
from src.viz.disagreement_thresholds import (
    WIDTH_NARROWER_RATIO,
    WIDTH_WIDER_RATIO,
    peak_alignment_tolerance_usd,
)
from src.viz.implied_lab_provenance import build_verification_payload


class TestClassifyDisagreement(unittest.TestCase):
    def test_aligned_when_peak_and_width_similar(self) -> None:
        self.assertEqual(
            classify_disagreement(peak_aligned=True, width_band="similar"),
            "aligned",
        )

    def test_directional_when_peak_not_aligned_width_similar(self) -> None:
        self.assertEqual(
            classify_disagreement(peak_aligned=False, width_band="similar"),
            "directional",
        )

    def test_width_vol_when_peak_aligned_width_not_similar(self) -> None:
        self.assertEqual(
            classify_disagreement(peak_aligned=True, width_band="wider"),
            "width_vol",
        )
        self.assertEqual(
            classify_disagreement(peak_aligned=True, width_band="narrower"),
            "width_vol",
        )

    def test_mixed_when_both_not_aligned(self) -> None:
        self.assertEqual(
            classify_disagreement(peak_aligned=False, width_band="wider"),
            "mixed",
        )
        self.assertEqual(
            classify_disagreement(peak_aligned=False, width_band="narrower"),
            "mixed",
        )


class TestWidthBandBoundaries(unittest.TestCase):
    def test_at_narrower_boundary_is_similar_not_narrower(self) -> None:
        sm = 0.1
        # sigma_user == sm * 0.92 is NOT strictly less → similar
        boundary = sm * WIDTH_NARROWER_RATIO
        self.assertEqual(width_band_from_sigmas(boundary, sm), "similar")

    def test_just_below_narrower_boundary(self) -> None:
        sm = 0.1
        boundary = sm * WIDTH_NARROWER_RATIO
        self.assertEqual(width_band_from_sigmas(boundary - 1e-12, sm), "narrower")

    def test_at_wider_boundary_is_similar(self) -> None:
        sm = 0.1
        boundary = sm * WIDTH_WIDER_RATIO
        self.assertEqual(width_band_from_sigmas(boundary, sm), "similar")

    def test_just_above_wider_boundary(self) -> None:
        sm = 0.1
        boundary = sm * WIDTH_WIDER_RATIO
        self.assertEqual(width_band_from_sigmas(boundary + 1e-12, sm), "wider")


class TestPeakToleranceBoundary(unittest.TestCase):
    def test_delta_equals_tolerance_is_not_aligned(self) -> None:
        mp = 50_000.0
        tol = peak_alignment_tolerance_usd(mp)
        center = mp + tol
        delta = center - mp
        self.assertEqual(delta, tol)
        self.assertFalse(abs(delta) < tol)

    def test_delta_just_inside_tolerance_is_aligned(self) -> None:
        mp = 50_000.0
        tol = peak_alignment_tolerance_usd(mp)
        center = mp + tol - 1e-9
        self.assertTrue(abs(center - mp) < tol)


class TestBeliefDisagreementHintsPayloadGolden(unittest.TestCase):
    def test_golden_payload_shape_and_schema_version(self) -> None:
        pl = belief_disagreement_hints_payload(
            center_usd=100_000.0,
            market_peak=95_000.0,
            sigma_user=0.12,
            sigma_mkt=0.10,
            shape_gap_strength="Moderate",
            market_reference_kind="market-implied",
        )
        self.assertEqual(pl["category_id"], "mixed")
        bd = pl["belief_disagreement"]
        self.assertEqual(bd["contract_schema_version"], CONTRACT_SCHEMA_VERSION)
        self.assertEqual(CONTRACT_SCHEMA_VERSION, "1")
        self.assertIn("classification_trace", bd)
        tr = bd["classification_trace"]
        self.assertEqual(tr["category_id"], "mixed")
        self.assertEqual(tr["shape_gap_strength"], "Moderate")
        self.assertEqual(tr["market_reference_kind"], "market-implied")
        self.assertIn("strategy_families", bd)
        self.assertEqual(len(bd["strategy_families"]), 3)
        fam0 = bd["strategy_families"][0]
        ex0 = fam0["example_structure"]
        self.assertEqual(ex0.get("structure_kind"), "illustrative_pattern")
        self.assertIn(fam0.get("tradeoff_failure_mode") or "", pl["markdown"])
        self.assertIn("**View:**", pl["markdown"])
        self.assertIn("**Tradeoff / failure mode:**", pl["markdown"])
        self.assertIn("Strategy families that fit this disagreement", pl["markdown"])


class TestBeliefVsMarketGlanceVerification(unittest.TestCase):
    def test_glance_present_when_belief_and_contract(self) -> None:
        pl = belief_disagreement_hints_payload(
            center_usd=100_000.0,
            market_peak=95_000.0,
            sigma_user=0.12,
            sigma_mkt=0.10,
            shape_gap_strength="Moderate",
            market_reference_kind="market-implied",
        )
        bd = pl["belief_disagreement"]
        v = build_verification_payload(
            market_data={"forward": 99_000.0, "dist": {"prices": [1.0, 2.0]}},
            summary={"name": "—", "cost_usd": 0.0},
            strategy=None,
            overlay={"payoff_usd": []},
            market_pdf_raw=[],
            call_marks=[],
            belief_verification={
                "enabled": True,
                "center_mode_usd": 100_000.0,
                "sigma_ln_of_price": 0.12,
                "sigma_mkt_at_horizon": 0.10,
            },
            belief_disagreement=bd,
            lab_mode="exact_strikes",
            belief_largest_gap_price_usd=88_000.0,
        )
        g = v.get("belief_vs_market_glance")
        self.assertIsInstance(g, dict)
        self.assertEqual(g["forward_usd"], 99_000.0)
        self.assertEqual(g["strategy_families_heading"], "Strategy families that fit this disagreement")
        self.assertEqual(g["fit_note"], "Fit is not recommendation.")
        self.assertEqual(g["largest_gap_display"], "~$88,000")
        self.assertIsInstance(g.get("digest_lines"), list)
        self.assertGreaterEqual(len(g["digest_lines"]), 4)
        self.assertIn("not predictions", g["digest_lines"][-1].lower())
        self.assertIsInstance(g.get("fit_bridge_bullets"), list)
        self.assertEqual(len(g["fit_bridge_bullets"]), 3)

    def test_glance_none_without_belief_contract(self) -> None:
        v = build_verification_payload(
            market_data={"forward": 99_000.0, "dist": {"prices": [1.0]}},
            summary={"name": "—", "cost_usd": 0.0},
            strategy=None,
            overlay={"payoff_usd": []},
            market_pdf_raw=[],
            call_marks=[],
            belief_verification=None,
            belief_disagreement=None,
            lab_mode=None,
        )
        self.assertIsNone(v.get("belief_vs_market_glance"))


class TestDisagreementScanPayload(unittest.TestCase):
    _BANNED_SUBSTR = (
        "you should",
        "best trade",
        "correct trade",
        "optimal trade",
    )

    def _assert_no_advisory_phrases(self, text: str) -> None:
        low = text.lower()
        for s in self._BANNED_SUBSTR:
            self.assertNotIn(s, low, msg=f"banned advisory fragment: {s!r}")

    def test_digest_order_and_mixed_category(self) -> None:
        pl = belief_disagreement_hints_payload(
            center_usd=100_000.0,
            market_peak=95_000.0,
            sigma_user=0.12,
            sigma_mkt=0.10,
            shape_gap_strength="Moderate",
            market_reference_kind="market-implied",
        )
        bd = pl["belief_disagreement"]
        scan = build_disagreement_scan_payload(bd)
        self.assertIsNotNone(scan)
        assert scan is not None
        lines = scan["digest_lines"]
        self.assertEqual(len(lines), 4)
        self.assertIn("above", lines[0].lower())
        self.assertIn("wider", lines[1].lower())
        self.assertIn("mixed", lines[2].lower())
        self.assertIn("bullish", lines[2].lower())
        full = "\n".join(lines) + scan["fit_bridge_intro"] + "\n".join(scan["fit_bridge_bullets"])
        self._assert_no_advisory_phrases(full)

    def test_directional_bearish_digest(self) -> None:
        pl = belief_disagreement_hints_payload(
            center_usd=90_000.0,
            market_peak=95_000.0,
            sigma_user=0.10,
            sigma_mkt=0.10,
            shape_gap_strength="Low",
            market_reference_kind="market-implied",
        )
        self.assertEqual(pl["category_id"], "directional")
        scan = build_disagreement_scan_payload(pl["belief_disagreement"])
        self.assertIsNotNone(scan)
        assert scan is not None
        self.assertIn("below", scan["digest_lines"][0].lower())
        self.assertIn("similar", scan["digest_lines"][1].lower())
        self.assertIn("directional", scan["digest_lines"][2].lower())
        self.assertIn("bearish", scan["digest_lines"][2].lower())

    def test_aligned_digest(self) -> None:
        pl = belief_disagreement_hints_payload(
            center_usd=95_000.0,
            market_peak=95_000.0,
            sigma_user=0.10,
            sigma_mkt=0.10,
            shape_gap_strength="Low",
            market_reference_kind="market-implied",
        )
        self.assertEqual(pl["category_id"], "aligned")
        scan = build_disagreement_scan_payload(pl["belief_disagreement"])
        self.assertIsNotNone(scan)
        assert scan is not None
        self.assertIn("aligned", scan["digest_lines"][0].lower())
        self.assertIn("aligned", scan["digest_lines"][2].lower())

    def test_fit_bridge_matches_family_count(self) -> None:
        pl = belief_disagreement_hints_payload(
            center_usd=100_000.0,
            market_peak=100_000.0,
            sigma_user=0.15,
            sigma_mkt=0.10,
            shape_gap_strength="Moderate",
            market_reference_kind="market-implied",
        )
        self.assertEqual(pl["category_id"], "width_vol")
        bd = pl["belief_disagreement"]
        scan = build_disagreement_scan_payload(bd)
        self.assertIsNotNone(scan)
        assert scan is not None
        self.assertEqual(len(scan["fit_bridge_bullets"]), len(bd["strategy_families"]))
        self.assertIn("not", scan["fit_bridge_intro"].lower())
        self.assertIn("illustrative", scan["fit_bridge_intro"].lower())

    def test_scan_none_without_trace(self) -> None:
        self.assertIsNone(build_disagreement_scan_payload(None))
        self.assertIsNone(build_disagreement_scan_payload({"category_id": "aligned"}))


if __name__ == "__main__":
    unittest.main()
