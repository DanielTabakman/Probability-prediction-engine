"""Safety tests for legacy Autobuilder Git writes and runtime VM state."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_operator_config import autonomous_git_writes_enabled, load_operator_config
from scripts.ppe_vm_phase_mirror import (
    _heartbeat_publish_due,
    load_vm_phase_mirror,
    maybe_commit_publish_vm_mirror,
    mirror_path,
    write_vm_phase_mirror,
)


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
        for key in (
            "PPE_GIT_AUTONOMOUS_WRITES",
            "PPE_ALLOW_LEGACY_GIT_PUBLISH",
            "PPE_OPERATOR_PROFILE",
        ):
            os.environ.pop(key, None)

    def tearDown(self) -> None:
        for key in (
            "PPE_GIT_AUTONOMOUS_WRITES",
            "PPE_ALLOW_LEGACY_GIT_PUBLISH",
            "PPE_OPERATOR_PROFILE",
        ):
            os.environ.pop(key, None)
        self._tmp.cleanup()

    def test_autonomous_git_writes_are_fail_closed_by_default(self) -> None:
        self.assertFalse(autonomous_git_writes_enabled())
        git_sync = load_operator_config(self.repo)["gitSync"]
        self.assertTrue(git_sync["pullEachPass"])
        self.assertFalse(git_sync["publishEachPass"])
        self.assertFalse(git_sync["mergeEachPass"])
        self.assertFalse(git_sync["pushAfterCommit"])
        self.assertFalse(git_sync["openPrOnPush"])

    def test_old_single_flag_no_longer_reenables_legacy_publisher(self) -> None:
        os.environ["PPE_GIT_AUTONOMOUS_WRITES"] = "1"
        self.assertFalse(autonomous_git_writes_enabled())
        self.assertFalse(load_operator_config(self.repo)["gitSync"]["publishEachPass"])

    def test_legacy_publisher_requires_two_part_break_glass(self) -> None:
        os.environ["PPE_GIT_AUTONOMOUS_WRITES"] = "legacy-unsafe"
        self.assertFalse(autonomous_git_writes_enabled())
        os.environ["PPE_ALLOW_LEGACY_GIT_PUBLISH"] = "1"
        self.assertTrue(autonomous_git_writes_enabled())

    def test_vm_mirror_is_never_committed(self) -> None:
        result = maybe_commit_publish_vm_mirror(self.repo, {"phase": "CLOSEOUT_PENDING"})
        self.assertEqual(result.get("reason"), "runtime_state_not_publishable")

    def test_vm_mirror_writes_to_gitignored_runtime_plane(self) -> None:
        status = {
            "as_of": "2026-07-11T18:10:00Z",
            "phase": "BUILD_IN_FLIGHT",
            "verdict": "WAIT",
            "operator": {"chapter_name": "chapter", "phase_plan_path": "plan.json"},
            "recommended_action": "wait",
        }
        with patch("scripts.ppe_vm_phase_mirror._is_loop_host", return_value=True):
            path = write_vm_phase_mirror(self.repo, status)
        self.assertEqual(path, mirror_path(self.repo))
        self.assertIn("artifacts/control_plane", str(path).replace("\\", "/"))
        self.assertEqual(load_vm_phase_mirror(self.repo)["phase"], "BUILD_IN_FLIGHT")
        self.assertFalse((self.repo / "docs" / "SOP" / "VM_OPERATOR_PHASE.json").exists())

    def test_runtime_heartbeat_never_requires_git_publication(self) -> None:
        self.assertFalse(
            _heartbeat_publish_due(
                {"phase": "BUILD_IN_FLIGHT"},
                {"last_publish_ok": False},
                fingerprint="BUILD_IN_FLIGHT|WAIT|||",
            )
        )


if __name__ == "__main__":
    unittest.main()
