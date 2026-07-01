"""Tests for VM mirror refresh, branch preflight, and stuck watchdog."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import patch

from scripts.ppe_operator_branch_preflight import assess_operator_branch_preflight
from scripts.ppe_operator_vm_mirror_refresh import (
    assess_mirror_health,
    mirror_is_populated,
    mirror_is_stale,
    refresh_vm_mirror_from_git,
)
from scripts.ppe_vm_phase_mirror import maybe_notify_stuck_in_flight, track_in_flight_since


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def test_mirror_is_populated() -> None:
    assert mirror_is_populated({"phase": "FINISH_IN_FLIGHT", "as_of": _utc_now()})
    assert not mirror_is_populated({"phase": None, "as_of": None})
    assert not mirror_is_populated(None)


def test_assess_mirror_health_stale() -> None:
    old = {"phase": "RUN_LOCAL_PENDING", "as_of": "2020-01-01T00:00:00Z"}
    health = assess_mirror_health(old, local_verdict="RUN_LOCAL")
    assert health["stale"] is True
    assert health["alert"] is True


def test_refresh_vm_mirror_from_git_updates(tmp_path, monkeypatch) -> None:
    mirror_path = tmp_path / "docs/SOP/VM_OPERATOR_PHASE.json"
    mirror_path.parent.mkdir(parents=True)
    mirror_path.write_text(
        json.dumps({"phase": None, "as_of": None}) + "\n",
        encoding="utf-8",
    )
    remote = {"phase": "FINISH_IN_FLIGHT", "as_of": _utc_now(), "verdict": "RUN_LOCAL"}

    def fake_read(repo, ref="origin/main"):
        return remote

    monkeypatch.setattr("scripts.ppe_operator_vm_mirror_refresh.read_mirror_from_git_ref", fake_read)
    monkeypatch.setattr(
        "scripts.ppe_operator_vm_mirror_refresh.maybe_fetch_origin_main",
        lambda repo, force=False: {"fetched": True},
    )
    report = refresh_vm_mirror_from_git(tmp_path)
    assert report["action"] == "updated_from_git"
    loaded = json.loads(mirror_path.read_text(encoding="utf-8"))
    assert loaded["phase"] == "FINISH_IN_FLIGHT"


def test_branch_preflight_blocks_product_branch(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        "scripts.ppe_operator_branch_preflight._current_branch",
        lambda repo: "product/foo-v1",
    )
    monkeypatch.setattr("scripts.ppe_operator_branch_preflight._dirty_paths", lambda repo: [])
    pf = assess_operator_branch_preflight(tmp_path, verdict="RUN_LOCAL", loop_host_allowed=False)
    assert pf["blocks_relay"] is True


def test_branch_preflight_allows_control_plane(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        "scripts.ppe_operator_branch_preflight._current_branch",
        lambda repo: "control-plane/foo",
    )
    monkeypatch.setattr("scripts.ppe_operator_branch_preflight._dirty_paths", lambda repo: [])
    pf = assess_operator_branch_preflight(tmp_path, verdict="RUN_LOCAL", loop_host_allowed=False)
    assert pf["blocks_relay"] is False


def test_track_in_flight_since(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PPE_LOOP_HOST", "1")
    (tmp_path / "ppe_operator_loop_host.local.cmd").write_text("@echo off\n", encoding="utf-8")
    status = {
        "phase": "FINISH_IN_FLIGHT",
        "verdict": "RUN_LOCAL",
        "operator": {"chapter_name": "test"},
    }
    with patch("scripts.ppe_loop_host_guard.loop_host_start_allowed", return_value=(True, "ok")):
        state = track_in_flight_since(tmp_path, status)
    assert state is not None
    assert state.get("phase") == "FINISH_IN_FLIGHT"


def test_maybe_notify_stuck_in_flight(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PPE_LOOP_HOST", "1")
    (tmp_path / "ppe_operator_loop_host.local.cmd").write_text("@echo off\n", encoding="utf-8")
    since_path = tmp_path / "artifacts/control_plane/VM_IN_FLIGHT_SINCE.json"
    since_path.parent.mkdir(parents=True)
    since_path.write_text(
        json.dumps({"phase": "FINISH_IN_FLIGHT", "since": "2020-01-01T00:00:00Z"}) + "\n",
        encoding="utf-8",
    )
    status = {
        "phase": "FINISH_IN_FLIGHT",
        "verdict": "RUN_LOCAL",
        "operator": {"chapter_name": "test"},
    }
    with patch("scripts.ppe_loop_host_guard.loop_host_start_allowed", return_value=(True, "ok")):
        with patch("scripts.ppe_notify_push.send_ntfy", return_value=True) as mock_ntfy:
            sent = maybe_notify_stuck_in_flight(tmp_path, status, stuck_seconds=60)
    assert sent is True
    mock_ntfy.assert_called_once()
