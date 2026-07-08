"""Tests for chapter mode lines in operator status formatting."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_operator_status import VERDICT_IDE_BUILD, VERDICT_RUN_LOCAL, _format_human


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

    def test_format_human_closeout_commands_desktop(self) -> None:
        status = {
            "verdict": VERDICT_RUN_LOCAL,
            "chapter_mode": {
                "mode": "CLOSEOUT_ONLY",
                "do_not_rebuild": True,
                "loop_host_allowed": False,
            },
            "commands": ["DESKTOP_CONTINUE.cmd --no-pause (SSH → VM finish_ide_build)"],
            "avoid": ["run_ppe_local.cmd on desktop (forbidden — use DESKTOP_CONTINUE)"],
        }
        text = _format_human(status, Path("."))
        self.assertIn("CLOSEOUT_ONLY", text)
        self.assertIn("Agent action", text)
        self.assertIn("Operator: nothing required", text)
        self.assertIn("DESKTOP_CONTINUE", text)

    def test_format_human_includes_build_worker_preflight(self) -> None:
        status = {
            "verdict": VERDICT_IDE_BUILD,
            "blocker": "product blocked [Slice-A]",
            "supply": {"backlog": {}, "queue_ready": 1},
        }
        with patch(
            "scripts.ppe_build_worker.collect_build_worker_status",
            return_value={
                "pref": "codex",
                "worker": "codex-cli",
                "preflight": {"classification": "ready", "detail": "Codex CLI headless ready"},
            },
        ):
            text = _format_human(status, Path("."))
        self.assertIn("Build worker preflight: `ready`", text)
        self.assertIn("Codex CLI headless ready", text)


if __name__ == "__main__":
    unittest.main()
