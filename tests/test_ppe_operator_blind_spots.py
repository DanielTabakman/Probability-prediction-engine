"""Tests for operator blind spots and VM host health."""

from __future__ import annotations

import json
from unittest.mock import patch

from scripts.check_vm_host_health import check_local_disk_health, collect_host_health
from scripts.ppe_operator_blind_spots import assess_operator_blind_spots, format_blind_spot_lines
from scripts.ppe_notify_push import ntfy_topic_stuck


def test_ntfy_topic_stuck_fallback(monkeypatch) -> None:
    monkeypatch.delenv("PPE_NTFY_TOPIC_STUCK", raising=False)
    monkeypatch.setenv("PPE_NTFY_TOPIC", "main-topic")
    assert ntfy_topic_stuck() == "main-topic"
    monkeypatch.setenv("PPE_NTFY_TOPIC_STUCK", "stuck-topic")
    assert ntfy_topic_stuck() == "stuck-topic"


def test_check_local_disk_health() -> None:
    disk = check_local_disk_health()
    assert disk["level"] in ("ok", "warn", "critical")
    assert disk["free_gb"] >= 0


def test_assess_blind_spots_gh_missing(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("PPE_NTFY_TOPIC", raising=False)
    with patch("scripts.ppe_operator_blind_spots._gh_auth_ok", return_value=(False, "not logged in")):
        with patch("scripts.ppe_operator_blind_spots._open_vm_mirror_prs", return_value=[]):
            blind = assess_operator_blind_spots(tmp_path, {"verdict": "RUN_LOCAL"})
    ids = {i["id"] for i in blind.get("issues") or []}
    assert "gh_auth" in ids


def test_assess_blind_spots_mirror_stale(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PPE_NTFY_TOPIC", "t")
    status = {
        "verdict": "RUN_LOCAL",
        "vm_mirror_health": {
            "alert": True,
            "agent_note": "VM mirror stale (45m old)",
            "stale": True,
            "populated": True,
        },
    }
    with patch("scripts.ppe_operator_blind_spots._gh_auth_ok", return_value=(True, "")):
        with patch("scripts.ppe_operator_blind_spots._open_vm_mirror_prs", return_value=[]):
            blind = assess_operator_blind_spots(tmp_path, status)
    ids = {i["id"] for i in blind.get("issues") or []}
    assert "vm_mirror_stale" in ids


def test_format_blind_spot_lines() -> None:
    payload = {
        "operator_health_line": "health: gh=ok ntfy=off spots=1",
        "issues": [{"severity": "high", "message": "test issue"}],
    }
    lines = format_blind_spot_lines(payload)
    assert any("Blind spots" in line for line in lines)


def test_collect_host_health_local(tmp_path) -> None:
    payload = collect_host_health(tmp_path, via_ssh=False)
    assert "disk" in payload
    assert "healthy" in payload
