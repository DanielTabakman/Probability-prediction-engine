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
        self.assertEqual(normalize_thread_role("steward"), "charter")
        self.assertEqual(normalize_thread_role("exploratory"), "charter")

    def test_classify_parked_lane(self) -> None:
        from scripts.ppe_thread_roles import (
            PARKED_LANE_CONTROL,
            PARKED_LANE_RELAY,
            classify_parked_lane,
        )

        self.assertEqual(classify_parked_lane("merge delegation PR #1039"), PARKED_LANE_CONTROL)
        self.assertEqual(classify_parked_lane("spine closeout DESKTOP_CONTINUE"), PARKED_LANE_RELAY)
        self.assertEqual(classify_parked_lane("Stripe billing decision"), "human")

    def test_infer_thread_role_from_opener(self) -> None:
        from scripts.ppe_thread_roles import infer_thread_role_from_opener

        self.assertEqual(infer_thread_role_from_opener("what's next?"), "operator")
        self.assertEqual(
            infer_thread_role_from_opener("Charter thread. THREAD_ROLE: charter. UX backlog."),
            "charter",
        )
        self.assertEqual(
            infer_thread_role_from_opener("close out thread — delegation v2 wiring"),
            "charter",
        )

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
