"""Tests for PHASE_SELECTION_ROADMAP auto-SELECTION."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_auto_select import run_auto_select
from scripts.ppe_manifest import load_manifest, save_manifest
from scripts.ppe_roadmap import (
    advance_after_chapter_closeout,
    bootstrap_next_ready,
    load_roadmap,
    prepare_selection_idle,
    save_roadmap,
    sync_roadmap_to_queue,
)
from scripts.ppe_queue import load_queue


class TestPpeRoadmap(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        plans = sop / "PHASE_PLANS"
        plans.mkdir(parents=True)

        def _plan(name: str, chapter: str) -> None:
            body = {
                "name": name,
                "sprintSpecPath": f"docs/SOP/SPRINT_{chapter}.md",
                "selectionRecord": f"docs/SOP/SEL_{chapter}.md",
                "slices": [{"sliceId": f"{chapter}-Closeout", "closeout": {"chapterId": chapter}}],
            }
            (plans / f"{chapter}.json").write_text(json.dumps(body), encoding="utf-8")
            (sop / f"SPRINT_{chapter}.md").write_text("# sprint\n", encoding="utf-8")
            (sop / f"SEL_{chapter}.md").write_text("# sel\n", encoding="utf-8")

        _plan("chapter_a", "A")
        _plan("chapter_b", "B")

        roadmap = {
            "version": 1,
            "items": [
                {
                    "planPath": "docs/SOP/PHASE_PLANS/A.json",
                    "status": "done",
                },
                {
                    "planPath": "docs/SOP/PHASE_PLANS/B.json",
                    "status": "pending",
                    "reason": "next chapter",
                    "workerMode": "deterministic",
                },
            ],
        }
        (sop / "PHASE_SELECTION_ROADMAP.json").write_text(
            json.dumps(roadmap, indent=2),
            encoding="utf-8",
        )
        (sop / "PHASE_QUEUE.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "items": [
                        {"planPath": "docs/SOP/PHASE_PLANS/A.json", "status": "DONE"},
                    ],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        (sop / "ACTIVE_PHASE_MANIFEST.json").write_text(
            json.dumps({"phasePlanPath": "", "status": "COMPLETE", "notes": ""}, indent=2),
            encoding="utf-8",
        )
        os.environ.pop("PPE_AUTO_ROADMAP", None)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_bootstrap_promotes_first_pending(self) -> None:
        out = bootstrap_next_ready(self.repo, apply=True)
        self.assertTrue(out.get("bootstrapped"))
        self.assertEqual(
            out.get("planPath"),
            "docs/SOP/PHASE_PLANS/B.json",
        )
        roadmap = load_roadmap(self.repo)
        row = next(i for i in roadmap["items"] if i["planPath"].endswith("B.json"))
        self.assertEqual(row["status"], "ready")
        queue = load_queue(self.repo)
        b = next(i for i in queue["items"] if i["planPath"].endswith("B.json"))
        self.assertEqual(b["status"], "READY")
        self.assertEqual(b.get("workerMode"), "deterministic")

    def test_advance_after_closeout(self) -> None:
        roadmap = load_roadmap(self.repo)
        for item in roadmap["items"]:
            if item["planPath"].endswith("B.json"):
                item["status"] = "pending"
        save_roadmap(self.repo, roadmap)
        adv = advance_after_chapter_closeout(
            self.repo,
            closed_plan_path="docs/SOP/PHASE_PLANS/A.json",
            apply=True,
        )
        self.assertTrue(adv.get("advanced"))
        self.assertEqual(adv.get("nextPlan"), "docs/SOP/PHASE_PLANS/B.json")

    def test_prepare_and_auto_select(self) -> None:
        prep = prepare_selection_idle(self.repo, apply=True)
        self.assertFalse(prep.get("skipped"))
        rc = run_auto_select(self.repo, apply=True, select_only=False, mark_done=False, force=False)
        self.assertEqual(rc, 0)
        manifest = load_manifest(self.repo)
        self.assertEqual(manifest["status"], "READY")
        self.assertEqual(manifest["phasePlanPath"], "docs/SOP/PHASE_PLANS/B.json")

    def test_sync_planned_queue_row(self) -> None:
        sync_roadmap_to_queue(self.repo, apply=True)
        queue = load_queue(self.repo)
        b = next(i for i in queue["items"] if i["planPath"].endswith("B.json"))
        self.assertEqual(b["status"], "PLANNED")

    def test_roadmap_disabled_by_env(self) -> None:
        os.environ["PPE_AUTO_ROADMAP"] = "0"
        save_manifest(
            self.repo,
            {"phasePlanPath": "", "status": "COMPLETE", "notes": ""},
        )
        out = bootstrap_next_ready(self.repo, apply=True)
        self.assertFalse(out.get("bootstrapped"))


if __name__ == "__main__":
    unittest.main()
