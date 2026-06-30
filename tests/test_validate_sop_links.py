"""Tests for validate_sop_links."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validate_sop_links import validate_sop_links


class TestValidateSopLinks(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True, exist_ok=True)
        (sop / "ACTIVE_PROGRAM_V1.md").write_text("# active\n", encoding="utf-8")
        (sop / "TOPIC_SOP_V1.md").write_text("# topic\n", encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _index(self) -> dict:
        return {
            "active_chapter_count": 1,
            "archived_chapter_count": 1,
            "active_chapters": [
                {
                    "chapter_id": "active_chapter_v1",
                    "archived": False,
                    "program_doc": "docs/SOP/ACTIVE_PROGRAM_V1.md",
                    "load_always": ["docs/SOP/ACTIVE_PROGRAM_V1.md"],
                    "load_for_build": [],
                    "load_on_demand": [],
                }
            ],
            "chapters": [
                {
                    "chapter_id": "archived_chapter_v1",
                    "archived": True,
                    "program_doc": "docs/SOP/MISSING_ARCHIVED_ONLY_V1.md",
                    "load_always": ["docs/SOP/MISSING_ARCHIVED_ONLY_V1.md"],
                }
            ],
        }

    def test_active_valid_archived_skipped(self) -> None:
        report = validate_sop_links(
            self.repo,
            index=self._index(),
            module_program_docs={"active_mod": "docs/SOP/ACTIVE_PROGRAM_V1.md"},
            topic_routes=[
                {
                    "id": "test_topic",
                    "sop": "docs/SOP/TOPIC_SOP_V1.md",
                    "load_always": ["docs/SOP/TOPIC_SOP_V1.md"],
                }
            ],
        )
        self.assertTrue(report["ok"])

    def test_active_missing_fails(self) -> None:
        index = self._index()
        index["active_chapters"][0]["load_always"] = ["docs/SOP/DOES_NOT_EXIST.md"]
        report = validate_sop_links(
            self.repo,
            index=index,
            module_program_docs={"active_mod": "docs/SOP/ACTIVE_PROGRAM_V1.md"},
            topic_routes=[],
        )
        self.assertFalse(report["ok"])


if __name__ == "__main__":
    unittest.main()
