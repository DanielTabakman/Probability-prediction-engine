"""Tests for auto run_ppe_local trigger."""

from __future__ import annotations

import json
from unittest.mock import patch

from scripts.ppe_auto_run_local import try_auto_run_local


def _status_run_local(plan: str = "docs/SOP/PHASE_PLANS/foo.json") -> dict:
    return {
        "verdict": "RUN_LOCAL",
        "phase_plan_path": plan,
        "guard": {"reason": "IDE_MARKER_OK", "detail": "All product slices marked"},
        "blocker": "IDE product marker present",
    }


def test_auto_run_local_spawns_worker(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_AUTO_RUN_LOCAL", "1")
    sop = tmp_path / "docs" / "SOP"
    sop.mkdir(parents=True)
    (sop / "PPE_AUTO_OPERATOR.local.json").write_text(
        json.dumps({"enabled": True, "autoRunLocal": True}),
        encoding="utf-8",
    )

    with patch("scripts.ppe_auto_run_local.collect_operator_status", return_value=_status_run_local()):
        with patch("scripts.ppe_auto_run_local._active_run_exists", return_value=False):
            with patch("scripts.ppe_auto_run_local.run_local_worker_running", return_value=False):
                with patch(
                    "scripts.ppe_auto_run_local._spawn_run_local_worker",
                    return_value={"started": True, "worker_pid": 999, "plan_path": "docs/SOP/PHASE_PLANS/foo.json"},
                ) as spawn:
                    result = try_auto_run_local(tmp_path)

    assert result.get("started") is True
    spawn.assert_called_once()


def test_auto_run_local_skips_when_disabled(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_AUTO_RUN_LOCAL", "0")
    result = try_auto_run_local(tmp_path)
    assert result.get("skipped") is True
