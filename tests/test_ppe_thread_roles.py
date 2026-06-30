"""Tests for thread role helpers."""

from __future__ import annotations

import unittest

from scripts.ppe_operator_status import VERDICT_IDE_BUILD, VERDICT_RUN_AUTO, VERDICT_RUN_LOCAL, _format_human
from scripts.ppe_thread_roles import (
    infer_next_thread_role,
    infer_suggest_thread_rotate,
    normalize_thread_role,
    prepend_role_opener,
)


class TestPpeThreadRoles(unittest.TestCase):
    def test_normalize_legacy_steward(self) -> None:
        self.assertEqual(normalize_thread_role("steward"), "operator")
        self.assertEqual(normalize_thread_role("exploratory"), "charter")

    def test_infer_suggest_thread_rotate_ide_build(self) -> None:
        out = infer_suggest_thread_rotate(
            verdict=VERDICT_IDE_BUILD,
            manifest_status="READY",
            plan_path="docs/SOP/PHASE_PLANS/x.json",
        )
        self.assertTrue(out["suggest_thread_rotate"])
        self.assertEqual(out["thread_rotate_reason"], "IDE_BUILD")

    def test_infer_suggest_thread_rotate_chapter_closeout(self) -> None:
        out = infer_suggest_thread_rotate(
            verdict=VERDICT_RUN_AUTO,
            manifest_status="COMPLETE",
            plan_path=None,
        )
        self.assertTrue(out["suggest_thread_rotate"])
        self.assertEqual(out["thread_rotate_reason"], "CHAPTER_CLOSEOUT")

    def test_infer_next_thread_role_from_charter(self) -> None:
        self.assertEqual(infer_next_thread_role(closing_role="charter"), "charter")

    def test_infer_next_thread_role_ide_build_verdict(self) -> None:
        self.assertEqual(
            infer_next_thread_role(closing_role="operator", operator_verdict=VERDICT_IDE_BUILD),
            "ide_build",
        )

    def test_prepend_role_opener_idempotent(self) -> None:
        text = "THREAD_ROLE: ide_build.\nDo work."
        self.assertEqual(prepend_role_opener(text, "IDE BUILD thread."), text)

    def test_format_human_includes_thread_rotate(self) -> None:
        body = _format_human(
            {
                "verdict": VERDICT_RUN_LOCAL,
                "supply": {"backlog": {}, "queue_ready": 0},
                "suggest_thread_rotate": True,
                "thread_rotate_reason": "RUN_LOCAL",
                "thread_rotate_message": "Rotate now.",
            },
            None,
        )
        self.assertIn("Thread rotate (recommended)", body)
        self.assertIn("RUN_LOCAL", body)


if __name__ == "__main__":
    unittest.main()
