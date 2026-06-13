"""Tests for operator status inbox block."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_operator_status import (
    VERDICT_IDE_BUILD,
    VERDICT_SUPPLY_LOW,
    _build_inbox,
    _format_inbox_block,
    collect_operator_status,
    write_status_report,
)


class TestPpeOperatorStatusInbox(unittest.TestCase):
    def test_build_inbox_ide_build(self) -> None:
        inbox = _build_inbox(
            verdict=VERDICT_IDE_BUILD,
            blocker="product blocked",
            product_slice="MVP1-Test-Product-Slice001",
            active_slice={"sliceId": "MVP1-Test-Product-Slice001", "starterPath": "artifacts/x.md"},
            commands=["ppe_go.cmd"],
            queue_preview=[{"planPath": "docs/SOP/PHASE_PLANS/a.json", "reason": "ready"}],
        )
        self.assertEqual(inbox["owner"], "IDE")
        self.assertEqual(inbox["active_slice_id"], "MVP1-Test-Product-Slice001")
        md = _format_inbox_block(inbox)
        self.assertIn("## Inbox", md)
        self.assertIn("@ppe-build-worker", md)
        self.assertIn("Queue preview", md)
        self.assertIn("a.json", md)

    def test_write_status_includes_inbox(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "docs" / "SOP").mkdir(parents=True)
            (repo / "artifacts" / "orchestrator").mkdir(parents=True)
            manifest = {
                "phasePlanPath": "",
                "sprintSpecPath": "",
                "status": "COMPLETE",
            }
            (repo / "docs/SOP/ACTIVE_PHASE_MANIFEST.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            queue = {"version": 1, "items": [{"planPath": "docs/SOP/PHASE_PLANS/q.json", "status": "READY"}]}
            (repo / "docs/SOP/PHASE_QUEUE.json").write_text(json.dumps(queue), encoding="utf-8")
            backlog = {"version": 1, "items": []}
            (repo / "docs/SOP/PHASE_CHAPTER_BACKLOG.json").write_text(json.dumps(backlog), encoding="utf-8")

            with patch("scripts.ppe_operator_status.run_preflight", return_value={"ok": True, "warnings": []}):
                with patch(
                    "scripts.ppe_operator_status.evaluate_continuous_guards",
                    return_value=type("G", (), {"exit_code": 0, "reason": "", "detail": ""})(),
                ):
                    status = collect_operator_status(repo)
            report = write_status_report(repo, status)
            text = report.read_text(encoding="utf-8")
            self.assertIn("## Inbox", text)
            self.assertIn("Queue preview", text)

    def test_supply_low_owner_steward(self) -> None:
        inbox = _build_inbox(
            verdict=VERDICT_SUPPLY_LOW,
            blocker="no work",
            product_slice=None,
            active_slice=None,
            commands=["backlog"],
            queue_preview=[],
        )
        self.assertEqual(inbox["owner"], "steward")


if __name__ == "__main__":
    unittest.main()
