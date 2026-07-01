"""Tests for DESKTOP_CONTINUE canonical runner."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scripts.ppe_desktop_continue import run_desktop_continue


def test_run_desktop_continue_ok(tmp_path: Path) -> None:
    repo = tmp_path

    def fake_pull(_repo: Path):
        return {"action": "pull", "ok": True, "stdout": "Already up to date."}

    def fake_prep(_repo: Path):
        return {"action": "prepare_relay_pull", "ok": True, "skipped": True}

    def fake_ssh(command: str, *, timeout: int = 120):
        if "finish_ide_build" in command:
            return {"ok": True, "exit_code": 0, "stdout": "finish ok", "stderr": ""}
        return {"ok": True, "exit_code": 0, "stdout": "PHASE=IDLE VERDICT=RUN_AUTO slice=-", "stderr": ""}

    with patch("scripts.ppe_operator_branch_preflight.prepare_desktop_relay_pull", side_effect=fake_prep):
        with patch("scripts.ppe_operator_git_sync.pull_main", side_effect=fake_pull):
            with patch("scripts.ppe_operator_vm_ssh.ssh_vm", side_effect=fake_ssh):
                out = run_desktop_continue(repo)
    assert out.get("ok") is True
    assert out.get("vm_finish", {}).get("ok") is True
