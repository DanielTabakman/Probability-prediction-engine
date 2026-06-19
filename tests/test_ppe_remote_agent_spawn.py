"""Tests for detached remote agent launch and build lock recovery."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.ppe_remote_agent import launch_agent_background
from scripts.ppe_remote_build_agent import (
    BUILD_LOCK_REL,
    BUILD_LOG_REL,
    clear_build_lock,
    is_build_lock_stale,
    launch_build,
    read_build_lock,
    write_build_lock,
)


def test_launch_agent_background_spawns_detached_worker(tmp_path, monkeypatch):
    monkeypatch.setenv("PYTHONPATH", str(tmp_path))
    proc = MagicMock()
    proc.pid = 4242

    with patch("scripts.ppe_remote_agent.agent_available", return_value=True):
        with patch("scripts.ppe_remote_agent.spawn_python_worker", return_value=proc) as spawn:
            out = launch_agent_background(
                tmp_path,
                prompt="build slice",
                log_name="REMOTE_BUILD_AGENT.log",
                started_message="started",
            )

    assert out["started"] is True
    assert out["worker_pid"] == 4242
    spawn.assert_called_once()
    args = spawn.call_args[0]
    assert args[1] == "scripts/ppe_remote_agent_worker.py"
    job_files = list((tmp_path / "artifacts" / "orchestrator").glob("REMOTE_AGENT_JOB_*.json"))
    assert len(job_files) == 1
    job = json.loads(job_files[0].read_text(encoding="utf-8"))
    assert job["prompt"] == "build slice"


def test_stale_build_lock_cleared_when_agent_never_started(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_BUILD_LOCK_STALE_SEC", "30")
    repo = tmp_path
    lock_path = repo / BUILD_LOCK_REL
    log_path = repo / BUILD_LOG_REL
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    old = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    write_build_lock(repo, slice_id="Slice002", plan_path="plan.json", source="test")
    data = json.loads(lock_path.read_text(encoding="utf-8"))
    data["started_at"] = "2020-01-01T00:00:00Z"
    lock_path.write_text(json.dumps(data) + "\n", encoding="utf-8")
    log_path.write_text("remote agent log start 2020-01-01T00:00:00Z\n", encoding="utf-8")

    assert is_build_lock_stale(repo, data) is True
    assert read_build_lock(repo) is None
    assert not lock_path.is_file()


def test_launch_build_records_worker_pid(tmp_path, monkeypatch):
    status = {
        "verdict": "IDE_BUILD",
        "phase_plan_path": "docs/SOP/PHASE_PLANS/foo.json",
        "guard": {"detail": "product [MVP1-Slice002, MVP1-Slice003] blocked"},
        "blocker": "blocked",
    }
    with patch("scripts.ppe_remote_build_agent.collect_operator_status", return_value=status):
        with patch("scripts.ppe_ide_product_ready.next_pending_product_slice", return_value="MVP1-Slice002"):
            with patch("scripts.ppe_remote_build_agent.write_starter"):
                with patch(
                    "scripts.ppe_build_worker.launch_build_worker_background",
                    return_value={"started": True, "worker_pid": 9999, "message": "ok"},
                ):
                    result = launch_build(tmp_path, source="test")

    assert result["started"] is True
    lock = json.loads((tmp_path / BUILD_LOCK_REL).read_text(encoding="utf-8"))
    assert lock["worker_pid"] == 9999

    clear_build_lock(tmp_path)
