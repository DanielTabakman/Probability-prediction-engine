"""Tests for ppe_token_audit."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_ide_build_starter import prune_starters_for_completed_chapters
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

    def write_completed_chapter_plan(self) -> Path:
        plan_rel = Path("docs/SOP/PHASE_PLANS/Completed_relay.json")
        evidence_rel = Path("docs/SOP/CHAPTER_EVIDENCE/Completed.md")
        plan_path = self.repo / plan_rel
        evidence_path = self.repo / evidence_rel
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        plan_path.write_text(
            json.dumps(
                {
                    "slices": [
                        {"sliceId": "Test-Slice001"},
                        {
                            "sliceId": "Completed-Closeout",
                            "closeout": {"evidenceDoc": evidence_rel.as_posix()},
                        },
                    ]
                }
            ),
            encoding="utf-8",
        )
        evidence_path.write_text("## Chapter status\n\n**COMPLETE**\n", encoding="utf-8")
        return self.repo / "artifacts" / "orchestrator" / "IDE_BUILD_STARTER_Test-Slice001.md"

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

    def test_build_token_audit_reports_stale_starter_read_only(self) -> None:
        starter = self.write_completed_chapter_plan()
        before = starter.read_bytes()

        report = build_token_audit(self.repo)

        self.assertEqual(report.stale_starter_ids, ["Test-Slice001"])
        self.assertTrue(starter.is_file())
        self.assertEqual(starter.read_bytes(), before)
        data = report.to_dict()
        self.assertEqual(len(data["starters"]), 1)
        self.assertEqual(data["starters"][0]["slice_id"], "Test-Slice001")
        self.assertEqual(data["always_on_total_chars"], sum(row.chars for row in report.rules if row.always_apply))

    def test_explicit_prune_removes_completed_chapter_starter(self) -> None:
        starter = self.write_completed_chapter_plan()

        removed = prune_starters_for_completed_chapters(self.repo)

        self.assertEqual(removed, ["Test-Slice001"])
        self.assertFalse(starter.exists())


if __name__ == "__main__":
    unittest.main()
