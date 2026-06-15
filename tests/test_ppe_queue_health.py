"""Tests for PHASE_QUEUE audit/repair."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_auto_select import run_auto_select
from scripts.ppe_queue import load_queue
from scripts.ppe_queue_health import (
    audit_backlog,
    audit_queue,
    audit_roadmap,
    chapter_marked_complete_in_repo,
    repair_backlog,
    repair_queue,
    repair_roadmap,
)


class TestPpeQueueHealth(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        plans = sop / "PHASE_PLANS"
        plans.mkdir(parents=True)
        plan = {
            "name": "chapter_done",
            "sprintSpecPath": "docs/SOP/SPRINT_X.md",
            "slices": [
                {
                    "sliceId": "X-Closeout",
                    "closeout": {
                        "evidenceDoc": "docs/SOP/CHAPTER_X_EVIDENCE_STATUS.md",
                        "chapterStatus": "COMPLETE",
                    },
                }
            ],
        }
        (plans / "chapter_done.json").write_text(json.dumps(plan), encoding="utf-8")
        (sop / "SPRINT_X.md").write_text("# X\n", encoding="utf-8")
        (sop / "CHAPTER_X_EVIDENCE_STATUS.md").write_text(
            "# Evidence\n\n**Status:** **COMPLETE** 2026-05-28\n",
            encoding="utf-8",
        )
        queue = {
            "version": 1,
            "items": [
                {
                    "planPath": "docs/SOP/PHASE_PLANS/chapter_done.json",
                    "status": "DONE",
                },
                {
                    "planPath": "docs/SOP/PHASE_PLANS/chapter_done.json",
                    "status": "READY",
                    "reason": "erroneous re-queue",
                },
            ],
        }
        (sop / "PHASE_QUEUE.json").write_text(json.dumps(queue, indent=2), encoding="utf-8")
        manifest = {
            "phasePlanPath": "",
            "status": "COMPLETE",
            "notes": "",
        }
        (sop / "ACTIVE_PHASE_MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_audit_detects_ready_after_done(self) -> None:
        issues, _ = audit_queue(self.repo)
        codes = {i["code"] for i in issues}
        self.assertIn("DUPLICATE_PLAN", codes)
        self.assertIn("READY_AFTER_DONE", codes)

    def test_repair_marks_duplicate_ready_done(self) -> None:
        fixes, remaining = repair_queue(self.repo, apply=True)
        self.assertTrue(fixes)
        self.assertEqual(remaining, [])
        queue = load_queue(self.repo)
        self.assertEqual(queue["items"][0]["status"], "DONE")
        self.assertEqual(queue["items"][1]["status"], "DONE")

    def test_auto_select_skips_repaired_stale_ready(self) -> None:
        repair_queue(self.repo, apply=True)
        rc = run_auto_select(self.repo, apply=True, select_only=False, mark_done=False, force=False)
        self.assertEqual(rc, 0)
        queue = load_queue(self.repo)
        ready = [i for i in queue["items"] if i.get("status") == "READY"]
        self.assertEqual(ready, [])

    def test_audit_backlog_detects_active_complete_chapter(self) -> None:
        backlog = {
            "version": 1,
            "items": [
                {
                    "chapterId": "early_ship",
                    "status": "blocked",
                    "planPath": "docs/SOP/PHASE_PLANS/chapter_done.json",
                }
            ],
        }
        (self.repo / "docs" / "SOP" / "PHASE_CHAPTER_BACKLOG.json").write_text(
            json.dumps(backlog, indent=2),
            encoding="utf-8",
        )
        issues = audit_backlog(self.repo)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["code"], "BACKLOG_ACTIVE_BUT_EVIDENCE_COMPLETE")

    def test_repair_backlog_marks_done(self) -> None:
        backlog = {
            "version": 1,
            "items": [
                {
                    "chapterId": "early_ship",
                    "status": "blocked",
                    "planPath": "docs/SOP/PHASE_PLANS/chapter_done.json",
                }
            ],
        }
        (self.repo / "docs" / "SOP" / "PHASE_CHAPTER_BACKLOG.json").write_text(
            json.dumps(backlog, indent=2),
            encoding="utf-8",
        )
        fixes, remaining = repair_backlog(self.repo, apply=True)
        self.assertTrue(fixes)
        self.assertEqual(remaining, [])
        backlog_data = json.loads(
            (self.repo / "docs" / "SOP" / "PHASE_CHAPTER_BACKLOG.json").read_text(encoding="utf-8")
        )
        self.assertEqual(backlog_data["items"][0]["status"], "done")

    def test_chapter_marked_complete_chapter_status_section(self) -> None:
        evidence = self.repo / "docs" / "SOP" / "CHAPTER_STATUS_EVIDENCE.md"
        evidence.write_text(
            "# Evidence\n\n## Chapter status\n\n**COMPLETE** (implementation)\n",
            encoding="utf-8",
        )
        plan = {
            "name": "status_section",
            "slices": [
                {
                    "sliceId": "Y-Closeout",
                    "closeout": {"evidenceDoc": "docs/SOP/CHAPTER_STATUS_EVIDENCE.md"},
                }
            ],
        }
        plan_path = self.repo / "docs" / "SOP" / "PHASE_PLANS" / "status_section.json"
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        self.assertTrue(
            chapter_marked_complete_in_repo(self.repo, "docs/SOP/PHASE_PLANS/status_section.json")
        )

    def test_audit_roadmap_detects_backlog_vocabulary(self) -> None:
        roadmap = {
            "version": 1,
            "items": [
                {
                    "planPath": "docs/SOP/PHASE_PLANS/chapter_done.json",
                    "status": "chartered",
                },
                {
                    "planPath": "docs/SOP/PHASE_PLANS/other.json",
                    "status": "blocked",
                },
            ],
        }
        (self.repo / "docs" / "SOP" / "PHASE_SELECTION_ROADMAP.json").write_text(
            json.dumps(roadmap, indent=2),
            encoding="utf-8",
        )
        issues = audit_roadmap(self.repo)
        self.assertEqual(len(issues), 2)
        self.assertEqual(issues[0]["code"], "ROADMAP_INVALID_STATUS")

    def test_repair_roadmap_normalizes_chartered_and_blocked(self) -> None:
        other_plan = {
            "name": "other",
            "slices": [{"sliceId": "O-Closeout", "closeout": {"chapterId": "other"}}],
        }
        (self.repo / "docs" / "SOP" / "PHASE_PLANS" / "other.json").write_text(
            json.dumps(other_plan),
            encoding="utf-8",
        )
        roadmap = {
            "version": 1,
            "items": [
                {
                    "planPath": "docs/SOP/PHASE_PLANS/chapter_done.json",
                    "status": "chartered",
                },
                {
                    "planPath": "docs/SOP/PHASE_PLANS/other.json",
                    "status": "blocked",
                },
            ],
        }
        (self.repo / "docs" / "SOP" / "PHASE_SELECTION_ROADMAP.json").write_text(
            json.dumps(roadmap, indent=2),
            encoding="utf-8",
        )
        fixes, remaining = repair_roadmap(self.repo, apply=True)
        self.assertEqual(len(fixes), 2)
        self.assertEqual(remaining, [])
        roadmap_data = json.loads(
            (self.repo / "docs" / "SOP" / "PHASE_SELECTION_ROADMAP.json").read_text(encoding="utf-8")
        )
        self.assertEqual(roadmap_data["items"][0]["status"], "done")
        self.assertEqual(roadmap_data["items"][1]["status"], "skipped")

    def test_repair_roadmap_only_one_pending_from_chartered(self) -> None:
        for slug in ("other_a", "other_b"):
            plan = {
                "name": slug,
                "slices": [{"sliceId": "O-Closeout", "closeout": {"chapterId": slug}}],
            }
            (self.repo / "docs" / "SOP" / "PHASE_PLANS" / f"{slug}.json").write_text(
                json.dumps(plan),
                encoding="utf-8",
            )
        roadmap = {
            "version": 1,
            "items": [
                {"planPath": "docs/SOP/PHASE_PLANS/other_a.json", "status": "chartered"},
                {"planPath": "docs/SOP/PHASE_PLANS/other_b.json", "status": "chartered"},
            ],
        }
        (self.repo / "docs" / "SOP" / "PHASE_SELECTION_ROADMAP.json").write_text(
            json.dumps(roadmap, indent=2),
            encoding="utf-8",
        )
        repair_roadmap(self.repo, apply=True)
        roadmap_data = json.loads(
            (self.repo / "docs" / "SOP" / "PHASE_SELECTION_ROADMAP.json").read_text(encoding="utf-8")
        )
        statuses = [row["status"] for row in roadmap_data["items"]]
        self.assertEqual(statuses.count("pending"), 1)
        self.assertEqual(statuses.count("skipped"), 1)


if __name__ == "__main__":
    unittest.main()
