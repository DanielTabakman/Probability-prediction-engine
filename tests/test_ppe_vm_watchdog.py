"""Tests for VM watchdog and bootstrap relay heal."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_vm_bootstrap import heal_stale_relay_state, loop_host_git_hygiene
from scripts.ppe_vm_watchdog import check_and_recover


def test_heal_stale_relay_state_resets_missing_result(tmp_path: Path) -> None:
    repo = tmp_path
    state_dir = repo / "artifacts" / "relay" / "state"
    state_dir.mkdir(parents=True)
    (state_dir / "run_state.json").write_text(
        json.dumps({"status": "staged_for_worker", "run_id": "20260101_120000"}),
        encoding="utf-8",
    )
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "relay_runtime_v0.py").write_text("# stub\n", encoding="utf-8")
    with patch("scripts.ppe_vm_bootstrap.subprocess.run") as run_mock:
        run_mock.return_value = type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        out = heal_stale_relay_state(repo)
    assert out["changes"]
    assert run_mock.call_count >= 2


def test_loop_host_git_hygiene_resets_trigger(tmp_path: Path) -> None:
    repo = tmp_path
    trigger = repo / ".cursor" / "IDE_BUILD_TRIGGER.json"
    trigger.parent.mkdir(parents=True)
    trigger.write_text('{"status":"pending"}', encoding="utf-8")
    with patch("scripts.ppe_vm_bootstrap._git") as git_mock:
        git_mock.side_effect = lambda _repo, *args: type(
            "P",
            (),
            {
                "returncode": 0,
                "stdout": " M .cursor/IDE_BUILD_TRIGGER.json\n" if args[:2] == ("status", "--porcelain") else "",
                "stderr": "",
            },
        )()
        out = loop_host_git_hygiene(repo)
    assert "reset .cursor/IDE_BUILD_TRIGGER.json" in out["changes"]


def test_watchdog_restarts_after_threshold(tmp_path: Path) -> None:
    repo = tmp_path
    with patch("scripts.ppe_vm_watchdog._stack_healthy", return_value=(False, {"phase": "STACK_DOWN"})):
        with patch("scripts.ppe_vm_watchdog._run_ensure_stack", return_value={"ok": True, "action": "ensure_stack"}):
            first = check_and_recover(repo, down_threshold=2, cooldown_sec=60, apply=True)
            second = check_and_recover(repo, down_threshold=2, cooldown_sec=60, apply=True)
    assert first.get("restarted") is False
    assert second.get("restarted") is True
