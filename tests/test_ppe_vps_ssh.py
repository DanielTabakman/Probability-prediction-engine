"""Tests for scripts/ppe_vps_ssh.py (config only; no live SSH)."""

from __future__ import annotations

from unittest import mock

import pytest

from scripts import ppe_vps_ssh as vps


def test_ssh_config_requires_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PPE_VPS_HOST", raising=False)
    monkeypatch.delenv("PPE_VPS_USER", raising=False)
    monkeypatch.delenv("PPE_VPS_SSH_KEY", raising=False)
    with pytest.raises(SystemExit, match="Missing VPS SSH config"):
        vps.ssh_config()


def test_ssh_config_defaults_root(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    key = tmp_path / "id_ed25519"
    key.write_text("fake-key\n", encoding="utf-8")
    monkeypatch.setenv("PPE_VPS_HOST", "203.0.113.1")
    monkeypatch.setenv("PPE_VPS_USER", "ppe")
    monkeypatch.setenv("PPE_VPS_SSH_KEY", str(key))
    monkeypatch.delenv("PPE_VPS_ROOT", raising=False)
    host, user, key_path, root = vps.ssh_config()
    assert host == "203.0.113.1"
    assert user == "ppe"
    assert key_path == str(key)
    assert root == "/opt/marketstructureos"


def test_print_config(capsys, tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    key = tmp_path / "k"
    key.write_text("x", encoding="utf-8")
    monkeypatch.setenv("PPE_VPS_HOST", "h")
    monkeypatch.setenv("PPE_VPS_USER", "u")
    monkeypatch.setenv("PPE_VPS_SSH_KEY", str(key))
    monkeypatch.setenv("PPE_VPS_ROOT", "/opt/foo")
    assert vps.main(["config"]) == 0
    out = capsys.readouterr().out
    assert "host=h" in out
    assert "root=/opt/foo" in out


def test_run_remote_invokes_ssh(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    key = tmp_path / "k"
    key.write_text("x", encoding="utf-8")
    monkeypatch.setenv("PPE_VPS_HOST", "h")
    monkeypatch.setenv("PPE_VPS_USER", "u")
    monkeypatch.setenv("PPE_VPS_SSH_KEY", str(key))

    calls: list[list[str]] = []

    def fake_run(argv, check=False):  # noqa: ANN001
        calls.append(argv)
        return mock.Mock(returncode=0)

    monkeypatch.setattr(vps.subprocess, "run", fake_run)
    vps.run_remote("echo hi")
    assert calls[0][0] == "ssh"
    assert calls[0][-1] == "echo hi"
    assert "-i" in calls[0]
