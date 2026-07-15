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

    def test_chapter_not_complete_when_slice_rows_pending(self) -> None:
        evidence = self.repo / "docs" / "SOP" / "CHAPTER_PENDING_EVIDENCE.md"
        evidence.write_text(
            "# Evidence\n\n**Status:** **COMPLETE** 2026-06-15\n\n"
            "| Slice | Status |\n|-------|--------|\n"
            "| X-Slice001 | PENDING |\n",
            encoding="utf-8",
        )
        plan = {
            "name": "pending_slices",
            "slices": [
                {
                    "sliceId": "X-Closeout",
                    "closeout": {"evidenceDoc": "docs/SOP/CHAPTER_PENDING_EVIDENCE.md"},
                }
            ],
        }
        plan_path = self.repo / "docs" / "SOP" / "PHASE_PLANS" / "pending_slices.json"
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        self.assertFalse(
            chapter_marked_complete_in_repo(self.repo, "docs/SOP/PHASE_PLANS/pending_slices.json")
        )

    def test_audit_detects_ready_with_terminal_backlog_even_without_done_queue_row(self) -> None:
        plan = {
            "name": "terminal_backlog_only",
            "slices": [
                {
                    "sliceId": "T-Closeout",
                    "closeout": {"evidenceDoc": "docs/SOP/TERMINAL_BACKLOG_ONLY_EVIDENCE.md"},
                }
            ],
        }
        (self.repo / "docs" / "SOP" / "PHASE_PLANS" / "terminal_backlog_only.json").write_text(
            json.dumps(plan),
            encoding="utf-8",
        )
        (self.repo / "docs" / "SOP" / "TERMINAL_BACKLOG_ONLY_EVIDENCE.md").write_text(
            "# Evidence\n\n**Status:** **PENDING**\n",
            encoding="utf-8",
        )
        backlog = {
            "version": 1,
            "items": [
                {
                    "chapterId": "terminal_backlog_only",
                    "status": "done",
                    "planPath": "docs/SOP/PHASE_PLANS/terminal_backlog_only.json",
                }
            ],
        }
        (self.repo / "docs" / "SOP" / "PHASE_CHAPTER_BACKLOG.json").write_text(
            json.dumps(backlog, indent=2),
            encoding="utf-8",
        )
        queue = {
            "version": 1,
            "items": [
                {
                    "planPath": "docs/SOP/PHASE_PLANS/terminal_backlog_only.json",
                    "status": "READY",
                    "reason": "stale frontier row",
                }
            ],
        }
        (self.repo / "docs" / "SOP" / "PHASE_QUEUE.json").write_text(
            json.dumps(queue, indent=2),
            encoding="utf-8",
        )
        issues, _ = audit_queue(self.repo)
        self.assertIn("READY_WITH_TERMINAL_BACKLOG", {issue["code"] for issue in issues})

    def _write_archived_complete_chapter(self) -> str:
        plan_rel = "docs/SOP/PHASE_PLANS/complete_requeue.json"
        evidence_rel = "docs/SOP/COMPLETE_REQUEUE_EVIDENCE.md"
        plan = {
            "name": "complete_requeue",
            "slices": [
                {
                    "sliceId": "Complete-Requeue-Closeout",
                    "closeout": {"evidenceDoc": evidence_rel},
                }
            ],
        }
        (self.repo / plan_rel).write_text(json.dumps(plan), encoding="utf-8")
        (self.repo / evidence_rel).write_text(
            "---\narchived: true\nclosed: 2026-07-15\n---\n\n"
            "# Complete requeue evidence\n\n"
            "**Status:** **COMPLETE** 2026-07-15\n\n"
            "| Slice | Status |\n|-------|--------|\n"
            "| Complete-Requeue-Closeout | CLOSED |\n",
            encoding="utf-8",
        )
        return plan_rel

    def test_explicit_requeue_can_reopen_archived_complete_terminal_frontier(self) -> None:
        plan_rel = self._write_archived_complete_chapter()
        backlog = {
            "version": 1,
            "items": [
                {
                    "chapterId": "complete_requeue",
                    "status": "done",
                    "planPath": plan_rel,
                }
            ],
        }
        (self.repo / "docs" / "SOP" / "PHASE_CHAPTER_BACKLOG.json").write_text(
            json.dumps(backlog, indent=2),
            encoding="utf-8",
        )
        queue = {
            "version": 1,
            "items": [
                {
                    "planPath": plan_rel,
                    "status": "READY",
                    "explicitRequeue": True,
                    "requeueReason": "new founder-approved follow-up slice",
                }
            ],
        }
        (self.repo / "docs" / "SOP" / "PHASE_QUEUE.json").write_text(
            json.dumps(queue, indent=2),
            encoding="utf-8",
        )
        issues, _ = audit_queue(self.repo)
        codes = {issue["code"] for issue in issues}
        self.assertNotIn("READY_BUT_CHAPTER_COMPLETE", codes)
        self.assertNotIn("READY_WITH_TERMINAL_BACKLOG", codes)
        self.assertNotIn("READY_WITH_ARCHIVED_COMPLETE_EVIDENCE", codes)

    def test_malformed_explicit_requeue_still_reports_terminal_history(self) -> None:
        plan_rel = self._write_archived_complete_chapter()
        (self.repo / "docs" / "SOP" / "PHASE_CHAPTER_BACKLOG.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "items": [
                        {
                            "chapterId": "complete_requeue",
                            "status": "done",
                            "planPath": plan_rel,
                        }
                    ],
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        malformed_requeues = [
            {"explicitRequeue": True},
            {"explicitRequeue": True, "requeueReason": ""},
            {"explicitRequeue": True, "requeueReason": "   "},
        ]
        for malformed in malformed_requeues:
            queue_item = {
                "planPath": plan_rel,
                "status": "READY",
                "reason": "malformed explicit requeue",
                **malformed,
            }
            (self.repo / "docs" / "SOP" / "PHASE_QUEUE.json").write_text(
                json.dumps({"version": 1, "items": [queue_item]}, indent=2),
                encoding="utf-8",
            )
            issues, _ = audit_queue(self.repo)
            codes = {issue["code"] for issue in issues}
            self.assertIn("READY_BUT_CHAPTER_COMPLETE", codes)

    def test_audit_detects_archived_complete_evidence_with_pending_slice_rows(self) -> None:
        evidence = self.repo / "docs" / "SOP" / "CHAPTER_PENDING_EVIDENCE.md"
        evidence.write_text(
            "---\narchived: true\n---\n\n"
            "# Evidence\n\n**Status:** **WITNESS COMPLETE**\n\n"
            "| Slice | Status |\n|-------|--------|\n"
            "| X-Slice001 | PENDING |\n",
            encoding="utf-8",
        )
        plan = {
            "name": "pending_slices",
            "slices": [
                {
                    "sliceId": "X-Closeout",
                    "closeout": {"evidenceDoc": "docs/SOP/CHAPTER_PENDING_EVIDENCE.md"},
                }
            ],
        }
        (self.repo / "docs" / "SOP" / "PHASE_PLANS" / "pending_slices.json").write_text(
            json.dumps(plan),
            encoding="utf-8",
        )
        queue = {
            "version": 1,
            "items": [
                {
                    "planPath": "docs/SOP/PHASE_PLANS/pending_slices.json",
                    "status": "READY",
                    "reason": "stale archived evidence row",
                }
            ],
        }
        (self.repo / "docs" / "SOP" / "PHASE_QUEUE.json").write_text(
            json.dumps(queue, indent=2),
            encoding="utf-8",
        )
        issues, _ = audit_queue(self.repo)
        self.assertIn("READY_WITH_ARCHIVED_COMPLETE_EVIDENCE", {issue["code"] for issue in issues})

    def test_recurring_chapter_never_marked_permanently_complete(self) -> None:
        evidence = self.repo / "docs" / "SOP" / "RECURRING_EVIDENCE.md"
        evidence.write_text(
            "# Evidence\n\n**Status:** **COMPLETE** 2026-06-30\n",
            encoding="utf-8",
        )
        plan = {
            "name": "recurring",
            "slices": [
                {
                    "sliceId": "R-Closeout",
                    "closeout": {
                        "recurring": True,
                        "evidenceDoc": "docs/SOP/RECURRING_EVIDENCE.md",
                    },
                }
            ],
        }
        plan_path = self.repo / "docs" / "SOP" / "PHASE_PLANS" / "recurring.json"
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        self.assertFalse(
            chapter_marked_complete_in_repo(self.repo, "docs/SOP/PHASE_PLANS/recurring.json")
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


if __name__ == "__main__":
    unittest.main()
