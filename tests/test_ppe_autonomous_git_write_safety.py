"""Safety tests for Autobuilder GitHub write opt-in and VM mirror churn guards."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_operator_config import autonomous_git_writes_enabled, load_operator_config
from scripts.ppe_vm_phase_mirror import _heartbeat_publish_due, maybe_commit_publish_vm_mirror


class TestAutonomousGitWriteSafety(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True)
        (sop / "PPE_AUTO_OPERATOR.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "enabled": True,
                    "gitSync": {
                        "enabled": True,
                        "pullEachPass": True,
                        "publishEachPass": True,
                        "mergeEachPass": True,
                        "pushAfterCommit": True,
                        "openPrOnPush": True,
                    },
                }
            ),
            encoding="utf-8",
        )
        os.environ.pop("PPE_GIT_AUTONOMOUS_WRITES", None)
        os.environ.pop("PPE_OPERATOR_PROFILE", None)

    def tearDown(self) -> None:
        os.environ.pop("PPE_GIT_AUTONOMOUS_WRITES", None)
        os.environ.pop("PPE_OPERATOR_PROFILE", None)
        self._tmp.cleanup()

    def test_autonomous_git_writes_are_fail_closed_by_default(self) -> None:
        self.assertFalse(autonomous_git_writes_enabled())
        git_sync = load_operator_config(self.repo)["gitSync"]
        self.assertTrue(git_sync["pullEachPass"])
        self.assertFalse(git_sync["publishEachPass"])
        self.assertFalse(git_sync["mergeEachPass"])
        self.assertFalse(git_sync["pushAfterCommit"])
        self.assertFalse(git_sync["openPrOnPush"])

    def test_explicit_runtime_opt_in_preserves_configured_writes(self) -> None:
        os.environ["PPE_GIT_AUTONOMOUS_WRITES"] = "1"
        self.assertTrue(autonomous_git_writes_enabled())
        git_sync = load_operator_config(self.repo)["gitSync"]
        self.assertTrue(git_sync["publishEachPass"])
        self.assertTrue(git_sync["mergeEachPass"])
        self.assertTrue(git_sync["pushAfterCommit"])
        self.assertTrue(git_sync["openPrOnPush"])

    def test_vm_mirror_does_not_commit_without_explicit_opt_in(self) -> None:
        payload = {
            "phase": "CLOSEOUT_PENDING",
            "verdict": "RUN_LOCAL",
            "chapter_name": "chapter",
            "phase_plan_path": "docs/SOP/PHASE_PLANS/chapter.json",
            "recommended_action": "run-local",
        }
        with patch("scripts.ppe_vm_phase_mirror._is_loop_host", return_value=True), patch(
            "scripts.ppe_vm_phase_mirror._git"
        ) as git_mock:
            result = maybe_commit_publish_vm_mirror(self.repo, payload)
        self.assertEqual(result.get("reason"), "autonomous_git_writes_disabled")
        git_mock.assert_not_called()

    def test_new_status_timestamp_alone_does_not_force_heartbeat(self) -> None:
        payload = {
            "as_of": "2026-07-11T18:10:00Z",
            "phase": "BUILD_IN_FLIGHT",
            "verdict": "WAIT",
        }
        prior = {
            "fingerprint": "BUILD_IN_FLIGHT|WAIT|||",
            "last_publish_at": "2026-07-11T18:09:30Z",
            "last_publish_ok": True,
        }
        self.assertFalse(
            _heartbeat_publish_due(
                payload,
                prior,
                fingerprint="BUILD_IN_FLIGHT|WAIT|||",
            )
        )


if __name__ == "__main__":
    unittest.main()
