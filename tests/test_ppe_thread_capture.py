"""Tests for thread insight capture at context closeout."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_thread_capture import (
    apply_capture,
    format_operator_capture_summary,
    load_capture_file,
    load_insights,
    render_insights_markdown,
)


class TestPpeThreadCapture(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True)
        (sop / "PHASE_CHAPTER_BACKLOG.json").write_text(json.dumps({"items": []}), encoding="utf-8")
        (sop / "HUMAN_STEWARD_BACKLOG.json").write_text(
            json.dumps({"version": 1, "items": []}),
            encoding="utf-8",
        )
        (sop / "TRIGGERED_IDEAS.json").write_text(
            json.dumps({"version": 1, "items": []}),
            encoding="utf-8",
        )
        (sop / "TRIGGERED_IDEAS.md").write_text("# Triggered ideas\n", encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_log_route_rejected(self) -> None:
        capture = {
            "insights": [
                {"kind": "decision", "text": "Keep closeout one-line in chat.", "route": "log"},
            ]
        }
        with self.assertRaises(ValueError):
            apply_capture(self.repo, capture)

    def test_apply_capture_ship_now(self) -> None:
        capture = {
            "insights": [
                {"kind": "note", "text": "Fixed typo in CONTEXT_RULES.", "route": "ship_now"},
            ]
        }
        report = apply_capture(self.repo, capture, closeout_id="c1", head="abc")
        self.assertTrue(report["ok"])
        self.assertEqual(report["counts"]["ship_now"], 1)
        store = load_insights(self.repo)
        self.assertEqual(len(store["items"]), 1)
        self.assertTrue(store["items"][0].get("shipped_in_thread"))
        md = render_insights_markdown(self.repo)
        self.assertIn("Fixed typo", md)

    def test_format_operator_capture_summary_numbered(self) -> None:
        capture = {
            "insights": [
                {"kind": "defer", "route": "triggered", "text": "Wallet revisit"},
                {"kind": "note", "route": "build", "text": "Module map sections"},
            ]
        }
        text = format_operator_capture_summary(capture, {"triggered": 1, "build": 1})
        self.assertIn("2 insight(s) captured", text)
        self.assertIn("1. [defer/triggered] Wallet revisit", text)
        self.assertIn("2. [note/build] Module map sections", text)

    def test_apply_capture_routes_triggered(self) -> None:
        capture = {
            "insights": [
                {
                    "kind": "defer",
                    "text": "Revisit when wallet chapter ships.",
                    "route": "triggered",
                    "title": "Wallet provider revisit",
                    "trigger_chapters": ["msos_wallet_connect_v1"],
                }
            ]
        }
        report = apply_capture(self.repo, capture)
        self.assertTrue(report["ok"])
        self.assertEqual(report["counts"]["triggered"], 1)
        self.assertIn("Revisit when wallet chapter ships", report["operator_summary"])
        triggered = json.loads((self.repo / "docs/SOP/TRIGGERED_IDEAS.json").read_text(encoding="utf-8"))
        self.assertEqual(len(triggered["items"]), 1)

    def test_apply_capture_routes_human(self) -> None:
        capture = {
            "insights": [
                {
                    "kind": "surprise",
                    "text": "Burst defers IDE_BUILD to director.",
                    "route": "human",
                    "title": "Burst IDE_BUILD handoff",
                    "category": "operator",
                }
            ]
        }
        report = apply_capture(self.repo, capture)
        self.assertTrue(report["ok"])
        self.assertEqual(report["counts"]["human"], 1)

    def test_apply_capture_routes_build(self) -> None:
        capture = {
            "insights": [
                {
                    "kind": "note",
                    "text": "Need module map operator sections.",
                    "route": "build",
                    "title": "unused",
                    "chapter_id": "msos_module_map_v1",
                    "reason": "[P2] Module map operator sections",
                }
            ]
        }
        report = apply_capture(self.repo, capture)
        self.assertTrue(report["ok"])
        self.assertEqual(report["counts"]["build"], 1)

    def test_load_capture_file_requires_insights(self) -> None:
        path = self.repo / "bad.json"
        path.write_text(json.dumps({"thread_role": "steward"}), encoding="utf-8")
        with self.assertRaises(ValueError):
            load_capture_file(path)


if __name__ == "__main__":
    unittest.main()
