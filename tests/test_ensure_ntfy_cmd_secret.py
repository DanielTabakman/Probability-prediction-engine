"""Tests for ensure_ntfy_cmd_secret."""

from __future__ import annotations

from scripts.ensure_ntfy_cmd_secret import ensure_secret


def test_ensure_secret_appends(tmp_path):
    path = tmp_path / "ppe_operator_notify.local.cmd"
    path.write_text('@echo off\nset "PPE_NTFY_TOPIC=t"\n', encoding="utf-8")
    out = ensure_secret(tmp_path, secret="s3cret")
    assert out["action"] == "appended"
    assert "PPE_NTFY_CMD_SECRET=s3cret" in path.read_text(encoding="utf-8")


def test_ensure_secret_repairs_malformed(tmp_path):
    path = tmp_path / "ppe_operator_notify.local.cmd"
    path.write_text('set "PPE_NTFY_TOPIC=t"\nset  PPE_NTFY_CMD_SECRET=ppe-msos-remote\\\n', encoding="utf-8")
    out = ensure_secret(tmp_path, secret="ppe-msos-remote")
    assert out["action"] == "repaired"
    assert 'set "PPE_NTFY_CMD_SECRET=ppe-msos-remote"' in path.read_text(encoding="utf-8")


def test_ensure_secret_idempotent(tmp_path):
    path = tmp_path / "ppe_operator_notify.local.cmd"
    path.write_text('set "PPE_NTFY_CMD_SECRET=ppe-msos-remote"\n', encoding="utf-8")
    out = ensure_secret(tmp_path)
    assert out["action"] == "already_set"
