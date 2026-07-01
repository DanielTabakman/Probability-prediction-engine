"""Closeout doc path validation and evidence archived front matter."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.relay.apply_control_closeout import CloseoutSpec, apply_control_closeout
from scripts.sop_discovery_core import (
    stamp_evidence_archived_frontmatter,
    validate_closeout_spec_docs,
)


class TestCloseoutDocValidation(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _spec(self, *, next_selection: str = "docs/SOP/MISSING_NEXT.md") -> CloseoutSpec:
        return CloseoutSpec(
            chapter_id="test_chapter",
            chapter_title="Test Chapter",
            chapter_status="COMPLETE",
            closed_date="2026-06-30",
            evidence_doc="docs/SOP/TEST_EVIDENCE.md",
            sprint_spec="docs/SOP/SPRINT_TEST.md",
            next_selection_doc=next_selection,
            carry_docs=["docs/SOP/TEST_EVIDENCE.md"],
        )

    def test_validate_closeout_spec_docs_missing_next_selection(self) -> None:
        (self.repo / "docs" / "SOP" / "TEST_EVIDENCE.md").write_text("# ev\n", encoding="utf-8")
        (self.repo / "docs" / "SOP" / "SPRINT_TEST.md").write_text("# sprint\n", encoding="utf-8")
        errors = validate_closeout_spec_docs(self.repo, self._spec())
        self.assertTrue(any("next_selection_doc" in e for e in errors))

    def test_apply_closeout_aborts_on_missing_docs(self) -> None:
        report = apply_control_closeout(self.repo, closeout=self._spec())
        self.assertFalse(report["passed"])
        self.assertIn("doc_validation_errors", report)
        brief = self.repo / "docs" / "SOP" / "AGENT_CONTINUITY_BRIEF.md"
        self.assertFalse(brief.is_file())

    def test_stamp_evidence_archived_frontmatter(self) -> None:
        evidence = self.repo / "docs" / "SOP" / "TEST_EVIDENCE.md"
        evidence.write_text("# Evidence\n\n**Status:** **ACTIVE**\n", encoding="utf-8")
        ok = stamp_evidence_archived_frontmatter(
            self.repo,
            "docs/SOP/TEST_EVIDENCE.md",
            chapter_id="test_chapter",
            closed_date="2026-06-30",
        )
        self.assertTrue(ok)
        text = evidence.read_text(encoding="utf-8")
        self.assertIn("archived: true", text)
        self.assertIn("chapter_id: test_chapter", text)


if __name__ == "__main__":
    unittest.main()
