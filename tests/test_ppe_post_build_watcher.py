"""Tests for post-build watcher."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_ide_product_ready import write_marker
from scripts.ppe_post_build_watcher import (
    post_build_watcher_enabled,
    try_finish_pending_ide_build,
)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


class TestPpePostBuildWatcher(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP" / "PHASE_PLANS"
        sop.mkdir(parents=True)
        self.plan_rel = "docs/SOP/PHASE_PLANS/phase.json"
        (sop / "phase.json").write_text(
            json.dumps(
                {
                    "baselineBranch": "main",
                    "slices": [
                        {"sliceId": "Ch-Product-Slice002"},
                        {"sliceId": "Ch-Product-Slice003"},
                    ],
                }
            ),
            encoding="utf-8",
        )
        (self.repo / "docs" / "SOP" / "PPE_AUTO_OPERATOR.json").write_text(
            json.dumps({"ideHandoff": {"postBuildWatcher": True}}),
            encoding="utf-8",
        )
        (self.repo / "docs" / "SOP" / "ACTIVE_PHASE_MANIFEST.json").write_text(
            json.dumps({"phasePlanPath": self.plan_rel, "status": "READY"}),
            encoding="utf-8",
        )
        _git(self.repo, "init")
        _git(self.repo, "config", "user.email", "test@test")
        _git(self.repo, "config", "user.name", "test")
        (self.repo / "README.md").write_text("x\n", encoding="utf-8")
        _git(self.repo, "add", "README.md", "docs")
        _git(self.repo, "commit", "-m", "init")
        _git(self.repo, "branch", "-M", "main")

    def tearDown(self) -> None:
        os.environ.pop("PPE_POST_BUILD_WATCHER", None)
        self._tmp.cleanup()

    def test_disabled_by_env(self) -> None:
        os.environ["PPE_POST_BUILD_WATCHER"] = "0"
        self.assertFalse(post_build_watcher_enabled(self.repo))

    @patch("scripts.ppe_post_build_watcher._spawn_finish_worker")
    def test_finish_when_branch_has_commits(self, spawn: object) -> None:
        spawn.return_value = {"started": True, "worker_pid": 12345, "slice_id": "Ch-Product-Slice002"}
        branch = "build/auto/Ch-Product-Slice002-local"
        _git(self.repo, "checkout", "-b", branch)
        (self.repo / "product.txt").write_text("p\n", encoding="utf-8")
        _git(self.repo, "add", "product.txt")
        _git(self.repo, "commit", "-m", "product")
        _git(self.repo, "checkout", "main")

        result = try_finish_pending_ide_build(self.repo)
        self.assertTrue(result.get("started"))
        assert spawn.called  # type: ignore[attr-defined]

    @patch("scripts.ppe_post_build_watcher._spawn_finish_worker")
    def test_skip_when_no_commits_on_build_branch(self, spawn: object) -> None:
        result = try_finish_pending_ide_build(self.repo)
        self.assertTrue(result.get("skipped"))
        assert not spawn.called  # type: ignore[attr-defined]


if __name__ == "__main__":
    unittest.main()
