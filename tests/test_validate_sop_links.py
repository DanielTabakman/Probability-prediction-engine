"""Tests for validate_sop_links."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validate_sop_links import validate_sop_links
from scripts.sop_discovery_core import (
    EXTRA_PROGRAM_DOCS,
    build_program_doc_index,
    validate_program_doc_footers,
)


class TestValidateSopLinks(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True, exist_ok=True)
        (sop / "ACTIVE_PROGRAM_V1.md").write_text(
            "# active\n\n## Agent load bundle\n\nResolve: `python scripts/resolve_sop.py --module active_mod --json`\n",
            encoding="utf-8",
        )
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


class TestSopDocHygieneTier10(unittest.TestCase):
    def test_program_index_includes_msos_website(self) -> None:
        data = build_program_doc_index(Path(__file__).resolve().parents[1])
        docs = {row["program_doc"] for row in data["programs"]}
        for extra in EXTRA_PROGRAM_DOCS:
            self.assertIn(extra, docs)

    def test_validate_program_doc_footers_real_repo(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        errors = validate_program_doc_footers(repo)
        self.assertEqual(errors, [], msg="\n".join(errors))

    def test_missing_footer_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            sop = repo / "docs" / "SOP"
            sop.mkdir(parents=True)
            (sop / "BAD_PROGRAM_V1.md").write_text("# no footer\n", encoding="utf-8")
            errors = validate_program_doc_footers(repo)
            self.assertTrue(any("BAD_PROGRAM_V1" in err for err in errors))


if __name__ == "__main__":
    unittest.main()
