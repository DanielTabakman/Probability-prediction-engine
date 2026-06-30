"""Tests for SOP / chapter doc discovery."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.sop_discovery_core import (
    build_chapter_doc_index,
    resolve_by_chapter,
    resolve_by_topic,
    write_chapter_doc_index,
)


class TestResolveSop(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        plans = self.repo / "docs" / "SOP" / "PHASE_PLANS"
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True, exist_ok=True)
        plans.mkdir(parents=True, exist_ok=True)

        plan_rel = "docs/SOP/PHASE_PLANS/ppe_exposure_menu_v1_relay.json"
        (plans / "ppe_exposure_menu_v1_relay.json").write_text(
            json.dumps(
                {
                    "sprintSpecPath": "docs/SOP/SPRINT_PPE_EXPOSURE_MENU_V1.md",
                    "selectionRecord": "docs/SOP/POST_PPE_EXPOSURE_MENU_V1_SELECTION.md",
                    "slices": [
                        {
                            "sliceId": "Closeout",
                            "closeout": {
                                "chapterId": "ppe_exposure_menu_v1",
                                "evidenceDoc": "docs/SOP/PPE_EXPOSURE_MENU_V1_EVIDENCE_STATUS.md",
                                "sprintSpec": "docs/SOP/SPRINT_PPE_EXPOSURE_MENU_V1.md",
                                "selectionOutcomeDoc": "docs/SOP/POST_PPE_EXPOSURE_MENU_V1_SELECTION.md",
                            },
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (sop / "SPRINT_PPE_EXPOSURE_MENU_V1.md").write_text("# sprint\n", encoding="utf-8")
        (sop / "POST_PPE_EXPOSURE_MENU_V1_SELECTION.md").write_text("# sel\n", encoding="utf-8")
        (sop / "PPE_EXPOSURE_MENU_V1_EVIDENCE_STATUS.md").write_text(
            "**Status:** **COMPLETE**\n",
            encoding="utf-8",
        )
        (sop / "PHASE_QUEUE.json").write_text(
            json.dumps(
                {
                    "items": [
                        {
                            "planPath": plan_rel,
                            "status": "DONE",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        self.plan_rel = plan_rel

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_resolve_by_chapter(self) -> None:
        report = resolve_by_chapter(self.repo, chapter_id="ppe_exposure_menu_v1")
        self.assertTrue(report["ok"])
        self.assertEqual(report["chapter_id"], "ppe_exposure_menu_v1")
        self.assertIn("docs/SOP/SPRINT_PPE_EXPOSURE_MENU_V1.md", report["load_for_build"])

    def test_resolve_by_topic_asset_batch(self) -> None:
        report = resolve_by_topic("asset batch wave 1")
        self.assertTrue(report["ok"])
        self.assertEqual(report["topic_route_id"], "asset_batch")
        self.assertIn("docs/SOP/ASSET_BATCH_EXPANSION_POLICY_V1.md", report["load_always"])

    def test_build_and_write_index(self) -> None:
        index = build_chapter_doc_index(self.repo)
        self.assertEqual(index["chapter_count"], 1)
        self.assertIn("ppe_exposure_menu_v1", index["by_chapter_id"])
        out = write_chapter_doc_index(self.repo)
        self.assertTrue(out.is_file())
        loaded = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(loaded["chapter_count"], 1)


if __name__ == "__main__":
    unittest.main()
