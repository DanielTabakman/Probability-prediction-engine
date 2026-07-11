"""Tests for runtime VM state health, branch preflight, timebox, and stuck watchdog."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import patch

from scripts.ppe_operator_branch_preflight import assess_operator_branch_preflight
from scripts.ppe_operator_pass_timebox import record_operator_session
from scripts.ppe_operator_vm_mirror_refresh import (
    assess_mirror_health,
    maybe_sync_desktop_mirror_after_ship,
    mirror_is_populated,
    refresh_vm_mirror_from_git,
    sync_desktop_mirror_from_main,
)
from scripts.ppe_vm_phase_mirror import (
    maybe_commit_publish_vm_mirror,
    maybe_notify_stuck_in_flight,
    track_in_flight_since,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_runtime_state(tmp_path, payload: dict) -> None:
    path = tmp_path / "artifacts/control_plane/VM_OPERATOR_PHASE.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_mirror_is_populated() -> None:
    assert mirror_is_populated({"phase": "FINISH_IN_FLIGHT", "as_of": _utc_now()})
    assert not mirror_is_populated({"phase": None})


def test_assess_mirror_health_stale() -> None:
    health = assess_mirror_health(
        {"phase": "RUN_LOCAL_PENDING", "as_of": "2020-01-01T00:00:00Z"},
        local_verdict="RUN_LOCAL",
    )
    assert health["alert"] is True
    assert health["untrusted"] is True
    assert health["heartbeat_overdue"] is False
    assert "direct status/SSH" in health["agent_note"]


def test_assess_mirror_health_in_flight_not_untrusted() -> None:
    health = assess_mirror_health(
        {"phase": "FINISH_IN_FLIGHT", "as_of": "2020-01-01T00:00:00Z"},
        local_verdict="RUN_LOCAL",
    )
    assert health["stale"] is True
    assert health["untrusted"] is False
    assert health["in_flight"] is True
    assert health["heartbeat_overdue"] is True
    assert health["alert"] is True


def test_sync_desktop_assesses_runtime_state_without_git(tmp_path) -> None:
    _write_runtime_state(tmp_path, {"phase": "IDLE", "as_of": _utc_now()})
    report = sync_desktop_mirror_from_main(tmp_path)
    assert report["ok"] is True
    assert report["health"]["populated"] is True
    assert report["transport"] == "runtime_local"
    assert "pull" not in report
    assert "merge" not in report


def test_maybe_sync_after_ship_is_obsolete(tmp_path) -> None:
    out = maybe_sync_desktop_mirror_after_ship(tmp_path, pre_push=True)
    assert out.get("skipped") is True
    assert out.get("reason") == "runtime_state_not_in_git"


def test_refresh_reads_runtime_state_without_git(tmp_path) -> None:
    _write_runtime_state(
        tmp_path,
        {"phase": "FINISH_IN_FLIGHT", "as_of": _utc_now(), "verdict": "RUN_LOCAL"},
    )
    report = refresh_vm_mirror_from_git(tmp_path)
    assert report["action"] == "runtime_local"
    assert report["local_populated"] is True
    assert report["transport"] == "runtime_local"


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


def test_maybe_commit_publish_vm_mirror_is_permanent_noop(tmp_path) -> None:
    result = maybe_commit_publish_vm_mirror(
        tmp_path,
        {"phase": "FINISH_IN_FLIGHT", "verdict": "RUN_LOCAL", "chapter_name": "ch"},
    )
    assert result == {"skipped": True, "reason": "runtime_state_not_publishable"}


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
