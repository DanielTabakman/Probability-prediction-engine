"""Tests for milestone gate v2 (closeout debt, steering reconcile)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_milestone_gate import (
    ACTIVE_CHAPTER_GATE,
    CLOSEOUT_REGISTRY_DEBT,
    STEERING_CANDIDATE_STALE,
    advance_steering_candidate,
    assess_closeout_debt,
    is_steering_candidate_stale,
    milestone_gate_issues,
    prune_stale_closeout_registry,
    reconcile_milestone_gate,
    resolve_next_build_candidate,
)


def _write_evidence(path: Path, *, complete: bool = True, pending: bool = False) -> None:
    status = "**COMPLETE** 2026-06-30" if complete else "**WITNESS COMPLETE**"
    rows = "| MSOS-X-Product-Slice002 | COMPLETE |\n"
    if pending:
        rows += "| MSOS-X-Platform-Slice007 | PENDING |\n"
    path.write_text(
        f"# Evidence\n\n**Status:** {status}\n\n| Slice | Status |\n|-------|--------|\n{rows}",
        encoding="utf-8",
    )


def _minimal_plan(
    repo: Path,
    chapter_id: str,
    *,
    evidence_rel: str,
    pending_evidence: bool = False,
) -> str:
    plan_path = f"docs/SOP/PHASE_PLANS/{chapter_id}_relay.json"
    evidence_path = repo / evidence_rel
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    _write_evidence(evidence_path, complete=not pending_evidence, pending=pending_evidence)
    plan = {
        "slices": [
            {
                "sliceId": f"MSOS-X-Closeout-Slice009",
                "closeout": {
                    "chapterId": chapter_id,
                    "evidenceDoc": evidence_rel,
                },
            }
        ]
    }
    full = repo / plan_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(json.dumps(plan), encoding="utf-8")
    return plan_path


class TestPpeMilestoneGate(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True)
        (sop / "PHASE_QUEUE.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "items": [
                        {
                            "planPath": "docs/SOP/PHASE_PLANS/msos_trader_workflow_horizon_nav_v1_relay.json",
                            "status": "DONE",
                        },
                        {
                            "planPath": "docs/SOP/PHASE_PLANS/msos_cross_venue_strategy_lab_v1_relay.json",
                            "status": "READY",
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
        (sop / "AGENT_STEERING_V1.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "nextBuildCandidateId": "msos_trader_workflow_horizon_nav_v1",
                    "spineQueueAfterCloseout": ["msos_cross_venue_strategy_lab_v1"],
                    "closeoutOnlyChapterIds": [
                        "msos_trader_workflow_horizon_nav_v1",
                        "msos_storyboard_visual_parity_v1",
                    ],
                }
            ),
            encoding="utf-8",
        )
        (sop / "ACTIVE_PHASE_MANIFEST.json").write_text(
            json.dumps(
                {
                    "phasePlanPath": "docs/SOP/PHASE_PLANS/msos_storyboard_visual_parity_v1_relay.json",
                    "status": "READY",
                }
            ),
            encoding="utf-8",
        )
        _minimal_plan(
            self.repo,
            "msos_trader_workflow_horizon_nav_v1",
            evidence_rel="docs/SOP/MSOS_TRADER_WORKFLOW_HORIZON_NAV_V1_EVIDENCE_STATUS.md",
        )
        _minimal_plan(
            self.repo,
            "msos_cross_venue_strategy_lab_v1",
            evidence_rel="docs/SOP/MSOS_CROSS_VENUE_STRATEGY_LAB_V1_EVIDENCE_STATUS.md",
        )
        _minimal_plan(
            self.repo,
            "msos_storyboard_visual_parity_v1",
            evidence_rel="docs/SOP/MSOS_STORYBOARD_VISUAL_PARITY_V1_EVIDENCE_STATUS.md",
            pending_evidence=True,
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_steering_candidate_stale_when_complete_and_done(self) -> None:
        self.assertTrue(is_steering_candidate_stale(self.repo))

    def test_resolve_next_build_skips_stale_steering(self) -> None:
        resolved = resolve_next_build_candidate(self.repo)
        self.assertEqual(resolved, "msos_cross_venue_strategy_lab_v1")

    def test_assess_closeout_debt_active_gate(self) -> None:
        debt = assess_closeout_debt(self.repo)
        self.assertEqual(debt["active_chapter_id"], "msos_storyboard_visual_parity_v1")
        self.assertGreater(int(debt["active_pending_count"] or 0), 0)
        self.assertTrue(debt["steering_stale"])

    def test_milestone_gate_issues_include_stale_and_active(self) -> None:
        debt = assess_closeout_debt(self.repo)
        codes = {i["code"] for i in milestone_gate_issues(self.repo, debt)}
        self.assertIn(ACTIVE_CHAPTER_GATE, codes)
        self.assertIn(STEERING_CANDIDATE_STALE, codes)

    def test_advance_steering_candidate_apply(self) -> None:
        out = advance_steering_candidate(self.repo, apply=True)
        self.assertTrue(out["applied"])
        self.assertEqual(out["nextBuildCandidateId"], "msos_cross_venue_strategy_lab_v1")
        steering = json.loads(
            (self.repo / "docs/SOP/AGENT_STEERING_V1.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            steering["nextBuildCandidateId"],
            "msos_cross_venue_strategy_lab_v1",
        )

    def test_prune_stale_registry_dry_run(self) -> None:
        out = prune_stale_closeout_registry(self.repo, apply=False)
        self.assertIn("msos_trader_workflow_horizon_nav_v1", out["pruned"])

    def test_reconcile_milestone_gate_apply(self) -> None:
        out = reconcile_milestone_gate(self.repo, apply=True)
        self.assertGreaterEqual(out["prune"]["pruned_count"], 1)
        self.assertTrue(out["advance"]["applied"])
        steering = json.loads(
            (self.repo / "docs/SOP/AGENT_STEERING_V1.json").read_text(encoding="utf-8")
        )
        self.assertNotIn("msos_trader_workflow_horizon_nav_v1", steering["closeoutOnlyChapterIds"])
        self.assertEqual(
            steering["nextBuildCandidateId"],
            "msos_cross_venue_strategy_lab_v1",
        )

    def test_registry_debt_issue_when_stale_present(self) -> None:
        debt = assess_closeout_debt(self.repo)
        codes = {i["code"] for i in milestone_gate_issues(self.repo, debt)}
        if int(debt.get("registry_stale") or 0) > 0:
            self.assertIn(CLOSEOUT_REGISTRY_DEBT, codes)


if __name__ == "__main__":
    unittest.main()
