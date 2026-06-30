"""Tests for chapter mode lines in operator status formatting."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.ppe_operator_status import VERDICT_RUN_LOCAL, _format_human


class TestOperatorStatusChapterMode(unittest.TestCase):
    def test_format_human_includes_closeout_mode(self) -> None:
        status = {
            "verdict": VERDICT_RUN_LOCAL,
            "chapter_mode": {
                "mode": "CLOSEOUT_ONLY",
                "do_not_rebuild": True,
                "product_slices_on_main": ["Ch-Product-Slice002"],
                "agent_instructions": ["Do NOT re-BUILD product."],
                "pending_closeout_chapters": ["msos_strategy_lab_dist_download_v1"],
                "next_build_candidate": "msos_trader_workflow_horizon_nav_v1",
            },
            "preflight_warnings": ["checkout is 'fix/foo', not main"],
        }
        text = _format_human(status, Path("."))
        self.assertIn("CLOSEOUT_ONLY", text)
        self.assertIn("Preflight warnings (action required", text)
        self.assertIn("RECOVERY_PROTOCOL", text)


if __name__ == "__main__":
    unittest.main()
