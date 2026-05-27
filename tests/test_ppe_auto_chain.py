"""Tests for phase auto-resume and slice remaining logic."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_auto_chain import (
    chapter_is_complete,
    continued_slice_ids,
    remaining_slice_ids,
    summary_matches_plan,
)


class TestPpeAutoChain(unittest.TestCase):
    def test_remaining_slices_after_blocked(self) -> None:
        summary = {
            "planPath": "docs/SOP/PHASE_PLANS/plan.json",
            "results": [
                {"kind": "ran", "sliceId": "A-001", "run": {"status": "CONTINUE"}},
                {"kind": "ran", "sliceId": "A-002", "run": {"status": "BLOCKED"}},
            ],
        }
        all_ids = ["A-001", "A-002", "A-003", "A-004"]
        done = continued_slice_ids(summary)
        remaining = [s for s in all_ids if s not in done]
        self.assertEqual(remaining, ["A-002", "A-003", "A-004"])

    def test_chapter_complete_when_closeout_continue(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        repo = Path(self._tmp.name)
        sop = repo / "docs" / "SOP" / "PHASE_PLANS"
        sop.mkdir(parents=True)
        plan = {
            "slices": [
                {"sliceId": "X-001"},
                {
                    "sliceId": "X-Closeout",
                    "closeout": {"chapterId": "x"},
                },
            ]
        }
        (sop / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
        manifest = {
            "phasePlanPath": "",
            "status": "COMPLETE",
        }
        (repo / "docs" / "SOP").mkdir(parents=True, exist_ok=True)
        (repo / "docs" / "SOP" / "ACTIVE_PHASE_MANIFEST.json").write_text(
            json.dumps(manifest),
            encoding="utf-8",
        )
        orch = repo / "artifacts" / "orchestrator"
        orch.mkdir(parents=True)
        (orch / "steward_phase_summary.json").write_text(
            json.dumps(
                {
                    "planPath": "docs/SOP/PHASE_PLANS/plan.json",
                    "results": [
                        {"kind": "ran", "sliceId": "X-001", "run": {"status": "CONTINUE"}},
                        {"kind": "ran", "sliceId": "X-Closeout", "run": {"status": "CONTINUE"}},
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.assertTrue(chapter_is_complete(repo, "docs/SOP/PHASE_PLANS/plan.json"))
        self._tmp.cleanup()

    def test_summary_matches_plan(self) -> None:
        self.assertTrue(
            summary_matches_plan(
                {"planPath": "docs/SOP/PHASE_PLANS/a.json"},
                "docs\\SOP\\PHASE_PLANS\\a.json",
            )
        )


if __name__ == "__main__":
    unittest.main()
