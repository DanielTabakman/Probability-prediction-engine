"""Tests for PHASE_CHAPTER_BACKLOG propagation."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_manifest import save_manifest
from scripts.ppe_roadmap import load_roadmap
from scripts.ppe_propagate_queue import (
    load_backlog,
    maybe_propagate_queue,
    promote_first_blocked_with_plan,
    propagate_from_backlog,
    save_backlog,
    sync_backlog_from_roadmap,
)


class TestPpePropagateQueue(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        plans = sop / "PHASE_PLANS"
        plans.mkdir(parents=True)
        plan = {
            "name": "next_chapter",
            "sprintSpecPath": "docs/SOP/SPRINT_NEXT.md",
            "selectionRecord": "docs/SOP/SEL_NEXT.md",
            "slices": [{"sliceId": "X-Closeout", "closeout": {"chapterId": "x"}}],
        }
        (plans / "next_relay.json").write_text(json.dumps(plan), encoding="utf-8")
        (sop / "SPRINT_NEXT.md").write_text("# n\n", encoding="utf-8")
        (sop / "SEL_NEXT.md").write_text("# s\n", encoding="utf-8")
        (sop / "PHASE_SELECTION_ROADMAP.json").write_text(
            json.dumps({"version": 1, "items": []}),
            encoding="utf-8",
        )
        (sop / "PHASE_QUEUE.json").write_text(json.dumps({"version": 1, "items": []}), encoding="utf-8")
        (sop / "PHASE_CHAPTER_BACKLOG.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "items": [
                        {
                            "chapterId": "next_chapter",
                            "status": "queued",
                            "planPath": "docs/SOP/PHASE_PLANS/next_relay.json",
                            "reason": "test",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        save_manifest(self.repo, {"phasePlanPath": "", "status": "COMPLETE", "notes": ""})
        os.environ["PPE_AUTO_PROPAGATE_QUEUE"] = "1"

    def tearDown(self) -> None:
        os.environ.pop("PPE_AUTO_PROPAGATE_QUEUE", None)
        self._tmp.cleanup()

    def test_propagate_appends_pending(self) -> None:
        out = propagate_from_backlog(self.repo, apply=True)
        self.assertTrue(out.get("propagated"))
        roadmap = load_roadmap(self.repo)
        self.assertEqual(roadmap["items"][-1]["status"], "pending")
        backlog = load_backlog(self.repo)
        self.assertEqual(backlog["items"][0]["status"], "chartered")

    def test_sync_backlog_done_from_queue(self) -> None:
        from scripts.ppe_queue import save_queue

        save_queue(
            self.repo,
            {
                "version": 1,
                "items": [
                    {
                        "planPath": "docs/SOP/PHASE_PLANS/next_relay.json",
                        "status": "DONE",
                        "reason": "closed",
                    }
                ],
            },
        )
        backlog = load_backlog(self.repo)
        backlog["items"][0]["status"] = "chartered"
        save_backlog(self.repo, backlog)
        from scripts.ppe_propagate_queue import sync_backlog_from_queue

        changes = sync_backlog_from_queue(self.repo, apply=True)
        self.assertTrue(changes)
        backlog = load_backlog(self.repo)
        self.assertEqual(backlog["items"][0]["status"], "done")

    def test_sync_backlog_done_from_roadmap(self) -> None:
        roadmap = load_roadmap(self.repo)
        roadmap["items"] = [
            {
                "planPath": "docs/SOP/PHASE_PLANS/next_relay.json",
                "status": "done",
            }
        ]
        from scripts.ppe_roadmap import save_roadmap

        save_roadmap(self.repo, roadmap)
        backlog = load_backlog(self.repo)
        backlog["items"][0]["status"] = "chartered"
        from scripts.ppe_propagate_queue import save_backlog

        save_backlog(self.repo, backlog)
        changes = sync_backlog_from_roadmap(self.repo, apply=True)
        self.assertTrue(changes)
        backlog = load_backlog(self.repo)
        self.assertEqual(backlog["items"][0]["status"], "done")

    def test_maybe_propagate_idle(self) -> None:
        out = maybe_propagate_queue(self.repo, apply=True)
        self.assertTrue(out.get("propagated"))

    def test_promote_blocked_when_prior_done(self) -> None:
        plans = self.repo / "docs" / "SOP" / "PHASE_PLANS"
        blocked_plan = {
            "name": "blocked_chapter",
            "sprintSpecPath": "docs/SOP/SPRINT_BLOCKED.md",
            "selectionRecord": "docs/SOP/SEL_BLOCKED.md",
            "slices": [{"sliceId": "B-Closeout", "closeout": {"chapterId": "b"}}],
        }
        (plans / "blocked_relay.json").write_text(json.dumps(blocked_plan), encoding="utf-8")
        (self.repo / "docs" / "SOP" / "SPRINT_BLOCKED.md").write_text("# b\n", encoding="utf-8")
        (self.repo / "docs" / "SOP" / "SEL_BLOCKED.md").write_text("# s\n", encoding="utf-8")
        backlog = load_backlog(self.repo)
        backlog["items"] = [
            {
                "chapterId": "done_chapter",
                "status": "done",
                "planPath": "docs/SOP/PHASE_PLANS/next_relay.json",
            },
            {
                "chapterId": "blocked_chapter",
                "status": "blocked",
                "planPath": "docs/SOP/PHASE_PLANS/blocked_relay.json",
            },
        ]
        save_backlog(self.repo, backlog)
        out = promote_first_blocked_with_plan(self.repo, apply=True)
        self.assertTrue(out.get("promoted"))
        backlog = load_backlog(self.repo)
        self.assertEqual(backlog["items"][1]["status"], "queued")

    def test_promote_skips_when_prior_not_done(self) -> None:
        plans = self.repo / "docs" / "SOP" / "PHASE_PLANS"
        (plans / "blocked_relay.json").write_text(
            json.dumps(
                {
                    "name": "b",
                    "sprintSpecPath": "docs/SOP/SPRINT_BLOCKED.md",
                    "selectionRecord": "docs/SOP/SEL_BLOCKED.md",
                    "slices": [{"sliceId": "B-Closeout", "closeout": {"chapterId": "b"}}],
                }
            ),
            encoding="utf-8",
        )
        backlog = load_backlog(self.repo)
        backlog["items"] = [
            {"chapterId": "active", "status": "chartered", "planPath": "docs/SOP/PHASE_PLANS/next_relay.json"},
            {
                "chapterId": "blocked_chapter",
                "status": "blocked",
                "planPath": "docs/SOP/PHASE_PLANS/blocked_relay.json",
            },
        ]
        save_backlog(self.repo, backlog)
        out = promote_first_blocked_with_plan(self.repo, apply=True)
        self.assertFalse(out.get("promoted"))
        self.assertIn("prior", str(out.get("reason", "")).lower())


if __name__ == "__main__":
    unittest.main()
