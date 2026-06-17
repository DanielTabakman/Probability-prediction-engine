"""Tests for human steward backlog."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_human_backlog import (
    load_backlog,
    open_items,
    phone_snippet_lines,
    render_markdown,
)


class TestPpeHumanBacklog(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True)
        (sop / "HUMAN_STEWARD_BACKLOG.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "items": [
                        {
                            "id": "a",
                            "title": "Topic A",
                            "status": "open",
                            "priority": "high",
                            "summary": "Do A",
                        },
                        {
                            "id": "b",
                            "title": "Topic B",
                            "status": "done",
                            "priority": "low",
                            "summary": "Done",
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_open_items_filters_done(self) -> None:
        items = open_items(self.repo)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["id"], "a")

    def test_phone_snippet_includes_high(self) -> None:
        lines = phone_snippet_lines(self.repo)
        self.assertTrue(any("Topic A" in line for line in lines))
        self.assertTrue(any("Steward topics" in line for line in lines))

    def test_render_markdown_lists_open(self) -> None:
        md = render_markdown(self.repo)
        self.assertIn("Topic A", md)
        self.assertIn("Topic B", md)


if __name__ == "__main__":
    unittest.main()
