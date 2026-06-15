"""Tests for desktop operator git sync."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scripts.ppe_operator_git_sync import (
    check_and_nudge_merges,
    ensure_main_on_loop_host,
    pull_main,
    publish_ahead,
)


def test_pull_skips_when_dirty(tmp_path: Path) -> None:
    repo = tmp_path
    with patch("scripts.ppe_operator_git_sync.pull_enabled", return_value=True):
        with patch("scripts.ppe_operator_git_sync.ensure_main_on_loop_host", return_value={"skipped": True}):
            with patch("scripts.ppe_operator_git_sync._current_branch", return_value="main"):
                with patch("scripts.ppe_operator_git_sync._dirty_paths", return_value=["scripts/foo.py"]):
                    out = pull_main(repo)
    assert out["skipped"] is True
    assert out["reason"] == "dirty working tree"


def test_ensure_main_stays_on_ops_until_runner_on_origin(tmp_path: Path) -> None:
    repo = tmp_path

    def fake_git(_repo: Path, *args: str):
        if args[:2] == ("fetch", "origin"):
            return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        if args[:2] == ("show", "origin/main:run_ppe_desktop_operator.cmd"):
            return type("P", (), {"returncode": 1, "stdout": "", "stderr": "missing"})()
        return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    with patch("scripts.ppe_operator_git_sync._git_sync_cfg", return_value={"checkoutMainWhenOpsBranch": True, "pullBranch": "main"}):
        with patch("scripts.ppe_operator_git_sync._current_branch", return_value="ops/desktop-operator"):
            with patch("scripts.ppe_operator_git_sync._dirty_paths", return_value=[]):
                with patch("scripts.ppe_operator_git_sync._git", side_effect=fake_git):
                    out = ensure_main_on_loop_host(repo)
    assert out["skipped"] is True
    assert "missing run_ppe_desktop_operator.cmd" in out["reason"]


def test_ensure_main_from_charter_when_clean(tmp_path: Path) -> None:
    repo = tmp_path
    calls: list[list[str]] = []

    def fake_git(_repo: Path, *args: str):
        calls.append(list(args))
        if args[:2] == ("fetch", "origin"):
            return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        if args[:2] == ("show", "origin/main:run_ppe_desktop_operator.cmd"):
            return type("P", (), {"returncode": 0, "stdout": "ok", "stderr": ""})()
        if args[:2] == ("pull", "--ff-only"):
            return type("P", (), {"returncode": 0, "stdout": "Already up to date.", "stderr": ""})()
        return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    with patch("scripts.ppe_operator_git_sync._git_sync_cfg", return_value={"checkoutMainWhenOpsBranch": True, "pullBranch": "main"}):
        with patch("scripts.ppe_operator_git_sync._current_branch", return_value="charter/msos-launch"):
            with patch("scripts.ppe_operator_git_sync._dirty_paths", return_value=[]):
                with patch("scripts.ppe_operator_git_sync._git", side_effect=fake_git):
                    out = ensure_main_on_loop_host(repo)
    assert out.get("checked_out") is True
    assert out.get("ok") is True
    assert any(args[:2] == ["checkout", "main"] for args in calls)


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


def test_check_merge_skips_when_disabled(tmp_path: Path) -> None:
    with patch("scripts.ppe_operator_git_sync.merge_each_pass_enabled", return_value=False):
        out = check_and_nudge_merges(tmp_path)
    assert out["skipped"] is True


def test_check_merge_merges_ready_pr(tmp_path: Path) -> None:
    repo = tmp_path
    pr = {
        "number": 42,
        "headRefName": "ops/loop-publish-abc",
        "mergeable": "MERGEABLE",
        "mergeStateStatus": "CLEAN",
        "isDraft": False,
        "labels": [{"name": "automerge"}],
        "url": "https://github.com/org/repo/pull/42",
    }
    merge_calls: list[list[str]] = []

    def fake_run(args, **kwargs):
        merge_calls.append(list(args))
        return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    with patch("scripts.ppe_operator_git_sync.merge_each_pass_enabled", return_value=True):
        with patch("scripts.ppe_operator_git_sync._gh_available", return_value=True):
            with patch("scripts.ppe_operator_git_sync._gh_json", return_value=[pr]):
                with patch("scripts.ppe_operator_git_sync.pull_enabled", return_value=False):
                    with patch("scripts.ppe_operator_git_sync.subprocess.run", side_effect=fake_run):
                        out = check_and_nudge_merges(repo)
    assert out["ok"] is True
    assert len(out["merged"]) == 1
    assert out["merged"][0]["number"] == 42
    assert any(args[:4] == ["gh", "pr", "merge", "42"] for args in merge_calls)


def test_check_merge_waits_when_ci_pending(tmp_path: Path) -> None:
    pr = {
        "number": 7,
        "headRefName": "ops/test-branch",
        "mergeable": "UNKNOWN",
        "mergeStateStatus": "UNSTABLE",
        "isDraft": False,
        "labels": [{"name": "automerge"}],
        "url": "https://github.com/org/repo/pull/7",
    }
    with patch("scripts.ppe_operator_git_sync.merge_each_pass_enabled", return_value=True):
        with patch("scripts.ppe_operator_git_sync._gh_available", return_value=True):
            with patch("scripts.ppe_operator_git_sync._gh_json", return_value=[pr]):
                with patch("scripts.ppe_operator_git_sync.subprocess.run") as run_mock:
                    out = check_and_nudge_merges(tmp_path)
    assert out["ok"] is True
    assert out["merged"] == []
    assert len(out["pending"]) == 1
    run_mock.assert_not_called()
