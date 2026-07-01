"""Tests for scripts/run_codebase_health_gate.py."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_codebase_health_gate import (
    evaluate_codebase_health_report,
    evaluate_consistency_report,
    run_gate,
)


class TestEvaluateCodebaseHealthReport(unittest.TestCase):
    def test_missing_canonical_doc_is_error(self) -> None:
        errors, warnings = evaluate_codebase_health_report(
            {
                "canonical_docs_present": {"docs/SOP/HANDOFF.md": False},
                "known_unresolved_items": [],
                "tree_cleanliness": {},
            }
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("missing canonical doc", errors[0])
        self.assertEqual(warnings, [])

    def test_unresolved_items_are_warnings(self) -> None:
        errors, warnings = evaluate_codebase_health_report(
            {
                "canonical_docs_present": {"docs/SOP/HANDOFF.md": True},
                "known_unresolved_items": ["scratch.txt"],
                "tree_cleanliness": {},
            }
        )
        self.assertEqual(errors, [])
        self.assertTrue(any("unresolved" in w for w in warnings))

    def test_structural_warnings_are_logged(self) -> None:
        errors, warnings = evaluate_codebase_health_report(
            {
                "canonical_docs_present": {},
                "known_unresolved_items": [],
                "tree_cleanliness": {},
                "structural_health": {
                    "warnings": [
                        {
                            "id": "app-py-monolith",
                            "severity": "watch",
                            "message": "app.py too large",
                        }
                    ]
                },
            }
        )
        self.assertEqual(errors, [])
        self.assertTrue(any("structural_health" in w for w in warnings))


class TestEvaluateConsistencyReport(unittest.TestCase):
    def test_error_findings_fail(self) -> None:
        errors, warnings = evaluate_consistency_report(
            {
                "passed": False,
                "findings": [
                    {
                        "severity": "error",
                        "doc": "docs/SOP/HANDOFF.md",
                        "locator": "line 1",
                        "message": "broken link",
                    }
                ],
            }
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("broken link", errors[0])

    def test_warnings_do_not_fail(self) -> None:
        errors, warnings = evaluate_consistency_report(
            {
                "passed": True,
                "findings": [
                    {
                        "severity": "warn",
                        "doc": "docs/SOP/HANDOFF.md",
                        "locator": "line 2",
                        "message": "duplicate heading",
                    }
                ],
            }
        )
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)


class TestRunGateIntegration(unittest.TestCase):
    def test_backlog_evidence_complete_fails_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            sop = repo / "docs" / "SOP"
            plans = sop / "PHASE_PLANS"
            plans.mkdir(parents=True)
            (sop / "PHASE_QUEUE.json").write_text(
                json.dumps({"version": 1, "items": []}),
                encoding="utf-8",
            )
            (sop / "CHAPTER_DONE_EVIDENCE.md").write_text(
                "# Evidence\n\n**Status:** **COMPLETE** 2026-06-05\n",
                encoding="utf-8",
            )
            plan = {
                "name": "done",
                "slices": [
                    {
                        "sliceId": "X-Closeout",
                        "closeout": {"evidenceDoc": "docs/SOP/CHAPTER_DONE_EVIDENCE.md"},
                    }
                ],
            }
            (plans / "done.json").write_text(json.dumps(plan), encoding="utf-8")
            (sop / "PHASE_CHAPTER_BACKLOG.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "items": [
                            {
                                "chapterId": "done",
                                "status": "blocked",
                                "planPath": "docs/SOP/PHASE_PLANS/done.json",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = run_gate(repo, skip_relay=True)
            self.assertFalse(result["ok"])
            self.assertTrue(
                any("BACKLOG_ACTIVE_BUT_EVIDENCE_COMPLETE" in err for err in result["errors"])
            )

    def test_queue_issues_fail_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            sop = repo / "docs" / "SOP"
            sop.mkdir(parents=True)
            (sop / "PHASE_QUEUE.json").write_text(
                json.dumps({"version": 1, "items": "not-an-array"}),
                encoding="utf-8",
            )
            result = run_gate(repo, skip_relay=True)
            self.assertFalse(result["ok"])
            self.assertTrue(any("queue" in err for err in result["errors"]))


if __name__ == "__main__":
    unittest.main()
