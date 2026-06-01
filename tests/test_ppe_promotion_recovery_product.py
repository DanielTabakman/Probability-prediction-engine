"""Product-slice promotion recovery must not auto-advance without commits."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_promotion_recovery import try_recover


class TestPpePromotionRecoveryProduct(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP" / "PHASE_PLANS"
        sop.mkdir(parents=True)
        self.plan_path = sop / "phase.json"
        self.plan_path.write_text(
            json.dumps(
                {
                    "slices": [
                        {"sliceId": "MVP1-Product-Slice002"},
                        {"sliceId": "MVP1-Smoke-Slice003"},
                    ],
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @patch("scripts.ppe_promotion_recovery.repair_queue", return_value=([], []))
    @patch("scripts.ppe_promotion_recovery._load_decision", return_value={"decision": "STOP_FOR_REVIEW"})
    @patch(
        "scripts.ppe_promotion_recovery._load_relay_result",
        return_value={
            "stop_condition": "SCOPE_AMBIGUITY",
            "build_branch": "build/auto/MVP1-Product-Slice002-local",
            "promotion": {"performed": False},
        },
    )
    @patch("scripts.ppe_promotion_recovery._find_newest_relay_run")
    @patch("scripts.ppe_promotion_recovery._build_branch_has_product_commits", return_value=False)
    def test_scope_ambiguity_product_does_not_return_100(
        self,
        _commits: object,
        mock_find: object,
        *_rest: object,
    ) -> None:
        run_dir = self.repo / "artifacts" / "relay" / "runs" / "r1"
        run_dir.mkdir(parents=True)
        mock_find.return_value = run_dir
        rc = try_recover(
            self.repo,
            exit_code=20,
            phase_plan=self.plan_path,
            slice_id="MVP1-Product-Slice002",
            build_branch="build/auto/MVP1-Product-Slice002-local",
        )
        self.assertEqual(rc, 0)

    @patch("scripts.ppe_promotion_recovery.repair_queue", return_value=([], []))
    @patch("scripts.ppe_promotion_recovery._load_decision", return_value={"decision": "STOP_FOR_REVIEW"})
    @patch("scripts.ppe_promotion_recovery._load_relay_result")
    @patch("scripts.ppe_promotion_recovery._find_newest_relay_run")
    @patch("scripts.ppe_promotion_recovery._build_branch_has_product_commits", return_value=True)
    def test_product_with_commits_may_resume(
        self,
        _commits: object,
        mock_find: object,
        mock_relay: object,
        *_rest: object,
    ) -> None:
        run_dir = self.repo / "artifacts" / "relay" / "runs" / "r1"
        run_dir.mkdir(parents=True)
        mock_find.return_value = run_dir
        mock_relay.return_value = {
            "stop_condition": "SCOPE_AMBIGUITY",
            "build_branch": "build/auto/MVP1-Product-Slice002-local",
            "baseline_branch": "main",
            "promotion": {"performed": False},
        }
        rc = try_recover(
            self.repo,
            exit_code=20,
            phase_plan=self.plan_path,
            slice_id="MVP1-Product-Slice002",
            build_branch="build/auto/MVP1-Product-Slice002-local",
        )
        self.assertEqual(rc, 100)


if __name__ == "__main__":
    unittest.main()
