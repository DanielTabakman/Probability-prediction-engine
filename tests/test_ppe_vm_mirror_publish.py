"""Tests for VM mirror heartbeat publish and off-main worktree publish."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import patch

from scripts.ppe_vm_phase_mirror import (
    IN_FLIGHT_PHASES,
    MIRROR_HEARTBEAT_PUBLISH_SECONDS,
    _heartbeat_publish_due,
    maybe_commit_publish_vm_mirror,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def test_heartbeat_publish_due_in_flight_after_budget() -> None:
    payload = {"phase": "BUILD_IN_FLIGHT", "as_of": _utc_now()}
    prior = {
        "fingerprint": "BUILD_IN_FLIGHT|IDE_BUILD|ch|",
        "last_publish_at": "2020-01-01T00:00:00Z",
        "last_publish_ok": True,
    }
    assert _heartbeat_publish_due(payload, prior, fingerprint=prior["fingerprint"]) is True


def test_heartbeat_publish_retries_after_failed_publish() -> None:
    payload = {"phase": "FINISH_IN_FLIGHT", "as_of": _utc_now()}
    prior = {
        "fingerprint": "FINISH_IN_FLIGHT|RUN_LOCAL|ch|",
        "last_publish_at": _utc_now(),
        "last_publish_ok": False,
    }
    assert _heartbeat_publish_due(payload, prior, fingerprint=prior["fingerprint"]) is True


def test_maybe_commit_publish_records_failed_publish(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PPE_LOOP_HOST", "1")
    (tmp_path / "ppe_operator_loop_host.local.cmd").write_text("@echo off\n", encoding="utf-8")
    mirror = tmp_path / "docs/SOP/VM_OPERATOR_PHASE.json"
    mirror.parent.mkdir(parents=True)
    mirror.write_text(json.dumps({"phase": "BUILD_IN_FLIGHT", "as_of": _utc_now()}) + "\n", encoding="utf-8")
    payload = {
        "phase": "BUILD_IN_FLIGHT",
        "verdict": "IDE_BUILD",
        "chapter_name": "ch",
        "as_of": _utc_now(),
    }
    with patch("scripts.ppe_loop_host_guard.loop_host_start_allowed", return_value=(True, "ok")):
        with patch("scripts.ppe_vm_phase_mirror._git") as mock_git:
            proc_ok = type("P", (), {"returncode": 0, "stdout": "docs/SOP/VM_OPERATOR_PHASE.json", "stderr": ""})()
            mock_git.return_value = proc_ok
            with patch(
                "scripts.ppe_operator_git_sync.publish_vm_mirror_ahead",
                return_value={"ok": False, "error": "push failed"},
            ):
                result = maybe_commit_publish_vm_mirror(tmp_path, payload)
    assert result.get("commit") is True
    state = json.loads((tmp_path / "artifacts/control_plane/VM_MIRROR_PUBLISH_STATE.json").read_text())
    assert state.get("last_publish_ok") is False


def test_in_flight_phases_include_build_and_finish() -> None:
    assert "BUILD_IN_FLIGHT" in IN_FLIGHT_PHASES
    assert MIRROR_HEARTBEAT_PUBLISH_SECONDS >= 300
