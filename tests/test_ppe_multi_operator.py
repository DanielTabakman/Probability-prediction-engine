"""Tests for propagation preview and multi-operator coordinator."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_manifest import save_manifest
from scripts.ppe_multi_operator import collect_multi_operator_status
from scripts.ppe_propagate_queue import preview_next_chapter
from scripts.ppe_roadmap import load_roadmap, save_roadmap


class TestPropagationPreview(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        plans = sop / "PHASE_PLANS"
        plans.mkdir(parents=True)
        for slug in ("active", "next"):
            plan = {
                "name": slug,
                "sprintSpecPath": f"docs/SOP/SPRINT_{slug.upper()}.md",
                "slices": [{"sliceId": f"{slug}-Closeout", "closeout": {"chapterId": slug}}],
            }
            (plans / f"{slug}_relay.json").write_text(json.dumps(plan), encoding="utf-8")
            (sop / f"SPRINT_{slug.upper()}.md").write_text("# s\n", encoding="utf-8")
        save_roadmap(
            self.repo,
            {
                "version": 1,
                "items": [
                    {"planPath": "docs/SOP/PHASE_PLANS/active_relay.json", "status": "ready"},
                    {"planPath": "docs/SOP/PHASE_PLANS/next_relay.json", "status": "pending"},
                ],
            },
        )
        save_manifest(
            self.repo,
            {
                "phasePlanPath": "docs/SOP/PHASE_PLANS/active_relay.json",
                "status": "RUNNING",
            },
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_preview_next_after_active(self) -> None:
        preview = preview_next_chapter(self.repo)
        self.assertEqual(preview.get("next_plan_path"), "docs/SOP/PHASE_PLANS/next_relay.json")
        self.assertEqual(preview.get("next_source"), "roadmap_after_active")


class TestMultiOperator(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True)
        (sop / "PPE_OPERATOR_INSTANCES.example.json").write_text(
            json.dumps({"version": 1, "instances": [{"id": "primary", "repoRoot": ".", "label": "p"}]}),
            encoding="utf-8",
        )
        (sop / "ACTIVE_PHASE_MANIFEST.json").write_text(
            json.dumps({"phasePlanPath": "", "status": "COMPLETE"}),
            encoding="utf-8",
        )
        (sop / "PHASE_QUEUE.json").write_text(json.dumps({"version": 1, "items": []}), encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_collect_multi_status(self) -> None:
        data = collect_multi_operator_status(self.repo)
        self.assertGreaterEqual(data.get("instance_count"), 1)
        self.assertTrue(data.get("instances"))


if __name__ == "__main__":
    unittest.main()
