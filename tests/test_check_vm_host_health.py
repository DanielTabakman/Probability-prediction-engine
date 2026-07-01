"""Tests for VM host health probes."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scripts.check_vm_host_health import check_vm_host_health_via_ssh


def test_vm_health_ssh_parses_python_json(tmp_path: Path) -> None:
    payload = (
        '{"as_of":"2026-01-01T00:00:00Z","disk":{"free_gb":40.0,"total_gb":120.0,"level":"ok"},'
        '"ram":{"free_gb":8.0,"total_gb":16.0,"free_pct":50.0,"level":"ok"}}'
    )

    def fake_ssh(command: str, *, timeout: int = 30):
        assert "check_vm_host_health.py" in command
        assert "powershell" not in command.lower()
        return {"ok": True, "stdout": payload, "stderr": ""}

    with patch("scripts.ppe_operator_vm_ssh.ssh_vm", side_effect=fake_ssh):
        out = check_vm_host_health_via_ssh(tmp_path)
    assert out.get("ok") is True
    assert out["disk"]["free_gb"] == 40.0
    assert out["ram"]["free_pct"] == 50.0
