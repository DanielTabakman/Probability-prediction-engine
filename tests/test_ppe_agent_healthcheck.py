"""Tests for scripts/ppe_agent_healthcheck.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.ppe_agent_healthcheck import run_agent_healthcheck


def test_healthcheck_ok_when_status_and_probe_pass(tmp_path: Path):
    def fake_run(argv, *, cwd=None, timeout=None):
        proc = MagicMock()
        if "status" in argv:
            proc.returncode = 0
            proc.stdout = "Logged in as user@example.com"
            proc.stderr = ""
        else:
            proc.returncode = 0
            proc.stdout = "OK"
            proc.stderr = ""
        return proc

    with patch("scripts.ppe_agent_healthcheck._run", side_effect=fake_run):
        with patch("scripts.ppe_agent_healthcheck._network_hint", return_value=[]):
            result = run_agent_healthcheck(tmp_path, skip_probe=False)
    assert result["ok"] is True


def test_healthcheck_fails_on_unavailable_probe(tmp_path: Path):
    def fake_run(argv, *, cwd=None, timeout=None):
        proc = MagicMock()
        if "status" in argv:
            proc.returncode = 0
            proc.stdout = "Logged in"
            proc.stderr = ""
        else:
            proc.returncode = 1
            proc.stdout = ""
            proc.stderr = "Error: [unavailable]"
        return proc

    with patch("scripts.ppe_agent_healthcheck._run", side_effect=fake_run):
        with patch("scripts.ppe_agent_healthcheck._network_hint", return_value=[]):
            result = run_agent_healthcheck(tmp_path, skip_probe=False)
    assert result["ok"] is False
    assert any("unavailable" in e.lower() for e in result["errors"])


def test_healthcheck_fails_when_not_logged_in(tmp_path: Path):
    proc = MagicMock()
    proc.returncode = 0
    proc.stdout = "Please log in"
    proc.stderr = ""

    with patch("scripts.ppe_agent_healthcheck._run", return_value=proc):
        with patch("scripts.ppe_agent_healthcheck._network_hint", return_value=[]):
            result = run_agent_healthcheck(tmp_path, skip_probe=True)
    assert result["ok"] is False
