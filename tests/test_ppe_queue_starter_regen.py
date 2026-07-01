"""IDE BUILD starter auto-regen when queue promotes to READY."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_ide_build_starter import starter_path
from scripts.ppe_queue import upsert_queue_item


class TestPpeQueueStarterRegen(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        plans = sop / "PHASE_PLANS"
        sop.mkdir(parents=True, exist_ok=True)
        plans.mkdir(parents=True, exist_ok=True)
        self.plan_rel = "docs/SOP/PHASE_PLANS/test_chapter_v1_relay.json"
        (plans / "test_chapter_v1_relay.json").write_text(
            json.dumps(
                {
                    "sprintSpecPath": "docs/SOP/SPRINT_TEST_CHAPTER_V1.md",
                    "selectionRecord": "docs/SOP/POST_TEST_CHAPTER_V1_SELECTION.md",
                    "slices": [
                        {
                            "sliceId": "Test-Chapter-Product-Slice001",
                            "declaredPlane": "PRODUCT-PLANE",
                            "layerPreset": "PPE_UI",
                            "buildBranch": "build/auto/Test-Chapter-Product-Slice001",
                            "touchSet": ["src/viz/test_widget.py"],
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
        (sop / "SPRINT_TEST_CHAPTER_V1.md").write_text("# sprint\n", encoding="utf-8")
        (sop / "POST_TEST_CHAPTER_V1_SELECTION.md").write_text("# sel\n", encoding="utf-8")
        (sop / "PHASE_QUEUE.json").write_text(json.dumps({"version": 1, "items": []}), encoding="utf-8")
        presets_src = Path(__file__).resolve().parents[1] / "docs" / "SOP" / "REPO_LAYER_PATH_PREFIXES.json"
        if presets_src.is_file():
            (sop / "REPO_LAYER_PATH_PREFIXES.json").write_text(
                presets_src.read_text(encoding="utf-8"),
                encoding="utf-8",
            )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_upsert_ready_regenerates_product_starter(self) -> None:
        rel_starter = starter_path("Test-Chapter-Product-Slice001")
        starter_file = self.repo / rel_starter
        self.assertFalse(starter_file.is_file())

        ok, msg = upsert_queue_item(self.repo, plan_path=self.plan_rel, status="READY")
        self.assertTrue(ok)
        self.assertIn("regen starters", msg)
        self.assertTrue(starter_file.is_file())
        self.assertIn("Test-Chapter-Product-Slice001", starter_file.read_text(encoding="utf-8"))

    def test_upsert_ready_idempotent_no_duplicate_regen_msg(self) -> None:
        upsert_queue_item(self.repo, plan_path=self.plan_rel, status="READY")
        _ok, msg = upsert_queue_item(self.repo, plan_path=self.plan_rel, status="READY")
        self.assertNotIn("regen starters", msg)


if __name__ == "__main__":
    unittest.main()
