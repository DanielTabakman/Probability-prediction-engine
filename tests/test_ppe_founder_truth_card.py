"""Tests for founder truth card and FC-2 factory SSOT audit."""

from __future__ import annotations

from pathlib import Path

from scripts.ppe_factory_change_audit import audit_factory_ssot
from scripts.ppe_founder_pulse import assess_alert
from scripts.ppe_operator_dispatch import scheduled_dispatch_allowed
from scripts.ppe_operator_status import (
    assess_founder_posture,
    build_founder_truth_card,
    format_founder_truth_card_lines,
)


def test_founder_posture_kick_on_action_ready() -> None:
    assert assess_founder_posture({"action_ready": True, "verdict": "RUN_LOCAL"}) == "kick"


def test_founder_posture_wait_on_monitor_watching() -> None:
    assert (
        assess_founder_posture(
            {
                "verdict": "RUN_LOCAL",
                "in_flight_monitor": {"status": "watching", "phase": "BUILD_IN_FLIGHT"},
            }
        )
        == "wait"
    )


def test_founder_posture_alert_on_stuck() -> None:
    assert (
        assess_founder_posture(
            {
                "verdict": "RUN_LOCAL",
                "in_flight_monitor": {"status": "stuck", "stuck": True},
            }
        )
        == "alert"
    )


def test_truth_card_lines() -> None:
    status = {
        "verdict": "RUN_LOCAL",
        "vm_trust": {"vm_phase": "BUILD_IN_FLIGHT", "wait_for_vm": True},
        "in_flight_monitor": {
            "status": "watching",
            "phase": "BUILD_IN_FLIGHT",
            "mirror_age_s": 720,
            "next_poll_m": 30,
        },
    }
    lines = format_founder_truth_card_lines(status)
    assert len(lines) == 1
    assert "Truth card" in lines[0]
    assert "posture=wait" in lines[0]
    card = build_founder_truth_card(status)
    assert card["mirror_age_m"] == 12


def test_alert_on_monitor_stuck() -> None:
    status = {
        "verdict": "RUN_LOCAL",
        "vm_phase": {"phase": "BUILD_IN_FLIGHT"},
        "in_flight_monitor": {"stuck": True, "phase": "BUILD_IN_FLIGHT", "elapsed_in_phase_m": 120},
    }
    coord = {"verdict": "proceed", "blocks_build": False, "delegation_tier": "auto"}
    alert = assess_alert(Path("."), status, coord)
    assert alert is not None
    assert "stuck" in alert["body"].lower()


def test_factory_ssot_audit_flags_missing_companion() -> None:
    issues = audit_factory_ssot(
        Path("."),
        changed_paths=["scripts/ppe_burst_plan.py"],
    )
    assert any(i.get("trigger") == "scripts/ppe_burst_plan.py" for i in issues)


def test_factory_ssot_audit_ok_with_companion() -> None:
    issues = audit_factory_ssot(
        Path("."),
        changed_paths=["scripts/ppe_burst_plan.py", "tests/test_ppe_burst_plan.py"],
    )
    assert not issues


def test_scheduled_dispatch_requires_opt_in(tmp_path: Path) -> None:
    assert scheduled_dispatch_allowed(tmp_path) is False
    (tmp_path / "ppe_operator_desktop_auto.local.cmd").write_text("@echo off\n", encoding="utf-8")
    assert scheduled_dispatch_allowed(tmp_path) is True
