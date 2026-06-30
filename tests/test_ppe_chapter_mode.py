"""Tests for chapter mode resolution (CLOSEOUT_ONLY vs IDE_BUILD)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_chapter_mode import (
    MODE_CLOSEOUT_ONLY,
    MODE_IDE_BUILD,
    MODE_RUN_LOCAL,
    compose_steward_action_snippet,
    format_chapter_mode_block,
    plan_chapter_id,
    resolve_chapter_mode,
)


class TestPpeChapterMode(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True)
        (sop / "ACTIVE_PRODUCT_DIRECTION.json").write_text(
            json.dumps({"nextStewardAction": "fallback"}, indent=2),
            encoding="utf-8",
        )
        (sop / "AGENT_STEERING_V1.json").write_text(
            json.dumps(
                {
                    "closeoutOnlyChapterIds": [
                        "msos_strategy_lab_dist_download_v1",
                    ],
                    "nextBuildCandidateId": "msos_trader_workflow_horizon_nav_v1",
                    "nextBuildCandidateNote": "promote READY",
                    "spineQueueAfterCloseout": ["msos_cross_venue_strategy_lab_v1"],
                    "parallelWork": "Asset batch wave 1 parallel.",
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_plan_chapter_id(self) -> None:
        self.assertEqual(
            plan_chapter_id("docs/SOP/PHASE_PLANS/foo_relay.json"),
            "foo",
        )

    def test_closeout_only_on_run_local_with_registry(self) -> None:
        plan = "docs/SOP/PHASE_PLANS/msos_strategy_lab_dist_download_v1_relay.json"
        with patch("scripts.ppe_chapter_mode.product_slices_on_main", return_value=["Ch-Product"]):
            info = resolve_chapter_mode(
                self.repo,
                verdict="RUN_LOCAL",
                plan_path=plan,
                guard_reason=None,
                chapter_name="MSOS Strategy Lab distribution CSV download",
            )
        self.assertEqual(info["mode"], MODE_CLOSEOUT_ONLY)
        self.assertTrue(info["do_not_rebuild"])
        block = format_chapter_mode_block(info)
        self.assertTrue(any("CLOSEOUT_ONLY" in line for line in block))

    def test_ide_build_when_not_on_main(self) -> None:
        with patch("scripts.ppe_chapter_mode.product_slices_on_main", return_value=[]):
            info = resolve_chapter_mode(
                self.repo,
                verdict="IDE_BUILD",
                plan_path="docs/SOP/PHASE_PLANS/new_chapter_relay.json",
                guard_reason="PRODUCT_BLOCKED",
            )
        self.assertEqual(info["mode"], MODE_IDE_BUILD)
        self.assertFalse(info["do_not_rebuild"])

    def test_ide_build_closeout_registry_without_on_main_checkout(self) -> None:
        plan = "docs/SOP/PHASE_PLANS/msos_strategy_lab_dist_download_v1_relay.json"
        with patch("scripts.ppe_chapter_mode.product_slices_on_main", return_value=[]):
            info = resolve_chapter_mode(
                self.repo,
                verdict="IDE_BUILD",
                plan_path=plan,
                guard_reason="PRODUCT_BLOCKED",
                chapter_name="MSOS Strategy Lab distribution CSV download",
            )
        self.assertEqual(info["mode"], MODE_CLOSEOUT_ONLY)
        self.assertTrue(info["do_not_rebuild"])

    def test_ide_marker_ok_is_closeout_only(self) -> None:
        info = resolve_chapter_mode(
            self.repo,
            verdict="RUN_LOCAL",
            plan_path="docs/SOP/PHASE_PLANS/x_relay.json",
            guard_reason="IDE_MARKER_OK",
        )
        self.assertEqual(info["mode"], MODE_CLOSEOUT_ONLY)
        self.assertTrue(info["do_not_rebuild"])

    def test_run_local_without_on_main(self) -> None:
        with patch("scripts.ppe_chapter_mode.product_slices_on_main", return_value=[]):
            info = resolve_chapter_mode(
                self.repo,
                verdict="RUN_LOCAL",
                plan_path="docs/SOP/PHASE_PLANS/x_relay.json",
                guard_reason=None,
            )
        self.assertEqual(info["mode"], MODE_RUN_LOCAL)

    def test_compose_steward_action_snippet(self) -> None:
        text = compose_steward_action_snippet(self.repo)
        self.assertIn("msos_trader_workflow_horizon_nav_v1", text)
        self.assertIn("do NOT re-BUILD", text)
        self.assertIn("OPERATOR_STATUS Mode", text)


if __name__ == "__main__":
    unittest.main()
