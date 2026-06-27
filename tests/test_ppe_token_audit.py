"""Tests for ppe_token_audit."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_token_audit import (
    ALWAYS_ON_CHAR_TARGET,
    STARTER_LINE_TARGET,
    audit_rules,
    build_recommendations,
    build_token_audit,
    render_token_audit_markdown,
)


class TestPpeTokenAudit(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        rules = self.repo / ".cursor" / "rules"
        rules.mkdir(parents=True)
        (rules / "ppe-operator-core.mdc").write_text(
            "---\nalwaysApply: true\n---\n\n# core\n" + ("x" * 500),
            encoding="utf-8",
        )
        (rules / "repo-layers.mdc").write_text(
            "---\nalwaysApply: false\n---\n\n# layers\n",
            encoding="utf-8",
        )
        orch = self.repo / "artifacts" / "orchestrator"
        orch.mkdir(parents=True)
        starter = "\n".join(["line"] * 50)
        (orch / "IDE_BUILD_STARTER_Test-Slice001.md").write_text(starter, encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_audit_rules_splits_always_on(self) -> None:
        rows = audit_rules(self.repo)
        always = [r for r in rows if r.always_apply]
        self.assertEqual(len(always), 1)
        self.assertEqual(always[0].name, "ppe-operator-core.mdc")

    def test_build_token_audit_report(self) -> None:
        report = build_token_audit(self.repo)
        data = report.to_dict()
        self.assertLess(data["always_on_total_chars"], ALWAYS_ON_CHAR_TARGET)
        self.assertEqual(len(data["starters"]), 1)
        self.assertTrue(data["starters"][0]["lines"], 50)
        md = render_token_audit_markdown(report)
        self.assertIn("Token economy audit", md)

    def test_recommendations_over_budget_starters(self) -> None:
        long_starter = "\n".join(["line"] * (STARTER_LINE_TARGET + 20))
        path = self.repo / "artifacts" / "orchestrator" / "IDE_BUILD_STARTER_Big.md"
        path.write_text(long_starter, encoding="utf-8")
        report = build_token_audit(self.repo)
        recs = build_recommendations(report)
        self.assertTrue(any("starter" in r.lower() for r in recs))

    def test_write_artifacts(self) -> None:
        from scripts.ppe_token_audit import write_token_audit_artifacts

        report = build_token_audit(self.repo)
        json_path, md_path = write_token_audit_artifacts(self.repo, report)
        self.assertTrue(json_path.is_file())
        self.assertTrue(md_path.is_file())
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertIn("always_on_total_chars", payload)


if __name__ == "__main__":
    unittest.main()
