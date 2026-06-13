"""Tests for ppe_queue_insert_after relative roadmap/queue placement."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_queue_insert_after import insert_chapter_after


class TestPpeQueueInsertAfter(unittest.TestCase):
    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.repo = Path(self._td.name)
        sop = self.repo / "docs" / "SOP"
        plans = sop / "PHASE_PLANS"
        plans.mkdir(parents=True)

        anchor_plan = plans / "anchor_relay.json"
        new_plan = plans / "new_relay.json"
        anchor_plan.write_text(
            json.dumps(
                {
                    "name": "anchor",
                    "baselineBranch": "main",
                    "sprintSpecPath": "docs/SOP/SPRINT_ANCHOR.md",
                    "selectionRecord": "docs/SOP/POST_ANCHOR.md",
                    "slices": [
                        {
                            "sliceId": "Anchor-Control-001",
                            "layerPreset": "CONTROL",
                            "sprintSpecPath": "docs/SOP/SPRINT_ANCHOR.md",
                            "buildBranch": "build/auto/anchor",
                            "declaredPlane": "EVIDENCE-PLANE",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        new_plan.write_text(
            json.dumps(
                {
                    "name": "new",
                    "baselineBranch": "main",
                    "sprintSpecPath": "docs/SOP/SPRINT_NEW.md",
                    "selectionRecord": "docs/SOP/POST_NEW.md",
                    "slices": [
                        {
                            "sliceId": "New-Control-001",
                            "layerPreset": "CONTROL",
                            "sprintSpecPath": "docs/SOP/SPRINT_NEW.md",
                            "buildBranch": "build/auto/new",
                            "declaredPlane": "EVIDENCE-PLANE",
                        },
                        {
                            "sliceId": "New-Closeout-002",
                            "layerPreset": "CONTROL",
                            "sprintSpecPath": "docs/SOP/SPRINT_NEW.md",
                            "buildBranch": "build/auto/new-closeout",
                            "declaredPlane": "EVIDENCE-PLANE",
                            "closeout": {
                                "chapterId": "new_chapter",
                                "chapterTitle": "new",
                                "chapterStatus": "COMPLETE",
                                "evidenceDoc": "docs/SOP/NEW_EVIDENCE.md",
                                "sprintSpec": "docs/SOP/SPRINT_NEW.md",
                                "selectionOutcomeDoc": "docs/SOP/POST_NEW.md",
                                "nextSelectionDoc": "docs/SOP/MVP1_FRONTIER.md",
                            },
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )

        (sop / "PHASE_SELECTION_ROADMAP.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "items": [
                        {"planPath": str(anchor_plan.relative_to(self.repo)).replace("\\", "/"), "status": "ready"},
                        {"planPath": "docs/SOP/PHASE_PLANS/tail_relay.json", "status": "pending"},
                    ],
                }
            ),
            encoding="utf-8",
        )
        (sop / "PHASE_QUEUE.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "items": [
                        {
                            "planPath": str(anchor_plan.relative_to(self.repo)).replace("\\", "/"),
                            "status": "READY",
                        },
                        {"planPath": "docs/SOP/PHASE_PLANS/tail_relay.json", "status": "PLANNED"},
                    ],
                }
            ),
            encoding="utf-8",
        )
        (sop / "PHASE_CHAPTER_BACKLOG.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "items": [
                        {
                            "chapterId": "new_chapter",
                            "status": "blocked",
                            "planPath": str(new_plan.relative_to(self.repo)).replace("\\", "/"),
                            "selectionRecord": "docs/SOP/POST_NEW.md",
                            "reason": "test insert",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        self.anchor_rel = str(anchor_plan.relative_to(self.repo)).replace("\\", "/")
        self.new_rel = str(new_plan.relative_to(self.repo)).replace("\\", "/")

    def tearDown(self) -> None:
        self._td.cleanup()

    def test_insert_after_places_before_tail(self) -> None:
        out = insert_chapter_after(
            self.repo,
            chapter_id="new_chapter",
            after_plan=self.anchor_rel,
            apply=True,
        )
        self.assertEqual(out["roadmapIndex"], 1)
        roadmap = json.loads((self.repo / "docs/SOP/PHASE_SELECTION_ROADMAP.json").read_text(encoding="utf-8"))
        plans = [item["planPath"] for item in roadmap["items"]]
        self.assertEqual(plans[1], self.new_rel)
        self.assertEqual(plans[2], "docs/SOP/PHASE_PLANS/tail_relay.json")

        queue = json.loads((self.repo / "docs/SOP/PHASE_QUEUE.json").read_text(encoding="utf-8"))
        q_plans = [item["planPath"] for item in queue["items"]]
        self.assertEqual(q_plans[1], self.new_rel)

        backlog = json.loads((self.repo / "docs/SOP/PHASE_CHAPTER_BACKLOG.json").read_text(encoding="utf-8"))
        row = backlog["items"][0]
        self.assertEqual(row["status"], "chartered")
        self.assertEqual(row["queueAfterPlanPath"], self.anchor_rel)


if __name__ == "__main__":
    unittest.main()
