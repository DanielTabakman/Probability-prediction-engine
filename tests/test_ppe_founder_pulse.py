"""Tests for founder collaboration pulse layers."""

from __future__ import annotations

from pathlib import Path

from scripts.ppe_founder_pulse import (
    assess_alert,
    build_completion_pulse,
    build_morning_pulse,
    load_charter,
)

REPO = Path(__file__).resolve().parents[1]


def test_charter_json_loads() -> None:
    data = load_charter(REPO)
    assert data.get("version") == 1
    assert "layers" in data


def test_morning_pulse_shape() -> None:
    status = {"verdict": "RUN_LOCAL", "chapter_name": "test_chapter", "chapter_mode": {"mode": "CLOSEOUT_ONLY"}}
    pulse = build_morning_pulse(REPO, status)
    assert pulse["layer"] == "morning"
    assert "Good morning" in pulse["body"]
    assert pulse["founder_role"] == "listen"


def test_completion_pulse_closing() -> None:
    status = {"verdict": "RUN_LOCAL", "chapter_name": "test_chapter", "chapter_mode": {"mode": "CLOSEOUT_ONLY"}}
    pulse = build_completion_pulse(REPO, status, slice_id="TEST-Slice001")
    assert pulse["layer"] == "completion"
    assert "Nothing required from you." in pulse["body"]
    assert "TEST-Slice001" in pulse["body"]


def test_alert_on_supply_low_without_candidate() -> None:
    status = {
        "verdict": "SUPPLY_LOW",
        "blocker": "no READY items in queue",
        "chapter_name": "idle",
        "chapter_mode": {},
    }
    coord = {"verdict": "proceed", "blocks_build": False, "delegation_tier": "auto"}
    alert = assess_alert(REPO, status, coord)
    assert alert is not None
    assert alert["layer"] == "alert"
    assert "Decision needed" in alert["body"]


def test_no_alert_when_vm_active() -> None:
    status = {
        "verdict": "IDE_BUILD",
        "chapter_mode": {"mode": "CLOSEOUT_ONLY"},
        "vm_phase": {"phase": "BUILD_IN_FLIGHT"},
    }
    coord = {
        "verdict": "recovery",
        "blocks_build": True,
        "chapter_issues": [{"code": "PRODUCT_ON_MAIN_NO_MARKER", "severity": "high"}],
        "delegation_tier": "auto",
    }
    alert = assess_alert(REPO, status, coord)
    assert alert is None
