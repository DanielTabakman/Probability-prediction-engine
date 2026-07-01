"""Tests for VM mirror refresh, branch preflight, pass timebox, stuck watchdog."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import patch

from scripts.ppe_operator_branch_preflight import assess_operator_branch_preflight
from scripts.ppe_operator_pass_timebox import record_operator_session
from scripts.ppe_operator_vm_mirror_refresh import (
    assess_mirror_health,
    mirror_is_populated,
    refresh_vm_mirror_from_git,
)
from scripts.ppe_vm_phase_mirror import (
    maybe_commit_publish_vm_mirror,
    maybe_notify_stuck_in_flight,
    track_in_flight_since,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def test_mirror_is_populated() -> None:
    assert mirror_is_populated({"phase": "FINISH_IN_FLIGHT", "as_of": _utc_now()})
    assert not mirror_is_populated({"phase": None})


def test_assess_mirror_health_stale() -> None:
    health = assess_mirror_health(
        {"phase": "RUN_LOCAL_PENDING", "as_of": "2020-01-01T00:00:00Z"},
        local_verdict="RUN_LOCAL",
    )
    assert health["alert"] is True


def test_refresh_vm_mirror_from_git(tmp_path, monkeypatch) -> None:
    mirror_path = tmp_path / "docs/SOP/VM_OPERATOR_PHASE.json"
    mirror_path.parent.mkdir(parents=True)
    mirror_path.write_text(json.dumps({"phase": None}) + "\n", encoding="utf-8")
    remote = {"phase": "FINISH_IN_FLIGHT", "as_of": _utc_now(), "verdict": "RUN_LOCAL"}
    monkeypatch.setattr(
        "scripts.ppe_operator_vm_mirror_refresh.read_mirror_from_git_ref",
        lambda repo, ref="origin/main": remote,
    )
    monkeypatch.setattr(
        "scripts.ppe_operator_vm_mirror_refresh.maybe_fetch_origin_main",
        lambda repo, force=False: {"fetched": True},
    )
    report = refresh_vm_mirror_from_git(tmp_path)
    assert report["action"] == "updated_from_git"


def test_branch_preflight_blocks_product(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        "scripts.ppe_operator_branch_preflight._current_branch",
        lambda repo: "product/foo",
    )
    monkeypatch.setattr("scripts.ppe_operator_branch_preflight._dirty_paths", lambda repo: [])
    pf = assess_operator_branch_preflight(tmp_path, verdict="RUN_LOCAL", loop_host_allowed=False)
    assert pf["blocks_relay"] is True


def test_operator_session_timebox(tmp_path) -> None:
    status = {"verdict": "RUN_LOCAL", "phase_plan_path": "docs/x.json", "chapter_mode": {"mode": "X"}}
    session_path = tmp_path / "artifacts/control_plane/OPERATOR_SESSION.json"
    session_path.parent.mkdir(parents=True)
    session_path.write_text(
        json.dumps(
            {
                "fingerprint": "RUN_LOCAL|docs/x.json|X",
                "started_at": "2020-01-01T00:00:00Z",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    out = record_operator_session(tmp_path, status)
    assert out["rotate_recommended"] is True


def test_maybe_commit_publish_vm_mirror(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PPE_LOOP_HOST", "1")
    (tmp_path / "ppe_operator_loop_host.local.cmd").write_text("@echo off\n", encoding="utf-8")
    mirror = tmp_path / "docs/SOP/VM_OPERATOR_PHASE.json"
    mirror.parent.mkdir(parents=True)
    mirror.write_text(json.dumps({"phase": "IDLE"}) + "\n", encoding="utf-8")
    payload = {"phase": "FINISH_IN_FLIGHT", "verdict": "RUN_LOCAL", "chapter_name": "ch"}
    with patch("scripts.ppe_loop_host_guard.loop_host_start_allowed", return_value=(True, "ok")):
        with patch("scripts.ppe_vm_phase_mirror._git") as mock_git:
            proc_ok = type("P", (), {"returncode": 0, "stdout": "docs/SOP/VM_OPERATOR_PHASE.json", "stderr": ""})()
            mock_git.return_value = proc_ok
            with patch("scripts.ppe_operator_git_sync.publish_vm_mirror_ahead", return_value={"ok": True}):
                result = maybe_commit_publish_vm_mirror(tmp_path, payload)
    assert result.get("ok") is True


def test_track_in_flight_since(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PPE_LOOP_HOST", "1")
    (tmp_path / "ppe_operator_loop_host.local.cmd").write_text("@echo off\n", encoding="utf-8")
    status = {"phase": "FINISH_IN_FLIGHT", "verdict": "RUN_LOCAL", "operator": {"chapter_name": "t"}}
    with patch("scripts.ppe_loop_host_guard.loop_host_start_allowed", return_value=(True, "ok")):
        state = track_in_flight_since(tmp_path, status)
    assert state is not None


def test_maybe_notify_stuck_in_flight(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PPE_LOOP_HOST", "1")
    (tmp_path / "ppe_operator_loop_host.local.cmd").write_text("@echo off\n", encoding="utf-8")
    since = tmp_path / "artifacts/control_plane/VM_IN_FLIGHT_SINCE.json"
    since.parent.mkdir(parents=True)
    since.write_text(json.dumps({"phase": "FINISH_IN_FLIGHT", "since": "2020-01-01T00:00:00Z"}) + "\n")
    status = {"phase": "FINISH_IN_FLIGHT", "verdict": "RUN_LOCAL", "operator": {"chapter_name": "t"}}
    with patch("scripts.ppe_loop_host_guard.loop_host_start_allowed", return_value=(True, "ok")):
        with patch("scripts.ppe_notify_push.send_ntfy_to_topic", return_value=True) as mock_ntfy:
            assert maybe_notify_stuck_in_flight(tmp_path, status, stuck_seconds=60) is True
    mock_ntfy.assert_called_once()
