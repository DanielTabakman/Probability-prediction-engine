"""Tests for desktop operator git sync."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scripts.ppe_operator_git_sync import (
    check_and_nudge_merges,
    ensure_main_on_loop_host,
    prepare_loop_host_for_handoff,
    pull_main,
    publish_ahead,
)


def test_pull_allows_preflight_exempt_dirty(tmp_path: Path) -> None:
    repo = tmp_path

    def fake_git(_repo: Path, *args: str):
        if args[:2] == ("status", "--porcelain"):
            return type("P", (), {"returncode": 0, "stdout": " M .cursor/IDE_BUILD_TRIGGER.json\n", "stderr": ""})()
        if args[:2] == ("fetch", "origin"):
            return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        if args[:2] == ("pull", "--ff-only"):
            return type("P", (), {"returncode": 0, "stdout": "Already up to date.", "stderr": ""})()
        return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    with patch("scripts.ppe_operator_git_sync.pull_enabled", return_value=True):
        with patch("scripts.ppe_operator_git_sync.ensure_main_on_loop_host", return_value={"skipped": True}):
            with patch("scripts.ppe_operator_git_sync._current_branch", return_value="main"):
                with patch("scripts.ppe_operator_git_sync._git", side_effect=fake_git):
                    out = pull_main(repo)
    assert out.get("ok") is True
    assert out.get("skipped") is not True


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


def test_prepare_handoff_resets_transient_build_branch(tmp_path: Path) -> None:
    repo = tmp_path
    calls: list[list[str]] = []

    def fake_git(_repo: Path, *args: str):
        calls.append(list(args))
        if args[:2] == ("status", "--porcelain"):
            return type(
                "P",
                (),
                {
                    "returncode": 0,
                    "stdout": " M docs/SOP/PHASE_QUEUE.json\n M docs/SOP/HANDOFF.md\n",
                    "stderr": "",
                },
            )()
        if args[:2] in (("fetch", "origin"), ("pull", "--ff-only")):
            return type("P", (), {"returncode": 0, "stdout": "ok", "stderr": ""})()
        if args[:3] == ["checkout", "origin/main", "--"]:
            return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        if args[:2] == ("checkout", "-f") or args[:2] == ("checkout", "main"):
            return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        if args[:2] == ("reset", "--hard"):
            return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    with patch("scripts.ppe_operator_git_sync._git_sync_cfg", return_value={"pullBranch": "main"}):
        with patch("scripts.ppe_operator_git_sync._current_branch", return_value="build/auto/MSOS-FCR-Product-Slice002"):
            with patch("scripts.ppe_operator_git_sync._git_operation_in_progress", return_value=False):
                with patch("scripts.ppe_operator_git_sync._git", side_effect=fake_git):
                    out = prepare_loop_host_for_handoff(repo)
    assert out.get("ok") is True
    assert any(args[:2] == ["reset", "--hard"] for args in calls)
    assert any(args[:2] == ["pull", "--ff-only"] for args in calls)


def test_prepare_handoff_aborts_merge_before_pull(tmp_path: Path) -> None:
    repo = tmp_path
    calls: list[list[str]] = []

    def fake_git(_repo: Path, *args: str):
        calls.append(list(args))
        if args[:2] == ("merge", "--abort"):
            return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        if args[:2] in (("fetch", "origin"), ("pull", "--ff-only")):
            return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    with patch("scripts.ppe_operator_git_sync._git_sync_cfg", return_value={"pullBranch": "main"}):
        with patch("scripts.ppe_operator_git_sync._current_branch", return_value="main"):
            with patch("scripts.ppe_operator_git_sync._git_operation_in_progress", return_value=True):
                with patch("scripts.ppe_operator_git_sync._dirty_paths", return_value=[]):
                    with patch(
                        "scripts.ppe_operator_git_sync.reset_runtime_sop_drift_from_origin",
                        return_value={"changes": []},
                    ):
                        with patch("scripts.ppe_operator_git_sync._git", side_effect=fake_git):
                            out = prepare_loop_host_for_handoff(repo)
    assert out.get("ok") is True
    assert any(args[:2] == ["merge", "--abort"] for args in calls)


def test_vm_finish_command_uses_prepare_handoff() -> None:
    from scripts.ppe_operator_vm_ssh import vm_finish_command

    cmd = vm_finish_command(pull_main=True)
    assert "ppe_vm_handoff_preflight.py" in cmd
    assert "finish_ide_build.cmd" in cmd
    assert "--prepare-handoff" not in cmd


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


def test_publish_reports_timeout(tmp_path: Path) -> None:
    repo = tmp_path

    def fake_git(_repo: Path, *args: str):
        if args[:2] == ("push", "origin"):
            return type(
                "P",
                (),
                {"returncode": 124, "stdout": "", "stderr": "command timed out after 120s"},
            )()
        return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    with patch("scripts.ppe_operator_git_sync.push_enabled", return_value=True):
        with patch("scripts.ppe_operator_git_sync._current_branch", return_value="main"):
            with patch("scripts.ppe_operator_git_sync._ahead_count", return_value=1):
                with patch("scripts.ppe_operator_git_sync._short_head", return_value="abc1234"):
                    with patch("scripts.ppe_operator_git_sync._git", side_effect=fake_git):
                        out = publish_ahead(repo)
    assert out["ok"] is False
    assert out.get("timed_out") is True


def test_vm_mirror_head_eligible_for_automerge() -> None:
    from scripts.ppe_operator_git_sync import VM_MIRROR_PUBLISH_PREFIX, _head_eligible_for_automerge

    head = f"{VM_MIRROR_PUBLISH_PREFIX}20260101120000-abc1234"
    assert _head_eligible_for_automerge(head, {}) is True


def test_publish_vm_mirror_ahead_opens_pr(tmp_path: Path) -> None:
    repo = tmp_path
    calls: list[list[str]] = []

    def fake_git(_repo: Path, *args: str):
        calls.append(list(args))
        if args[:2] == ("push", "origin"):
            return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    with patch("scripts.ppe_operator_git_sync.push_enabled", return_value=True):
        with patch("scripts.ppe_operator_git_sync._current_branch", return_value="main"):
            with patch("scripts.ppe_operator_git_sync._ahead_count", return_value=1):
                with patch("scripts.ppe_operator_git_sync._short_head", return_value="abc1234"):
                    with patch("scripts.ppe_operator_git_sync._git", side_effect=fake_git):
                        with patch(
                            "scripts.ppe_operator_git_sync._open_pr",
                            return_value="https://github.com/example/pr/1",
                        ) as open_pr:
                            from scripts.ppe_operator_git_sync import publish_vm_mirror_ahead

                            out = publish_vm_mirror_ahead(repo, phase="FINISH_IN_FLIGHT")
    assert out["ok"] is True
    assert out.get("mirror_only") is True
    open_pr.assert_called_once()
    assert open_pr.call_args.kwargs.get("labels") == ["automerge"]
