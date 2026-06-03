"""Tests for ppe_context_bands."""

from __future__ import annotations

import unittest

from scripts.ppe_context_bands import (
    ESCALATE_LINE_THRESHOLD,
    WATCH_LINE_THRESHOLD,
    advisory_actions,
    classify_line_count,
    score_build_packet,
    worst_band,
)


class TestPpeContextBands(unittest.TestCase):
    def test_classify_normal(self) -> None:
        self.assertEqual(classify_line_count(WATCH_LINE_THRESHOLD), "NORMAL")
        self.assertEqual(classify_line_count(100), "NORMAL")

    def test_classify_watch(self) -> None:
        self.assertEqual(classify_line_count(WATCH_LINE_THRESHOLD + 1), "WATCH")
        self.assertEqual(classify_line_count(ESCALATE_LINE_THRESHOLD), "WATCH")

    def test_classify_escalate(self) -> None:
        self.assertEqual(classify_line_count(ESCALATE_LINE_THRESHOLD + 1), "ESCALATE")

    def test_worst_band(self) -> None:
        self.assertEqual(worst_band("NORMAL", "WATCH"), "WATCH")
        self.assertEqual(worst_band("WATCH", "ESCALATE", "NORMAL"), "ESCALATE")

    def test_score_build_packet(self) -> None:
        text = "\n".join(["line"] * 250)
        scored = score_build_packet(text)
        self.assertEqual(scored["band"], "WATCH")
        self.assertEqual(scored["line_count"], 250)
        self.assertTrue(advisory_actions("WATCH"))


if __name__ == "__main__":
    unittest.main()
