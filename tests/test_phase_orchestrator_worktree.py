"""Worktree baseline fallback when branch is checked out elsewhere."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.phase_orchestrator_v0 import Orchestrator


class TestPhaseOrchestratorWorktree(unittest.TestCase):
    def test_detach_when_branch_already_used(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
            (repo / "pyproject.toml").write_text("[project]\nname='t'\n", encoding="utf-8")
            subprocess.run(["git", "add", "pyproject.toml"], cwd=repo, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "init"],
                cwd=repo,
                check=True,
                capture_output=True,
            )
            subprocess.run(["git", "checkout", "-b", "dev"], cwd=repo, check=True, capture_output=True)
            holder = repo / "holder"
            subprocess.run(["git", "worktree", "add", str(holder), "main"], cwd=repo, check=True, capture_output=True)

            orch = Orchestrator(repo)
            wt = orch.ensure_worktree(baseline_local="main", build_branch="build/auto/test-slice")
            self.assertTrue(wt.is_dir())
            head = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=wt,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            main_sha = subprocess.run(
                ["git", "rev-parse", "main"],
                cwd=repo,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            self.assertEqual(head, main_sha)


if __name__ == "__main__":
    unittest.main()
