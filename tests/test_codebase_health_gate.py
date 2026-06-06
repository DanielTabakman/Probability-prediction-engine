"""Tests for scripts/run_codebase_health_gate.py."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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
    def test_gate_passes_on_clean_repo(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        result = run_gate(repo)
        self.assertTrue(result["ok"], msg="\n".join(result["errors"]))
        self.assertIsNotNone(result["artifacts"]["codebase_health_report"])
        self.assertIsNotNone(result["artifacts"]["control_plane_consistency_report"])

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
