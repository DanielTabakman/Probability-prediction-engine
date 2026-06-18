"""Worktree baseline fallback when branch is checked out elsewhere."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.phase_orchestrator_v0 import Orchestrator


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [
            "git",
            "-c",
            "user.email=test@example.com",
            "-c",
            "user.name=Test User",
            *args,
        ],
        cwd=cwd,
        capture_output=True,
        check=True,
    )


class TestPhaseOrchestratorWorktree(unittest.TestCase):
    def test_detach_when_branch_already_used(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _git(repo, "init", "-b", "main")
            (repo / "pyproject.toml").write_text("[project]\nname='t'\n", encoding="utf-8")
            _git(repo, "add", "pyproject.toml")
            _git(repo, "commit", "-m", "init")
            _git(repo, "checkout", "-b", "dev")
            holder = repo / "holder"
            _git(repo, "worktree", "add", str(holder), "main")

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

    def test_reuse_refreshes_worktree_to_baseline_tip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _git(repo, "init", "-b", "main")
            (repo / "pyproject.toml").write_text("[project]\nname='t'\n", encoding="utf-8")
            _git(repo, "add", "pyproject.toml")
            _git(repo, "commit", "-m", "init")
            old_sha = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()

            orch = Orchestrator(repo)
            wt = orch.ensure_worktree(baseline_local="main", build_branch="build/auto/reuse-slice")
            self.assertEqual(
                subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=wt,
                    capture_output=True,
                    text=True,
                    check=True,
                ).stdout.strip(),
                old_sha,
            )

            (repo / "README.md").write_text("v2\n", encoding="utf-8")
            _git(repo, "add", "README.md")
            _git(repo, "commit", "-m", "advance main")
            new_sha = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            self.assertNotEqual(old_sha, new_sha)

            wt2 = orch.ensure_worktree(baseline_local="main", build_branch="build/auto/reuse-slice")
            self.assertEqual(wt2, wt)
            head = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=wt,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            self.assertEqual(head, new_sha)

    def test_broken_worktree_is_recreated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _git(repo, "init", "-b", "main")
            (repo / "pyproject.toml").write_text("[project]\nname='t'\n", encoding="utf-8")
            (repo / "tests").mkdir()
            (repo / "tests" / "test_ok.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
            _git(repo, "add", ".")
            _git(repo, "commit", "-m", "init")

            orch = Orchestrator(repo)
            wt = orch.ensure_worktree(baseline_local="main", build_branch="build/auto/broken-slice")
            self.assertTrue((wt / "tests").is_dir())

            for child in list(wt.iterdir()):
                if child.is_dir():
                    import shutil

                    shutil.rmtree(child)
                else:
                    child.unlink()
            (wt / "artifacts").mkdir()

            wt2 = orch.ensure_worktree(baseline_local="main", build_branch="build/auto/broken-slice")
            self.assertEqual(wt2, wt)
            self.assertTrue((wt / "tests" / "test_ok.py").is_file())


if __name__ == "__main__":
    unittest.main()
