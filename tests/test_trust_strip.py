"""Sprint 006: always-visible trust strip lines from verification_summary (+ optional belief note)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.viz.decision_ready_review import assert_no_advisory_language
from src.viz.implied_lab_provenance import TRUST_STRIP_FALLBACK_LINE, build_trust_strip_lines


class TestTrustStripLines(unittest.TestCase):
    def test_none_verification_fallback_only(self) -> None:
        lines = build_trust_strip_lines(None)
        self.assertEqual(lines, [TRUST_STRIP_FALLBACK_LINE])
        assert_no_advisory_language("\n".join(lines))

    def test_empty_verification_summary_fallback(self) -> None:
        lines = build_trust_strip_lines({"verification_summary": {}})
        self.assertEqual(lines, [TRUST_STRIP_FALLBACK_LINE])

    def test_missing_verification_summary_fallback(self) -> None:
        lines = build_trust_strip_lines({"data_sources": ["Deribit"]})
        self.assertEqual(lines, [TRUST_STRIP_FALLBACK_LINE])

    def test_minimal_summary_required_strings(self) -> None:
        vs = {
            "as_of_utc": "2026-04-10T12:00:00+00:00",
            "data_sources": ["Deribit"],
            "overlay_basis": "Green overlay: strikes from exact K1–K4 using listed option marks.",
            "strategy_families_scope": (
                "Strategy families in the belief panel are illustrative_pattern fit classes only — "
                "not optimized tickets."
            ),
        }
        lines = build_trust_strip_lines({"verification_summary": vs})
        joined = "\n".join(lines)
        self.assertIn("As of (UTC):", joined)
        self.assertIn("2026-04-10T12:00:00+00:00", joined)
        self.assertIn("Sources:", joined)
        self.assertIn("Deribit", joined)
        self.assertIn("Overlay basis:", joined)
        self.assertIn("Green overlay:", joined)
        self.assertIn("illustrative_pattern", joined)
        self.assertIn("not optimized tickets", joined)
        self.assertIn("Full traces and numeric inputs", joined)
        self.assertIn("Verification", joined)
        assert_no_advisory_language(joined)

    def test_empty_data_sources_placeholder(self) -> None:
        vs = {
            "as_of_utc": "2026-01-01T00:00:00+00:00",
            "data_sources": [],
            "overlay_basis": "Green overlay: test.",
            "strategy_families_scope": "Illustrative scope line.",
        }
        lines = build_trust_strip_lines({"verification_summary": vs})
        self.assertTrue(any("not listed for this run" in ln for ln in lines))

    def test_belief_note_appended_when_enabled(self) -> None:
        vs = {
            "as_of_utc": "2026-01-01T00:00:00+00:00",
            "data_sources": ["Deribit"],
            "overlay_basis": "Green overlay: x.",
            "strategy_families_scope": "Scope.",
        }
        belief = {
            "enabled": True,
            "note": "Subjective lognormal-style overlay for comparison; not the risk-neutral distribution.",
        }
        lines = build_trust_strip_lines({"verification_summary": vs, "belief": belief})
        joined = "\n".join(lines)
        self.assertIn("Belief (teal):", joined)
        self.assertIn("Subjective lognormal-style overlay", joined)
        assert_no_advisory_language(joined)

    def test_belief_note_skipped_when_disabled_or_invalid(self) -> None:
        vs = {
            "as_of_utc": "2026-01-01T00:00:00+00:00",
            "data_sources": ["A"],
            "overlay_basis": "o",
            "strategy_families_scope": "s",
        }
        off = build_trust_strip_lines(
            {"verification_summary": vs, "belief": {"enabled": False, "note": "should not show"}}
        )
        self.assertFalse(any("should not show" in ln for ln in off))
        inv = build_trust_strip_lines(
            {
                "verification_summary": vs,
                "belief": {"enabled": True, "invalid": True, "note": "should not show"},
            }
        )
        self.assertFalse(any("should not show" in ln for ln in inv))


if __name__ == "__main__":
    unittest.main()
