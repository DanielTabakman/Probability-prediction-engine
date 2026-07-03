"""Tests for adaptive VM in-flight monitor."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_in_flight_monitor import (
    LOG_TAIL_LINES,
    collect_monitor_snapshot,
    collect_stuck_log_tail,
    compute_next_poll_seconds,
    format_brief,
    run_monitor_pass,
)
from scripts.ppe_vm_phase_mirror import (
    BUILD_IN_FLIGHT_STUCK_SECONDS,
    FINISH_IN_FLIGHT_STUCK_SECONDS,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def test_compute_next_poll_adaptive() -> None:
    assert compute_next_poll_seconds(
        phase="BUILD_IN_FLIGHT",
        elapsed_s=600,
        mirror_stale=False,
        wait_for_vm=True,
    ) == 1800
    assert compute_next_poll_seconds(
        phase="BUILD_IN_FLIGHT",
        elapsed_s=2000,
        mirror_stale=False,
        wait_for_vm=True,
    ) == 600
    assert compute_next_poll_seconds(
        phase="BUILD_IN_FLIGHT",
        elapsed_s=float(BUILD_IN_FLIGHT_STUCK_SECONDS) + 60,
        mirror_stale=False,
        wait_for_vm=True,
    ) == 300
    assert compute_next_poll_seconds(
        phase="FINISH_IN_FLIGHT",
        elapsed_s=3700,
        mirror_stale=False,
        wait_for_vm=True,
    ) == 600
    assert compute_next_poll_seconds(
        phase="FINISH_IN_FLIGHT",
        elapsed_s=float(FINISH_IN_FLIGHT_STUCK_SECONDS) + 60,
        mirror_stale=False,
        wait_for_vm=True,
    ) == 300
    assert compute_next_poll_seconds(
        phase="BUILD_IN_FLIGHT",
        elapsed_s=100,
        mirror_stale=True,
        wait_for_vm=True,
    ) == 60
    assert compute_next_poll_seconds(
        phase="RUN_LOCAL_PENDING",
        elapsed_s=None,
        mirror_stale=False,
        wait_for_vm=False,
    ) == 0


def test_collect_stuck_log_tail(tmp_path: Path) -> None:
    log_path = tmp_path / "artifacts/orchestrator/REMOTE_BUILD_AGENT.log"
    log_path.parent.mkdir(parents=True)
    log_path.write_text("\n".join(f"line-{i}" for i in range(30)) + "\n", encoding="utf-8")
    tail = collect_stuck_log_tail(tmp_path, "BUILD_IN_FLIGHT")
    assert tail is not None
    assert len(tail["lines"]) == LOG_TAIL_LINES
    assert tail["lines"][-1] == "line-29"


def test_collect_snapshot_action_ready(tmp_path, monkeypatch) -> None:
    mirror = {
        "phase": "RUN_LOCAL_PENDING",
        "verdict": "RUN_LOCAL",
        "as_of": _utc_now(),
        "chapter_name": "test_chapter",
    }
    mirror_path = tmp_path / "docs/SOP/VM_OPERATOR_PHASE.json"
    mirror_path.parent.mkdir(parents=True)
    mirror_path.write_text(json.dumps(mirror) + "\n", encoding="utf-8")
    monkeypatch.setattr(
        "scripts.ppe_in_flight_monitor.refresh_vm_mirror_from_git",
        lambda repo, **kw: {"action": "skip_fresh_local"},
    )
    snap = collect_monitor_snapshot(tmp_path, local_verdict="RUN_LOCAL")
    assert snap["wait_for_vm"] is False
    assert snap["done"] is True
    assert snap["completion_action"] == "DESKTOP_CONTINUE.cmd --no-pause"
    assert "action_ready" in snap["status"]


def test_collect_snapshot_watching(tmp_path, monkeypatch) -> None:
    mirror = {
        "phase": "BUILD_IN_FLIGHT",
        "verdict": "IDE_BUILD",
        "as_of": _utc_now(),
    }
    mirror_path = tmp_path / "docs/SOP/VM_OPERATOR_PHASE.json"
    mirror_path.parent.mkdir(parents=True)
    mirror_path.write_text(json.dumps(mirror) + "\n", encoding="utf-8")
    monkeypatch.setattr(
        "scripts.ppe_in_flight_monitor.refresh_vm_mirror_from_git",
        lambda repo, **kw: {"action": "skip_fresh_local"},
    )
    snap = collect_monitor_snapshot(tmp_path, local_verdict="RUN_LOCAL")
    assert snap["wait_for_vm"] is True
    assert snap["done"] is False
    assert snap["next_poll_s"] == 1800


def test_run_monitor_pass_escalates_when_stuck(tmp_path, monkeypatch) -> None:
    mirror = {
        "phase": "BUILD_IN_FLIGHT",
        "verdict": "IDE_BUILD",
        "as_of": _utc_now(),
    }
    mirror_path = tmp_path / "docs/SOP/VM_OPERATOR_PHASE.json"
    mirror_path.parent.mkdir(parents=True)
    mirror_path.write_text(json.dumps(mirror) + "\n", encoding="utf-8")
    state_path = tmp_path / "artifacts/control_plane/IN_FLIGHT_MONITOR_STATE.json"
    state_path.parent.mkdir(parents=True)
    state_path.write_text(
        json.dumps(
            {
                "watch_phase": "BUILD_IN_FLIGHT",
                "watch_started_at": "2020-01-01T00:00:00Z",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "scripts.ppe_in_flight_monitor.refresh_vm_mirror_from_git",
        lambda repo, **kw: {"action": "skip_fresh_local"},
    )
    with patch("scripts.ppe_in_flight_monitor.ssh_vm", return_value={"ok": True, "stdout": "ok"}) as ssh:
        result = run_monitor_pass(tmp_path, local_verdict="RUN_LOCAL", escalate=True)
    assert result["stuck"] is True
    assert result.get("stuck_threshold_m") == 45
    assert result["escalation"]["attempted"] is True
    ssh.assert_called_once()


def test_collect_snapshot_stuck_includes_log_tail(tmp_path, monkeypatch) -> None:
    mirror = {
        "phase": "BUILD_IN_FLIGHT",
        "verdict": "IDE_BUILD",
        "as_of": _utc_now(),
    }
    mirror_path = tmp_path / "docs/SOP/VM_OPERATOR_PHASE.json"
    mirror_path.parent.mkdir(parents=True)
    mirror_path.write_text(json.dumps(mirror) + "\n", encoding="utf-8")
    state_path = tmp_path / "artifacts/control_plane/IN_FLIGHT_MONITOR_STATE.json"
    state_path.parent.mkdir(parents=True)
    state_path.write_text(
        json.dumps(
            {
                "watch_phase": "BUILD_IN_FLIGHT",
                "watch_started_at": "2020-01-01T00:00:00Z",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    log_path = tmp_path / "artifacts/orchestrator/REMOTE_BUILD_AGENT.log"
    log_path.parent.mkdir(parents=True)
    log_path.write_text("agent still running\n", encoding="utf-8")
    monkeypatch.setattr(
        "scripts.ppe_in_flight_monitor.refresh_vm_mirror_from_git",
        lambda repo, **kw: {"action": "skip_fresh_local"},
    )
    snap = collect_monitor_snapshot(tmp_path, local_verdict="RUN_LOCAL")
    assert snap["stuck"] is True
    assert snap.get("log_tail", {}).get("lines") == ["agent still running"]
    assert snap.get("stuck_threshold_m") == 45


def test_collect_snapshot_healthy_idle_no_false_continue(tmp_path, monkeypatch) -> None:
    mirror = {
        "phase": "HEALTHY_IDLE",
        "verdict": "SUPPLY_LOW",
        "as_of": _utc_now(),
    }
    mirror_path = tmp_path / "docs/SOP/VM_OPERATOR_PHASE.json"
    mirror_path.parent.mkdir(parents=True)
    mirror_path.write_text(json.dumps(mirror) + "\n", encoding="utf-8")
    monkeypatch.setattr(
        "scripts.ppe_in_flight_monitor.refresh_vm_mirror_from_git",
        lambda repo, **kw: {"action": "skip_fresh_local"},
    )
    snap = collect_monitor_snapshot(tmp_path, local_verdict="RUN_LOCAL")
    assert snap["wait_for_vm"] is False
    assert snap["completion_action"] is None
    assert snap["status"] == "cleared"


def test_format_brief() -> None:
    line = format_brief(
        {
            "status": "watching",
            "phase": "BUILD_IN_FLIGHT",
            "elapsed_in_phase_m": 12,
            "next_poll_s": 1800,
            "next_poll_m": 30,
            "done": False,
            "message": "Watching.",
        }
    )
    assert "IN_FLIGHT_MONITOR" in line
    assert "next_check=30m" in line


def test_maybe_start_monitor_daemon_skips_loop_host(tmp_path, monkeypatch) -> None:
    from scripts.ppe_in_flight_monitor import maybe_start_monitor_daemon

    monkeypatch.setenv("PPE_LOOP_HOST", "1")
    (tmp_path / "ppe_operator_loop_host.local.cmd").write_text("@echo off\n", encoding="utf-8")
    with patch("scripts.ppe_loop_host_guard.loop_host_start_allowed", return_value=(True, "ok")):
        result = maybe_start_monitor_daemon(tmp_path)
    assert result.get("skipped") is True
