"""Tests for bounded SELECTION automation (ppe_auto_select + ppe_queue)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_auto_select import run_auto_select
from scripts.ppe_manifest import load_manifest, save_manifest
from scripts.ppe_queue import load_queue, mark_queue_item_done


class TestPpeAutoSelect(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        plans = sop / "PHASE_PLANS"
        plans.mkdir(parents=True)
        plan_a = {
            "name": "chapter_a",
            "sprintSpecPath": "docs/SOP/SPRINT_A.md",
            "selectionRecord": "docs/SOP/SEL_A.md",
            "slices": [{"sliceId": "A-Closeout", "closeout": {"chapterId": "a"}}],
        }
        plan_b = {
            "name": "chapter_b",
            "sprintSpecPath": "docs/SOP/SPRINT_B.md",
            "selectionRecord": "docs/SOP/SEL_B.md",
            "slices": [{"sliceId": "B-Closeout", "closeout": {"chapterId": "b"}}],
        }
        (plans / "chapter_a.json").write_text(json.dumps(plan_a), encoding="utf-8")
        (plans / "chapter_b.json").write_text(json.dumps(plan_b), encoding="utf-8")
        (sop / "SPRINT_A.md").write_text("# A\n", encoding="utf-8")
        (sop / "SPRINT_B.md").write_text("# B\n", encoding="utf-8")
        (sop / "SEL_A.md").write_text("# A\n", encoding="utf-8")
        (sop / "SEL_B.md").write_text("# B\n", encoding="utf-8")
        queue = {
            "version": 1,
            "items": [
                {
                    "planPath": "docs/SOP/PHASE_PLANS/chapter_a.json",
                    "status": "DONE",
                },
                {
                    "planPath": "docs/SOP/PHASE_PLANS/chapter_b.json",
                    "status": "READY",
                    "reason": "test next",
                },
            ],
        }
        (sop / "PHASE_QUEUE.json").write_text(json.dumps(queue, indent=2), encoding="utf-8")
        manifest = {
            "phasePlanPath": "docs/SOP/PHASE_PLANS/chapter_a.json",
            "sprintSpecPath": "docs/SOP/SPRINT_A.md",
            "status": "COMPLETE",
            "notes": "closed",
        }
        (sop / "ACTIVE_PHASE_MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_complete_manifest_finalizes_and_selects_next(self) -> None:
        rc = run_auto_select(self.repo, apply=True, select_only=False, mark_done=False, force=False)
        self.assertEqual(rc, 0)
        manifest = load_manifest(self.repo)
        self.assertEqual(manifest["status"], "READY")
        self.assertEqual(
            manifest["phasePlanPath"],
            "docs/SOP/PHASE_PLANS/chapter_b.json",
        )
        queue = load_queue(self.repo)
        self.assertEqual(queue["items"][0]["status"], "DONE")
        self.assertEqual(queue["items"][1]["status"], "READY")

    def test_mark_queue_item_done(self) -> None:
        ok, _ = mark_queue_item_done(
            self.repo,
            plan_path="docs/SOP/PHASE_PLANS/chapter_b.json",
        )
        self.assertTrue(ok)
        queue = load_queue(self.repo)
        self.assertEqual(queue["items"][1]["status"], "DONE")

    def test_idle_when_no_ready_items(self) -> None:
        save_manifest(
            self.repo,
            {
                "phasePlanPath": "",
                "status": "COMPLETE",
                "notes": "",
            },
        )
        queue = load_queue(self.repo)
        for item in queue["items"]:
            item["status"] = "DONE"
        from scripts.ppe_queue import save_queue

        save_queue(self.repo, queue)
        rc = run_auto_select(self.repo, apply=True, select_only=False, mark_done=False, force=False)
        self.assertEqual(rc, 0)
        manifest = load_manifest(self.repo)
        self.assertEqual(manifest.get("phasePlanPath"), "")


if __name__ == "__main__":
    unittest.main()
