"""Tests for desktop operator git sync."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scripts.ppe_operator_git_sync import pull_main, publish_ahead


def test_pull_skips_when_dirty(tmp_path: Path) -> None:
    repo = tmp_path
    with patch("scripts.ppe_operator_git_sync.pull_enabled", return_value=True):
        with patch("scripts.ppe_operator_git_sync._current_branch", return_value="main"):
            with patch("scripts.ppe_operator_git_sync._dirty_paths", return_value=["scripts/foo.py"]):
                out = pull_main(repo)
    assert out["skipped"] is True
    assert out["reason"] == "dirty working tree"


def test_publish_skips_when_nothing_ahead(tmp_path: Path) -> None:
    repo = tmp_path
    with patch("scripts.ppe_operator_git_sync.push_enabled", return_value=True):
        with patch("scripts.ppe_operator_git_sync._current_branch", return_value="main"):
            with patch("scripts.ppe_operator_git_sync._ahead_count", return_value=0):
                with patch(
                    "scripts.ppe_operator_git_sync._git",
                    return_value=type("P", (), {"returncode": 1, "stdout": "", "stderr": ""})(),
                ):
                    out = publish_ahead(repo)
    assert out["skipped"] is True


def test_publish_main_uses_loop_publish_branch(tmp_path: Path) -> None:
    repo = tmp_path
    calls: list[list[str]] = []

    def fake_git(_repo: Path, *args: str):
        calls.append(list(args))
        return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    with patch("scripts.ppe_operator_git_sync.push_enabled", return_value=True):
        with patch("scripts.ppe_operator_git_sync._current_branch", return_value="main"):
            with patch("scripts.ppe_operator_git_sync._ahead_count", return_value=2):
                with patch("scripts.ppe_operator_git_sync._short_head", return_value="abc1234"):
                    with patch("scripts.ppe_operator_git_sync._git", side_effect=fake_git):
                        with patch("scripts.ppe_operator_git_sync._open_pr", return_value="https://pr"):
                            out = publish_ahead(repo)
    assert out["ok"] is True
    assert any(args[0:2] == ["push", "origin"] for args in calls)
    assert "ops/loop-publish-" in out["pushed_ref"]
