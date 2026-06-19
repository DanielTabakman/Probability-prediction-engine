"""Tests for continuous operator guards."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_operator_guards import (
    GUARD_EXIT,
    GUARD_SKIP_CHAPTER,
    evaluate_selection_guards,
    run_continuous_guards,
)


def _operator_json(**guards: object) -> str:
    return json.dumps(
        {
            "enabled": True,
            "guards": {"enabled": True, **guards},
        }
    )


class TestPpeOperatorGuards(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        plans = sop / "PHASE_PLANS"
        sop.mkdir(parents=True)
        plans.mkdir(parents=True)
        (sop / "PPE_AUTO_OPERATOR.json").write_text(
            _operator_json(blockProductUnderGlobalDeterministic=True),
            encoding="utf-8",
        )
        plan = {
            "sprintSpecPath": "docs/SOP/SPRINT_TEST.md",
            "slices": [
                {"sliceId": "Ch-Control-Slice001"},
                {"sliceId": "Ch-Product-Slice002"},
                {"sliceId": "Ch-Closeout-Slice003", "closeout": True},
            ],
        }
        (plans / "test_relay.json").write_text(json.dumps(plan), encoding="utf-8")
        os.environ["PPE_SKIP_ACP"] = "1"

    def tearDown(self) -> None:
        os.environ.pop("PPE_SKIP_ACP", None)
        os.environ.pop("PPE_OPERATOR_GUARDS", None)
        self._tmp.cleanup()

    def test_product_plan_blocked_under_skip_acp(self) -> None:
        rc = run_continuous_guards(self.repo, "docs/SOP/PHASE_PLANS/test_relay.json")
        self.assertEqual(rc, GUARD_EXIT)
        report = self.repo / "artifacts/orchestrator/OPERATOR_GUARD_REPORT.md"
        text = report.read_text(encoding="utf-8")
        self.assertTrue(report.is_file())
        self.assertIn("PRODUCT_BLOCKED", text)
        self.assertIn("[Ch-Product-Slice002]", text)
        self.assertIn("IDE_BUILD_STARTER", text)

    def test_product_guard_shows_next_pending_only(self) -> None:
        from scripts.ppe_ide_product_ready import write_marker

        plan = {
            "sprintSpecPath": "docs/SOP/SPRINT_TEST.md",
            "slices": [
                {"sliceId": "Ch-Control-Slice001"},
                {"sliceId": "Ch-Product-Slice002"},
                {"sliceId": "Ch-Product-Slice003"},
                {"sliceId": "Ch-Closeout-Slice004", "closeout": True},
            ],
        }
        plan_rel = "docs/SOP/PHASE_PLANS/multi.json"
        path = self.repo / "docs" / "SOP" / "PHASE_PLANS" / "multi.json"
        path.write_text(json.dumps(plan), encoding="utf-8")
        write_marker(
            self.repo,
            phase_plan_path=plan_rel,
            slice_id="Ch-Product-Slice002",
            build_branch="main",
            commit_sha="abc123",
        )
        rc = run_continuous_guards(self.repo, plan_rel)
        self.assertEqual(rc, GUARD_EXIT)
        detail = (self.repo / "artifacts/orchestrator/OPERATOR_GUARD_REPORT.md").read_text(encoding="utf-8")
        self.assertIn("[Ch-Product-Slice003]", detail)
        bracket = detail.split("[", 1)[1].split("]", 1)[0]
        self.assertNotIn("Ch-Product-Slice002", bracket)

    @patch("scripts.ppe_ide_product_ready.next_pending_product_slice", return_value=None)
    def test_product_plan_ok_with_marker(self, *_m: object) -> None:
        rc = run_continuous_guards(self.repo, "docs/SOP/PHASE_PLANS/test_relay.json")
        self.assertEqual(rc, 0)

    def test_evidence_only_plan_ok(self) -> None:
        plan = {
            "slices": [
                {"sliceId": "Ch-Control-Slice001"},
                {"sliceId": "Ch-Smoke-Slice002"},
            ],
        }
        path = self.repo / "docs/SOP/PHASE_PLANS/evidence.json"
        path.write_text(json.dumps(plan), encoding="utf-8")
        rc = run_continuous_guards(self.repo, "docs/SOP/PHASE_PLANS/evidence.json")
        self.assertEqual(rc, 0)

    def test_context_escalate(self) -> None:
        evidence_plan = self.repo / "docs" / "SOP" / "PHASE_PLANS" / "evidence.json"
        evidence_plan.write_text(
            json.dumps({"sprintSpecPath": "docs/SOP/SPRINT_TEST.md", "slices": [{"sliceId": "Ch-Control-Slice001"}]}),
            encoding="utf-8",
        )
        (self.repo / "docs" / "SOP" / "SPRINT_TEST.md").write_text(
            "\n".join(["line"] * 401),
            encoding="utf-8",
        )
        (self.repo / "docs" / "SOP" / "PPE_AUTO_OPERATOR.json").write_text(
            _operator_json(
                blockProductUnderGlobalDeterministic=False,
                stopOnContextEscalate=True,
            ),
            encoding="utf-8",
        )
        rc = run_continuous_guards(self.repo, "docs/SOP/PHASE_PLANS/evidence.json")
        self.assertEqual(rc, GUARD_EXIT)
        report = (self.repo / "artifacts/orchestrator/OPERATOR_GUARD_REPORT.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("CONTEXT_ESCALATE", report)

    def test_max_phase_slices(self) -> None:
        (self.repo / "docs" / "SOP" / "PPE_AUTO_OPERATOR.json").write_text(
            _operator_json(
                blockProductUnderGlobalDeterministic=False,
                maxPhaseSlices=2,
                phaseSliceBatching=False,
            ),
            encoding="utf-8",
        )
        rc = run_continuous_guards(self.repo, "docs/SOP/PHASE_PLANS/test_relay.json")
        self.assertEqual(rc, GUARD_EXIT)
        self.assertIn("TOO_MANY_SLICES", (self.repo / "artifacts/orchestrator/OPERATOR_GUARD_REPORT.md").read_text(encoding="utf-8"))

    def test_selection_guard_skips_evidence_complete(self) -> None:
        evidence = self.repo / "docs" / "SOP" / "CHAPTER_DONE_EVIDENCE.md"
        evidence.write_text("# Evidence\n\n**Status:** **COMPLETE** 2026-06-05\n", encoding="utf-8")
        plan = {
            "sprintSpecPath": "docs/SOP/SPRINT_TEST.md",
            "slices": [
                {
                    "sliceId": "Ch-Closeout-Slice003",
                    "closeout": {"evidenceDoc": "docs/SOP/CHAPTER_DONE_EVIDENCE.md"},
                }
            ],
        }
        (self.repo / "docs" / "SOP" / "PHASE_PLANS" / "done_relay.json").write_text(
            json.dumps(plan),
            encoding="utf-8",
        )
        guard = evaluate_selection_guards(self.repo, "docs/SOP/PHASE_PLANS/done_relay.json")
        self.assertIsNotNone(guard)
        assert guard is not None
        self.assertEqual(guard.exit_code, GUARD_SKIP_CHAPTER)
        self.assertEqual(guard.reason, "SKIP_CHAPTER_EVIDENCE_COMPLETE")

    @patch("scripts.ppe_operator_guards.chapter_marked_complete_in_repo", return_value=True)
    def test_skip_evidence_complete(self, *_m: object) -> None:
        (self.repo / "docs" / "SOP" / "PHASE_QUEUE.json").write_text(
            json.dumps({"version": 1, "items": [{"planPath": "docs/SOP/PHASE_PLANS/test_relay.json", "status": "READY"}]}),
            encoding="utf-8",
        )
        (self.repo / "docs" / "SOP" / "ACTIVE_PHASE_MANIFEST.json").write_text(
            json.dumps({"phasePlanPath": "docs/SOP/PHASE_PLANS/test_relay.json", "status": "READY"}),
            encoding="utf-8",
        )
        rc = run_continuous_guards(self.repo, "docs/SOP/PHASE_PLANS/test_relay.json")
        self.assertEqual(rc, GUARD_SKIP_CHAPTER)

    def test_stripe_deferred_when_operator_prereq_open(self) -> None:
        stripe_plan = "docs/SOP/PHASE_PLANS/msos_billing_stripe_v1_relay.json"
        (self.repo / "docs" / "SOP" / "PHASE_PLANS" / "msos_billing_stripe_v1_relay.json").write_text(
            json.dumps({"sprintSpecPath": "docs/SOP/SPRINT_TEST.md", "slices": []}),
            encoding="utf-8",
        )
        (self.repo / "docs" / "SOP" / "HUMAN_STEWARD_BACKLOG.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "items": [
                        {
                            "id": "stripe_operator_prereq",
                            "status": "open",
                            "title": "Stripe operator prerequisites",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        guard = evaluate_selection_guards(self.repo, stripe_plan)
        self.assertIsNotNone(guard)
        assert guard is not None
        self.assertEqual(guard.exit_code, GUARD_SKIP_CHAPTER)
        self.assertEqual(guard.reason, "STRIPE_BUILD_DEFERRED")


if __name__ == "__main__":
    unittest.main()
