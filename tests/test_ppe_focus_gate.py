"""Tests for product-focus gate (validation report + urgent bypass)."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_auto_select import run_auto_select
from scripts.ppe_focus_gate import (
    evaluate_focus_gate,
    format_ide_focus_block,
    infer_focus_playbook_tier_from_reason,
    validation_report_blocks_selection,
    validation_report_gate_issues,
    validation_report_status,
)
from scripts.ppe_manifest import save_manifest
from scripts.ppe_propagate_queue import propagate_from_backlog


class TestPpeFocusGate(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        plans = sop / "PHASE_PLANS"
        plans.mkdir(parents=True)
        self.plan_rel = "docs/SOP/PHASE_PLANS/chapter.json"
        plan = {
            "name": "ch",
            "sprintSpecPath": "docs/SOP/SPRINT.md",
            "selectionRecord": "docs/SOP/SEL.md",
            "slices": [{"sliceId": "X-Closeout", "closeout": {"chapterId": "x"}}],
        }
        (plans / "chapter.json").write_text(json.dumps(plan), encoding="utf-8")
        (sop / "SPRINT.md").write_text("# s\n", encoding="utf-8")
        (sop / "SEL.md").write_text("# s\n", encoding="utf-8")
        os.environ["PPE_FOCUS_GATE"] = "1"

    def tearDown(self) -> None:
        os.environ.pop("PPE_FOCUS_GATE", None)
        self._tmp.cleanup()

    def _write_draft_report(self) -> None:
        p = self.repo / "docs" / "SOP" / "MSOS_P8_VALIDATION_REPORT_V1.md"
        p.write_text("**Status:** **DRAFT**\n", encoding="utf-8")

    def _write_complete_report(self) -> None:
        p = self.repo / "docs" / "SOP" / "MSOS_P8_VALIDATION_REPORT_V1.md"
        p.write_text("**Status:** **COMPLETE**\n", encoding="utf-8")

    def test_validation_report_status(self) -> None:
        self._write_draft_report()
        self.assertEqual(validation_report_status(self.repo), "DRAFT")
        self._write_complete_report()
        self.assertEqual(validation_report_status(self.repo), "COMPLETE")

    def test_gate_blocks_without_urgent(self) -> None:
        self._write_draft_report()
        (self.repo / "docs" / "SOP" / "PHASE_CHAPTER_BACKLOG.json").write_text(
            json.dumps(
                {
                    "items": [
                        {
                            "chapterId": "ch",
                            "planPath": self.plan_rel,
                            "focusPlaybookTier": "P2",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        focus = evaluate_focus_gate(self.repo, self.plan_rel)
        self.assertFalse(focus.allowed)
        self.assertEqual(focus.tier, "P2")

    def test_urgent_bypass(self) -> None:
        self._write_draft_report()
        (self.repo / "docs" / "SOP" / "PHASE_CHAPTER_BACKLOG.json").write_text(
            json.dumps(
                {
                    "items": [
                        {
                            "chapterId": "ch",
                            "planPath": self.plan_rel,
                            "urgent": True,
                            "urgentReason": "IRL demo",
                            "focusPlaybookTier": "P0",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        focus = evaluate_focus_gate(self.repo, self.plan_rel)
        self.assertTrue(focus.allowed)
        self.assertTrue(focus.urgent_bypass)

    def test_auto_select_skips_when_gate_blocks(self) -> None:
        self._write_draft_report()
        sop = self.repo / "docs" / "SOP"
        (sop / "PHASE_QUEUE.json").write_text(
            json.dumps(
                {
                    "items": [
                        {"planPath": self.plan_rel, "status": "READY", "reason": "[LOW] test"},
                    ]
                }
            ),
            encoding="utf-8",
        )
        save_manifest(self.repo, {"phasePlanPath": "", "status": "COMPLETE", "notes": ""})
        rc = run_auto_select(self.repo, apply=True, select_only=False, mark_done=False, force=False)
        self.assertEqual(rc, 0)
        from scripts.ppe_manifest import load_manifest

        self.assertEqual(load_manifest(self.repo).get("phasePlanPath"), "")

    def test_auto_select_allows_when_report_complete(self) -> None:
        self._write_complete_report()
        sop = self.repo / "docs" / "SOP"
        (sop / "PHASE_QUEUE.json").write_text(
            json.dumps(
                {
                    "items": [
                        {"planPath": self.plan_rel, "status": "READY", "reason": "ok"},
                    ]
                }
            ),
            encoding="utf-8",
        )
        save_manifest(self.repo, {"phasePlanPath": "", "status": "COMPLETE", "notes": ""})
        rc = run_auto_select(self.repo, apply=True, select_only=False, mark_done=False, force=False)
        self.assertEqual(rc, 0)
        from scripts.ppe_manifest import load_manifest

        self.assertEqual(load_manifest(self.repo)["phasePlanPath"], self.plan_rel)

    def test_propagate_blocked_by_gate(self) -> None:
        self._write_draft_report()
        os.environ["PPE_AUTO_PROPAGATE_QUEUE"] = "1"
        sop = self.repo / "docs" / "SOP"
        (sop / "PHASE_SELECTION_ROADMAP.json").write_text(
            json.dumps({"version": 1, "items": []}),
            encoding="utf-8",
        )
        (sop / "PHASE_QUEUE.json").write_text(json.dumps({"version": 1, "items": []}), encoding="utf-8")
        (sop / "PHASE_CHAPTER_BACKLOG.json").write_text(
            json.dumps(
                {
                    "items": [
                        {
                            "chapterId": "ch",
                            "status": "queued",
                            "planPath": self.plan_rel,
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        save_manifest(self.repo, {"phasePlanPath": "", "status": "COMPLETE", "notes": ""})
        out = propagate_from_backlog(self.repo, apply=True)
        self.assertFalse(out.get("propagated"))
        self.assertIn("focus gate", str(out.get("reason", "")))

    def test_p2_low_priority_bypasses_draft_report(self) -> None:
        self._write_draft_report()
        (self.repo / "docs" / "SOP" / "PHASE_CHAPTER_BACKLOG.json").write_text(
            json.dumps(
                {
                    "items": [
                        {
                            "chapterId": "ch",
                            "planPath": self.plan_rel,
                            "focusPlaybookTier": "P2",
                            "priority": "low",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        focus = evaluate_focus_gate(self.repo, self.plan_rel)
        self.assertTrue(focus.allowed)
        self.assertIn("P2 low-priority", focus.reason)

    def test_infer_focus_playbook_tier_from_reason(self) -> None:
        self.assertEqual(infer_focus_playbook_tier_from_reason("[LOW] quant"), "P2")
        self.assertEqual(infer_focus_playbook_tier_from_reason("[P3] distro"), "P3")

    def test_validation_report_gate_issues_when_p8_complete_but_report_draft(self) -> None:
        self._write_draft_report()
        p8 = self.repo / "docs" / "SOP" / "MSOS_P8_TESTER_RELEASE_EVIDENCE_STATUS.md"
        p8.write_text("**Status:** **COMPLETE** 2026-06-12\n", encoding="utf-8")
        issues = validation_report_gate_issues(self.repo)
        self.assertEqual(len(issues), 1)
        self.assertIn("focus_gate", issues[0])

    def test_validation_report_gate_issues_clear_when_complete(self) -> None:
        self._write_complete_report()
        p8 = self.repo / "docs" / "SOP" / "MSOS_P8_TESTER_RELEASE_EVIDENCE_STATUS.md"
        p8.write_text("**Status:** **COMPLETE** 2026-06-12\n", encoding="utf-8")
        self.assertEqual(validation_report_gate_issues(self.repo), [])

    def test_format_ide_focus_block(self) -> None:
        text = format_ide_focus_block(tier="P2", urgent_bypass=False)
        self.assertIn("North star", text)
        self.assertIn("P2", text)


if __name__ == "__main__":
    unittest.main()
