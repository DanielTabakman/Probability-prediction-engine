"""Tests for PPE autobuilder status and phase derivation."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_autobuilder import (
    PHASE_AWAITING_BUILD,
    PHASE_BUILD_IN_FLIGHT,
    PHASE_CLOSEOUT_PENDING,
    PHASE_FINISH_IN_FLIGHT,
    PHASE_HEALTHY_IDLE,
    PHASE_RUN_LOCAL_PENDING,
    PHASE_STACK_DOWN,
    STATUS_JSON_REL,
    action_advance,
    collect_autobuilder_status,
    derive_phase,
    format_status_brief,
    write_status_artifact,
)


def _operator_status(**overrides) -> dict:
    base = {
        "verdict": "RUN_AUTO",
        "exit_code": 0,
        "phase_plan_path": "docs/SOP/PHASE_PLANS/test.json",
        "blocker": None,
        "guard": {"reason": "", "detail": ""},
    }
    base.update(overrides)
    return base


def test_derive_phase_stack_down():
    phase = derive_phase(
        operator_status=_operator_status(verdict="RUN_AUTO"),
        stack={"loop_running": False, "watch_running": True},
        build_lock=None,
        closeout={"pending": False},
        finish_worker={"running": False},
        dispatch_degraded=False,
    )
    assert phase == PHASE_STACK_DOWN


def test_derive_phase_awaiting_build():
    phase = derive_phase(
        operator_status=_operator_status(verdict="IDE_BUILD", exit_code=7),
        stack={"loop_running": True, "watch_running": True},
        build_lock=None,
        closeout={"pending": False},
        finish_worker={"running": False},
        dispatch_degraded=False,
    )
    assert phase == PHASE_AWAITING_BUILD


def test_derive_phase_build_in_flight():
    phase = derive_phase(
        operator_status=_operator_status(verdict="IDE_BUILD", exit_code=7),
        stack={"loop_running": True, "watch_running": True},
        build_lock={"slice_id": "MVP1-Slice002"},
        closeout={"pending": False},
        finish_worker={"running": False},
        dispatch_degraded=False,
    )
    assert phase == PHASE_BUILD_IN_FLIGHT


def test_derive_phase_closeout_pending():
    phase = derive_phase(
        operator_status=_operator_status(verdict="IDE_BUILD", exit_code=7),
        stack={"loop_running": True, "watch_running": True},
        build_lock=None,
        closeout={"pending": True},
        finish_worker={"running": False},
        dispatch_degraded=False,
    )
    assert phase == PHASE_CLOSEOUT_PENDING


def test_derive_phase_finish_in_flight():
    phase = derive_phase(
        operator_status=_operator_status(verdict="IDE_BUILD"),
        stack={"loop_running": True, "watch_running": True},
        build_lock=None,
        closeout={"pending": True},
        finish_worker={"running": True},
        dispatch_degraded=False,
    )
    assert phase == PHASE_FINISH_IN_FLIGHT


def test_derive_phase_run_local():
    phase = derive_phase(
        operator_status=_operator_status(verdict="RUN_LOCAL"),
        stack={"loop_running": True, "watch_running": True},
        build_lock=None,
        closeout={"pending": False},
        finish_worker={"running": False},
        dispatch_degraded=False,
    )
    assert phase == PHASE_RUN_LOCAL_PENDING


def test_derive_phase_healthy_idle():
    phase = derive_phase(
        operator_status=_operator_status(verdict="RUN_AUTO"),
        stack={"loop_running": True, "watch_running": True},
        build_lock=None,
        closeout={"pending": False},
        finish_worker={"running": False},
        dispatch_degraded=False,
    )
    assert phase == PHASE_HEALTHY_IDLE


def test_collect_autobuilder_status_writes_json(tmp_path: Path):
    with (
        patch("scripts.ppe_operator_status.collect_operator_status", return_value=_operator_status()),
        patch(
            "scripts.ppe_desktop_operator_stack.stack_status",
            return_value={"loop_running": True, "watch_running": True, "ntfy_listen_running": False},
        ),
        patch("scripts.ppe_autobuilder._build_lock_summary", return_value=None),
        patch(
            "scripts.ppe_autobuilder._resolve_pending_slice",
            return_value={"slice_id": None, "plan_path": None, "starter": None},
        ),
        patch("scripts.ppe_autobuilder._closeout_pending", return_value={"pending": False}),
        patch("scripts.ppe_autobuilder._finish_worker_running", return_value={"running": False}),
        patch(
            "scripts.ppe_autobuilder._dispatch_profile",
            return_value={
                "prefer_ide": False,
                "degraded": False,
                "reason": None,
                "preflight": {"ok": True, "classification": "ready"},
            },
        ),
        patch("scripts.ppe_autobuilder._automation_summary", return_value={"trigger_status": "idle"}),
        patch("scripts.ppe_ide_handoff.load_handoff_state", return_value={}),
        patch("scripts.ppe_ide_product_ready.load_marker", return_value=None),
    ):
        status = collect_autobuilder_status(tmp_path)
        path = write_status_artifact(tmp_path, status)

    assert status["phase"] == PHASE_HEALTHY_IDLE
    assert status["verdict"] == "RUN_AUTO"
    assert "allowed_actions" in status
    assert status["build"]["preflight"]["classification"] == "ready"
    assert path == tmp_path / STATUS_JSON_REL
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["agent"] == "@ppe-autobuilder-operator"


def test_format_status_brief():
    brief = format_status_brief(
        {
            "phase": PHASE_AWAITING_BUILD,
            "verdict": "IDE_BUILD",
            "recommended_action": "retry-build",
            "stack": {"loop_running": True, "watch_running": True},
            "build": {"slice_id": "MVP1-Slice003"},
        }
    )
    assert "PHASE=AWAITING_BUILD" in brief
    assert "MVP1-Slice003" in brief


def test_action_advance_ensure_on_stack_down(tmp_path: Path):
    with (
        patch(
            "scripts.ppe_autobuilder.collect_autobuilder_status",
            return_value={"phase": PHASE_STACK_DOWN, "recommended_action": "ensure"},
        ),
        patch("scripts.ppe_autobuilder.action_ensure", return_value={"action": "ensure", "started": True}) as ensure,
    ):
        result = action_advance(tmp_path)
    ensure.assert_called_once()
    assert result["action"] == "ensure"
