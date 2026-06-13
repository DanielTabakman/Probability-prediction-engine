"""Tests for backlog-priority ordering in ppe_auto_select."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_auto_select import choose_next_plan


class TestPpeAutoSelectPriority(unittest.TestCase):
    def test_high_priority_ready_before_low_in_queue_file_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            sop = repo / "docs" / "SOP"
            plans = sop / "PHASE_PLANS"
            plans.mkdir(parents=True)

            def _plan(name: str, sid: str) -> None:
                p = {
                    "name": name,
                    "sprintSpecPath": f"docs/SOP/SPRINT_{name}.md",
                    "selectionRecord": f"docs/SOP/SEL_{name}.md",
                    "slices": [{"sliceId": sid, "closeout": {"chapterId": name}}],
                }
                (plans / f"{name}.json").write_text(json.dumps(p), encoding="utf-8")
                (sop / f"SPRINT_{name}.md").write_text("# x\n", encoding="utf-8")
                (sop / f"SEL_{name}.md").write_text("# x\n", encoding="utf-8")

            _plan("low_chapter", "Low-Closeout")
            _plan("high_chapter", "High-Closeout")

            queue = {
                "version": 1,
                "items": [
                    {
                        "planPath": "docs/SOP/PHASE_PLANS/low_chapter.json",
                        "status": "READY",
                        "reason": "low first in file",
                    },
                    {
                        "planPath": "docs/SOP/PHASE_PLANS/high_chapter.json",
                        "status": "READY",
                        "reason": "high second in file",
                    },
                ],
            }
            (sop / "PHASE_QUEUE.json").write_text(json.dumps(queue), encoding="utf-8")
            backlog = {
                "version": 1,
                "items": [
                    {
                        "chapterId": "low_chapter",
                        "status": "chartered",
                        "priority": "low",
                        "planPath": "docs/SOP/PHASE_PLANS/low_chapter.json",
                    },
                    {
                        "chapterId": "high_chapter",
                        "status": "chartered",
                        "priority": "high",
                        "planPath": "docs/SOP/PHASE_PLANS/high_chapter.json",
                    },
                ],
            }
            (sop / "PHASE_CHAPTER_BACKLOG.json").write_text(json.dumps(backlog), encoding="utf-8")
            (sop / "MSOS_P8_VALIDATION_REPORT_V1.md").write_text("**Status:** **COMPLETE**\n", encoding="utf-8")

            plan, reason = choose_next_plan(repo)
            self.assertEqual(plan, "docs/SOP/PHASE_PLANS/high_chapter.json")
            self.assertIn("high", reason.lower())


if __name__ == "__main__":
    unittest.main()
