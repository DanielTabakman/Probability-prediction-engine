"""Tests for BLOCKERS.md generation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.ppe_operator_blockers import (
    BLOCKERS_REL,
    build_blockers_payload,
    format_blockers_md,
    write_blockers_report,
)
from scripts.ppe_operator_status import VERDICT_FIX_PLAN


class TestPpeOperatorBlockers(unittest.TestCase):
    def test_write_blockers_from_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "artifacts" / "orchestrator").mkdir(parents=True)
            status = {
                "as_of": "2026-06-12T00:00:00Z",
                "verdict": VERDICT_FIX_PLAN,
                "blocker": "context escalate",
                "inbox": {
                    "owner": "triage",
                    "agent": "@ppe-triage-worker",
                    "next_command": "ppe_go.cmd",
                },
            }
            out = write_blockers_report(repo, status)
            self.assertTrue(out.is_file())
            text = out.read_text(encoding="utf-8")
            self.assertIn("Operator blockers", text)
            self.assertIn("@ppe-triage-worker", text)

    def test_format_inbox_notify_line(self) -> None:
        from scripts.ppe_operator_status import format_inbox_notify_line

        line = format_inbox_notify_line(
            {
                "owner": "IDE",
                "agent": "@ppe-build-worker",
                "active_slice_id": "Ch-Product-Slice001",
                "next_command": "ppe_go.cmd",
            }
        )
        self.assertIn("owner=IDE", line)
        self.assertIn("Ch-Product-Slice001", line)


if __name__ == "__main__":
    unittest.main()
