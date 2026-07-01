"""Tests for chapter coordination audit/repair."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_chapter_coordination import (
    assess_chapter_coordination_health,
    audit_chapter,
    format_operator_coordination_lines,
    paths_touch_coordination,
    plan_coordination_repair,
    repair_chapter,
    repair_repo_coordination,
)
from scripts.ppe_manifest import save_manifest


class TestChapterCoordination(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        plans = sop / "PHASE_PLANS"
        plans.mkdir(parents=True)
        apps = self.repo / "apps" / "msos-web" / "src" / "app"
        apps.mkdir(parents=True)
        (apps / "page.tsx").write_text("export default function Page() { return null; }\n", encoding="utf-8")

        self.plan_rel = "docs/SOP/PHASE_PLANS/msos_storyboard_visual_parity_v1_relay.json"
        plan = {
            "name": "msos_storyboard_visual_parity_v1",
            "baselineBranch": "main",
            "slices": [
                {
                    "sliceId": "MSOS-VisParityV1-Product-Slice002",
                    "layerPreset": "MSOS_UI",
                    "buildBranch": "build/auto/MSOS-VisParityV1-Product-Slice002",
                    "touchSet": ["apps/msos-web/src/app/page.tsx"],
                },
                {
                    "sliceId": "MSOS-VisParityV1-Closeout-Slice009",
                    "closeout": {
                        "evidenceDoc": "docs/SOP/VIS_PARITY_EVIDENCE.md",
                    },
                },
            ],
        }
        (plans / "msos_storyboard_visual_parity_v1_relay.json").write_text(json.dumps(plan), encoding="utf-8")
        (sop / "VIS_PARITY_EVIDENCE.md").write_text(
            "# Evidence\n\n**Status:** **PENDING**\n\n| Slice | Status |\n| --- | --- |\n| MSOS-VisParityV1-Product-Slice002 | PENDING |\n",
            encoding="utf-8",
        )
        (sop / "PHASE_QUEUE.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "items": [
                        {
                            "planPath": self.plan_rel,
                            "status": "READY",
                            "reason": "test",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (sop / "AGENT_STEERING_V1.json").write_text(
            json.dumps({"version": 1, "closeoutOnlyChapterIds": []}),
            encoding="utf-8",
        )
        (sop / "MSOS_FRONTIER.md").write_text(
            "### msos storyboard visual parity v1 — relay queue — **COMPLETE**\n",
            encoding="utf-8",
        )
        save_manifest(
            self.repo,
            {
                "phasePlanPath": self.plan_rel,
                "status": "READY",
                "notes": "test",
            },
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_paths_touch_coordination(self) -> None:
        self.assertTrue(paths_touch_coordination(["docs/SOP/PHASE_QUEUE.json"]))
        self.assertTrue(paths_touch_coordination(["apps/msos-web/src/app/page.tsx"]))
        self.assertFalse(paths_touch_coordination(["scripts/ppe_foo.py"]))

    def test_audit_detects_marker_and_registry_gaps(self) -> None:
        issues = audit_chapter(self.repo, self.plan_rel)
        codes = {i["code"] for i in issues}
        self.assertIn("PRODUCT_ON_MAIN_NO_MARKER", codes)
        self.assertIn("CLOSEOUT_REGISTRY_MISSING", codes)
        self.assertIn("FRONTIER_AHEAD_OF_EVIDENCE", codes)
        self.assertIn("QUEUE_ACTIVE_PRODUCT_DESYNC", codes)

    def test_repair_marks_slices_and_registry(self) -> None:
        fixes, remaining = repair_chapter(self.repo, self.plan_rel, apply=True)
        actions = {f["action"] for f in fixes}
        self.assertIn("mark_ide_product_ready", actions)
        self.assertIn("add_closeout_registry", actions)
        marker = json.loads(
            (self.repo / "artifacts/orchestrator/IDE_PRODUCT_READY.json").read_text(encoding="utf-8")
        )
        self.assertIn("MSOS-VisParityV1-Product-Slice002", marker.get("completedProductSlices") or [])
        steering = json.loads((self.repo / "docs/SOP/AGENT_STEERING_V1.json").read_text(encoding="utf-8"))
        self.assertIn("msos_storyboard_visual_parity_v1", steering.get("closeoutOnlyChapterIds") or [])
        codes = {i["code"] for i in remaining}
        self.assertIn("FRONTIER_AHEAD_OF_EVIDENCE", codes)

    def test_assess_and_format_operator_lines_before_repair(self) -> None:
        health = assess_chapter_coordination_health(self.repo)
        self.assertFalse(health.get("ok"))
        self.assertGreater(int(health.get("repairable_plan_count") or 0), 0)
        lines = format_operator_coordination_lines(self.repo)
        joined = "\n".join(lines)
        self.assertIn("Chapter coordination", joined)
        self.assertIn("WARN", joined)

    def test_repair_repo_clears_marker_desync(self) -> None:
        plan = plan_coordination_repair(self.repo)
        self.assertGreater(plan.get("repairable_plan_count", 0), 0)
        out = repair_repo_coordination(self.repo, apply=True)
        self.assertGreater(out.get("fix_count", 0), 0)
        health = assess_chapter_coordination_health(self.repo)
        codes = {i.get("code") for i in health.get("issues") or []}
        self.assertNotIn("PRODUCT_ON_MAIN_NO_MARKER", codes)
        self.assertNotIn("QUEUE_ACTIVE_PRODUCT_DESYNC", codes)
        self.assertNotIn("CLOSEOUT_REGISTRY_MISSING", codes)


if __name__ == "__main__":
    unittest.main()
