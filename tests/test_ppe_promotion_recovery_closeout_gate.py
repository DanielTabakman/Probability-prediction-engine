"""Closeout promotion recovery must not run while non-closeout slices remain."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_promotion_recovery import try_recover


class TestPpePromotionRecoveryCloseoutGate(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        plans = sop / "PHASE_PLANS"
        plans.mkdir(parents=True)
        self.plan_path = plans / "phase.json"
        self.plan_path.write_text(
            json.dumps(
                {
                    "slices": [
                        {"sliceId": "X-Platform-Slice003"},
                        {
                            "sliceId": "X-Closeout-Slice005",
                            "closeout": {
                                "chapterId": "x",
                                "evidenceDoc": "docs/SOP/X_EVIDENCE.md",
                            },
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
        (sop / "X_EVIDENCE.md").write_text("# X\n", encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @patch("scripts.ppe_promotion_recovery.repair_queue", return_value=([], []))
    @patch("scripts.ppe_promotion_recovery._load_decision", return_value={"decision": "STOP_FOR_REVIEW"})
    @patch(
        "scripts.ppe_promotion_recovery._load_relay_result",
        return_value={
            "stop_condition": "UNCLEAR_TEST_RESULTS",
            "build_branch": "build/auto/X-Closeout",
            "promotion": {"performed": False},
            "baseline_branch": "main",
        },
    )
    @patch("scripts.ppe_promotion_recovery._find_newest_relay_run")
    @patch("scripts.ppe_promotion_recovery._run", return_value=type("P", (), {"returncode": 0, "stdout": "abc"})())
    def test_closeout_skipped_when_slices_pending(
        self,
        _git: object,
        mock_find: object,
        *_rest: object,
    ) -> None:
        run_dir = self.repo / "artifacts" / "relay" / "runs" / "r1"
        run_dir.mkdir(parents=True)
        mock_find.return_value = run_dir
        progress = self.repo / "artifacts" / "orchestrator" / "PHASE_SLICE_PROGRESS.json"
        progress.parent.mkdir(parents=True)
        progress.write_text(
            json.dumps(
                {
                    "planPath": "docs/SOP/PHASE_PLANS/phase.json",
                    "completedSliceIds": [],
                }
            ),
            encoding="utf-8",
        )
        with patch("scripts.ppe_promotion_recovery._run_control_closeout") as mock_closeout:
            rc = try_recover(
                self.repo,
                exit_code=20,
                phase_plan=self.plan_path,
                slice_id="X-Closeout-Slice005",
                build_branch="build/auto/X-Closeout",
            )
            mock_closeout.assert_not_called()
        self.assertIn(rc, (0, 100))


if __name__ == "__main__":
    unittest.main()
