"""Tests for ppe_token_audit."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_token_audit import (
    ALWAYS_ON_CHAR_TARGET,
    append_history_snapshot,
    audit_rules,
    build_token_audit,
    compute_verdict,
    read_history,
)


class TestPpeTokenAudit(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        rules = self.repo / ".cursor" / "rules"
        rules.mkdir(parents=True)
        (rules / "ppe-operator-core.mdc").write_text(
            "---\nalwaysApply: true\n---\n\n# core\n" + ("x" * 400),
            encoding="utf-8",
        )
        (rules / "repo-layers.mdc").write_text("---\nalwaysApply: false\n---\n\n# x\n", encoding="utf-8")
        orch = self.repo / "artifacts" / "orchestrator"
        orch.mkdir(parents=True)
        (orch / "IDE_BUILD_STARTER_Test-Slice001.md").write_text("\n".join(["line"] * 50), encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_audit_rules(self) -> None:
        rows = audit_rules(self.repo)
        always = [r for r in rows if r.always_apply]
        self.assertEqual(len(always), 1)

    def test_build_and_verdict_ok(self) -> None:
        report = build_token_audit(self.repo)
        self.assertEqual(compute_verdict(report), "OK")
        self.assertLess(report.to_dict()["always_on_total_chars"], ALWAYS_ON_CHAR_TARGET)

    def test_history_append(self) -> None:
        report = build_token_audit(self.repo)
        path = append_history_snapshot(self.repo, report)
        self.assertTrue(path.is_file())
        rows = read_history(self.repo)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["verdict"], report.verdict)


if __name__ == "__main__":
    unittest.main()
