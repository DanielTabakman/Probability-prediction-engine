"""Tests for queue chapter selection skip-and-continue."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_auto_select import choose_next_plan_result
from scripts.ppe_queue_selection import (
    anchor_chapter_complete,
    choose_next_selectable,
    selection_blockers,
)


class TestPpeQueueSelection(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        plans = sop / "PHASE_PLANS"
        plans.mkdir(parents=True)

        self.plan_a = "docs/SOP/PHASE_PLANS/chapter_a_relay.json"
        self.plan_b = "docs/SOP/PHASE_PLANS/chapter_b_relay.json"
        self.plan_anchor = "docs/SOP/PHASE_PLANS/anchor_relay.json"

        for rel, cid in (
            (self.plan_anchor, "anchor_ch"),
            (self.plan_a, "chapter_a"),
            (self.plan_b, "chapter_b"),
        ):
            plan = {
                "name": cid,
                "sprintSpecPath": f"docs/SOP/SPRINT_{cid}.md",
                "selectionRecord": f"docs/SOP/SEL_{cid}.md",
                "slices": [{"sliceId": f"{cid}-Closeout", "closeout": {"chapterId": cid}}],
            }
            (self.repo / rel).write_text(json.dumps(plan), encoding="utf-8")
            (sop / f"SPRINT_{cid}.md").write_text(f"# {cid}\n", encoding="utf-8")
            (sop / f"SEL_{cid}.md").write_text(f"# {cid}\n", encoding="utf-8")

        backlog = {
            "items": [
                {
                    "chapterId": "chapter_b",
                    "status": "chartered",
                    "planPath": self.plan_b,
                    "queueAfterPlanPath": self.plan_anchor,
                }
            ]
        }
        (sop / "PHASE_CHAPTER_BACKLOG.json").write_text(json.dumps(backlog, indent=2), encoding="utf-8")
        (sop / "MSOS_P8_VALIDATION_REPORT_V1.md").write_text("**Status:** **COMPLETE**\n", encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _write_queue(self, items: list[dict]) -> None:
        queue = {"version": 1, "items": items}
        (self.repo / "docs" / "SOP" / "PHASE_QUEUE.json").write_text(
            json.dumps(queue, indent=2),
            encoding="utf-8",
        )

    def test_anchor_incomplete_blocks_selection(self) -> None:
        blockers = selection_blockers(self.repo, self.plan_b)
        self.assertTrue(any("anchor" in b for b in blockers))
        self.assertFalse(anchor_chapter_complete(self.repo, self.plan_anchor))

    def test_skips_blocked_ready_and_selects_next(self) -> None:
        self._write_queue(
            [
                {"planPath": self.plan_b, "status": "READY", "reason": "blocked first"},
                {"planPath": self.plan_a, "status": "READY", "reason": "ok second"},
            ]
        )
        result = choose_next_selectable(self.repo, load_items(self.repo), status="READY")
        self.assertEqual(result.plan_path, self.plan_a)
        self.assertEqual(len(result.skipped), 1)
        self.assertEqual(result.skipped[0].chapter_id, "chapter_b")

    def test_auto_select_result_matches(self) -> None:
        self._write_queue(
            [
                {"planPath": self.plan_b, "status": "READY"},
                {"planPath": self.plan_a, "status": "READY"},
            ]
        )
        result = choose_next_plan_result(self.repo)
        self.assertEqual(result.plan_path, self.plan_a)

    @patch("scripts.ppe_progress_notify.send_ntfy", return_value=True)
    @patch("scripts.ppe_progress_notify.ntfy_configured", return_value=True)
    @patch("scripts.ppe_progress_notify.notify_enabled", return_value=True)
    def test_skip_notify_on_blocked_first_ready(
        self, _ne: object, _nc: object, send: object
    ) -> None:
        from scripts.ppe_auto_select import maybe_notify_selection_skips

        self._write_queue(
            [
                {"planPath": self.plan_b, "status": "READY"},
                {"planPath": self.plan_a, "status": "READY"},
            ]
        )
        result = choose_next_plan_result(self.repo)
        maybe_notify_selection_skips(
            self.repo,
            skipped=result.skipped,
            selected_plan=result.plan_path,
            apply=True,
        )
        self.assertTrue(send.called)
        title = send.call_args[0][0]
        self.assertIn("skipped", title.lower())


def load_items(repo: Path) -> list:
    queue = json.loads((repo / "docs" / "SOP" / "PHASE_QUEUE.json").read_text(encoding="utf-8"))
    return queue["items"]


if __name__ == "__main__":
    unittest.main()
