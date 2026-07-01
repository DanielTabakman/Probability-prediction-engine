"""Tests for ppe_feedback_steward_hook.py."""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from scripts.ppe_feedback_steward_hook import BACKLOG_ID, run_hook


class TestPpeFeedbackStewardHook(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _write_feedback(self, rows: list[dict]) -> None:
        path = self.repo / "data" / "ppe_web_feedback.jsonl"
        path.parent.mkdir(parents=True)
        path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    def test_hook_triggers_on_low_usefulness(self) -> None:
        self._write_feedback(
            [
                {"usefulness": 2, "repeat_use_intent": 2, "created_at_utc": datetime.now(timezone.utc).isoformat()},
                {"usefulness": 1, "repeat_use_intent": 2, "created_at_utc": datetime.now(timezone.utc).isoformat()},
            ]
        )
        backlog_path = self.repo / "docs" / "SOP" / "HUMAN_STEWARD_BACKLOG.json"
        backlog_path.parent.mkdir(parents=True)
        backlog_path.write_text(json.dumps({"items": []}) + "\n", encoding="utf-8")

        with mock.patch("scripts.ppe_feedback_steward_hook.resolve_feedback_path", return_value=self.repo / "data" / "ppe_web_feedback.jsonl"):
            with mock.patch("scripts.ppe_human_backlog.backlog_path", return_value=backlog_path):
                out = run_hook(self.repo, days=7, dry_run=False)
        self.assertTrue(out["triggered"])
        backlog = json.loads(backlog_path.read_text(encoding="utf-8"))
        ids = [i.get("id") for i in backlog.get("items") or []]
        self.assertIn(BACKLOG_ID, ids)

    def test_hook_skips_when_usefulness_ok(self) -> None:
        self._write_feedback(
            [
                {"usefulness": 5, "repeat_use_intent": 5, "created_at_utc": datetime.now(timezone.utc).isoformat()},
                {"usefulness": 4, "repeat_use_intent": 4, "created_at_utc": datetime.now(timezone.utc).isoformat()},
            ]
        )
        with mock.patch("scripts.ppe_feedback_steward_hook.resolve_feedback_path", return_value=self.repo / "data" / "ppe_web_feedback.jsonl"):
            out = run_hook(self.repo, days=7, dry_run=True)
        self.assertFalse(out["triggered"])


if __name__ == "__main__":
    unittest.main()
