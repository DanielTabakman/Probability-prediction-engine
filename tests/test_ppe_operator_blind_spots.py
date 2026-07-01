"""Tests for operator blind spots and VM host health."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.check_vm_host_health import check_local_disk_health, collect_host_health
from scripts.ppe_operator_blind_spots import assess_operator_blind_spots, format_blind_spot_lines

try:
    from scripts.ppe_notify_push import bootstrap_operator_notify_env, ntfy_configured, ntfy_topic_stuck
except ImportError:
    bootstrap_operator_notify_env = None  # type: ignore[misc, assignment]
    ntfy_configured = None  # type: ignore[misc, assignment]
    ntfy_topic_stuck = None  # type: ignore[misc, assignment]


def test_ntfy_topic_stuck_fallback(monkeypatch) -> None:
    if ntfy_topic_stuck is None:
        pytest.skip("ntfy_topic_stuck removed from ppe_notify_push")
    monkeypatch.delenv("PPE_NTFY_TOPIC_STUCK", raising=False)
    monkeypatch.setenv("PPE_NTFY_TOPIC", "main-topic")
    assert ntfy_topic_stuck() == "main-topic"
    monkeypatch.setenv("PPE_NTFY_TOPIC_STUCK", "stuck-topic")
    assert ntfy_topic_stuck() == "stuck-topic"


@pytest.mark.skipif(sys.platform != "win32", reason="bootstrap_operator_notify_env uses cmd.exe")
def test_bootstrap_loads_notify_local_cmd(tmp_path: Path, monkeypatch) -> None:
    if bootstrap_operator_notify_env is None or ntfy_configured is None:
        pytest.skip("bootstrap_operator_notify_env removed from ppe_notify_push")
    monkeypatch.delenv("PPE_NTFY_TOPIC", raising=False)
    (tmp_path / "ppe_operator_notify.local.cmd").write_text(
        '@echo off\nset "PPE_NTFY_TOPIC=ppe-test-topic-from-file"\n',
        encoding="utf-8",
    )
    bootstrap_operator_notify_env(tmp_path)
    assert ntfy_configured()
    assert os.environ.get("PPE_NTFY_TOPIC") == "ppe-test-topic-from-file"


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


def test_assess_blind_spots_ignores_layer_scope_info_warning(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PPE_NTFY_TOPIC", "t")
    status = {
        "verdict": "RUN_LOCAL",
        "preflight_warnings": ["repo layer scope: preset='CONTROL' (dirty paths OK)"],
    }
    with patch("scripts.ppe_operator_blind_spots._gh_auth_ok", return_value=(True, "")):
        with patch("scripts.ppe_operator_blind_spots._open_vm_mirror_prs", return_value=[]):
            blind = assess_operator_blind_spots(tmp_path, status)
    ids = {i["id"] for i in blind.get("issues") or []}
    assert "mixed_plane" not in ids


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


def test_check_vm_host_health_ssh_uses_encoded_command() -> None:
    from scripts.check_vm_host_health import _powershell_encoded_command, _vm_host_health_ps_script

    cmd = _powershell_encoded_command(_vm_host_health_ps_script())
    assert "EncodedCommand" in cmd
    assert "$tg" not in cmd
    assert ";" not in cmd.split("EncodedCommand", 1)[1]
