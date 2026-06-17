"""Tests for operator Desktop shortcut installer."""

from __future__ import annotations

from pathlib import Path

from scripts.ppe_operator_shortcuts import (
    detect_role,
    shortcuts_for_role,
    shortcuts_need_refresh,
)


def test_detect_role_vm_loop_host(tmp_path):
    (tmp_path / "ppe_operator_loop_host.local.cmd").write_text(
        'set "PPE_LOOP_HOST=1"\n', encoding="utf-8"
    )
    assert detect_role(tmp_path) == "vm_loop_host"


def test_detect_role_daily_driver(tmp_path):
    (tmp_path / "ppe_operator_no_loop.local.cmd").write_text(
        'set "PPE_STACK_FORBIDDEN=1"\n', encoding="utf-8"
    )
    assert detect_role(tmp_path) == "daily_driver"


def test_shortcuts_for_role_vm():
    names = shortcuts_for_role("vm_loop_host")
    assert "VM STATUS" in names
    assert "DESKTOP BUILD" not in names


def test_shortcuts_need_refresh_when_missing(tmp_path, monkeypatch):
    (tmp_path / "ppe_operator_no_loop.local.cmd").write_text("x\n", encoding="utf-8")
    monkeypatch.setattr(
        "scripts.ppe_operator_shortcuts.desktop_dir",
        lambda: tmp_path / "Desktop",
    )
    assert shortcuts_need_refresh(tmp_path, "daily_driver") is True
