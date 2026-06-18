"""Tests for context window closeout gather script."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_context_window_closeout import (
    collect_snapshot,
    render_draft_markdown,
    write_artifacts,
)


class TestPpeContextWindowCloseout(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True)
        (sop / "ACTIVE_PHASE_MANIFEST.json").write_text(
            json.dumps(
                {
                    "status": "READY",
                    "phasePlanPath": "",
                    "sprintSpecPath": "",
                }
            ),
            encoding="utf-8",
        )
        (sop / "PHASE_QUEUE.json").write_text(json.dumps({"items": []}), encoding="utf-8")
        (sop / "PHASE_CHAPTER_BACKLOG.json").write_text(
            json.dumps({"items": [{"chapterId": "x", "status": "blocked"}]}),
            encoding="utf-8",
        )
        (sop / "HUMAN_STEWARD_BACKLOG.json").write_text(
            json.dumps({"version": 1, "items": []}),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_render_draft_contains_agent_fill_and_machine_sections(self) -> None:
        snapshot = collect_snapshot(self.repo)
        md = render_draft_markdown(self.repo, snapshot)
        self.assertIn("## Machine facts", md)
        self.assertIn("<!-- AGENT_FILL", md)
        self.assertIn("## Follow-up triage", md)
        self.assertIn("AGENT CONTINUITY", md)

    def test_write_artifacts_creates_control_plane_files(self) -> None:
        snapshot = collect_snapshot(self.repo)
        json_path, md_path = write_artifacts(self.repo, snapshot)
        self.assertTrue(json_path.is_file())
        self.assertTrue(md_path.is_file())
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertIn("preflight", payload)
        self.assertIn("operator", payload)


if __name__ == "__main__":
    unittest.main()
