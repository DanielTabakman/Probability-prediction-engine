"""Tests for Cursor SDK steward (no live Agent.prompt)."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_manifest import save_manifest
from scripts.ppe_roadmap import load_roadmap, save_roadmap
from scripts.ppe_steward_cursor import (
    apply_proposal,
    needs_steward_charter,
    scaffold_chapter_files,
    validate_proposal,
)


class TestPpeStewardCursor(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True)
        (sop / "AGENT_CONTINUITY_BRIEF.md").write_text("# brief\n", encoding="utf-8")
        (sop / "MVP1_FRONTIER.md").write_text("# frontier\n", encoding="utf-8")
        (sop / "PPE_INTEGRATED_STATUS.md").write_text("# status\n", encoding="utf-8")
        save_roadmap(
            self.repo,
            {
                "version": 1,
                "items": [
                    {
                        "planPath": "docs/SOP/PHASE_PLANS/done.json",
                        "status": "done",
                    }
                ],
            },
        )
        (sop / "PHASE_QUEUE.json").write_text(
            json.dumps({"version": 1, "items": []}),
            encoding="utf-8",
        )
        save_manifest(
            self.repo,
            {"phasePlanPath": "", "status": "COMPLETE", "notes": ""},
        )
        os.environ["PPE_AUTO_STEWARD"] = "1"
        os.environ.pop("PPE_STEWARD_ALLOW_PRODUCT", None)

    def tearDown(self) -> None:
        os.environ.pop("PPE_AUTO_STEWARD", None)
        self._tmp.cleanup()

    def test_needs_steward_when_idle(self) -> None:
        need, _ = needs_steward_charter(self.repo)
        self.assertTrue(need)

    def test_apply_proposal_scaffold_and_roadmap(self) -> None:
        proposal = {
            "chapterId": "mvp1_test_charter",
            "chapterTitle": "Test charter",
            "planPath": "docs/SOP/PHASE_PLANS/mvp1_test_charter_relay.json",
            "reason": "unit test",
            "workerMode": "deterministic",
            "scaffold": True,
        }
        self.assertEqual(validate_proposal(self.repo, proposal), [])
        written = scaffold_chapter_files(self.repo, proposal)
        self.assertTrue(written)
        out = apply_proposal(self.repo, proposal, apply=True)
        self.assertTrue(out.get("applied"))
        roadmap = load_roadmap(self.repo)
        last = roadmap["items"][-1]
        self.assertEqual(last["status"], "pending")
        self.assertEqual(last["planPath"], proposal["planPath"])

    def test_rejects_product_worker_without_flag(self) -> None:
        proposal = {
            "chapterId": "x",
            "planPath": "docs/SOP/PHASE_PLANS/x_relay.json",
            "reason": "r",
            "workerMode": "acp",
        }
        errs = validate_proposal(self.repo, proposal)
        self.assertTrue(any("deterministic" in e for e in errs))


if __name__ == "__main__":
    unittest.main()
