"""Tests for ppe_branch_recovery."""

from __future__ import annotations

import subprocess

from scripts.ppe_branch_recovery import (
    classify_scoped_paths,
    recover_branch,
    recovery_ship_command,
    suggest_branch,
)


def test_suggest_branch_control_plane() -> None:
    br = suggest_branch("control", suffix="auto-ship")
    assert br.startswith("control-plane/recovery-auto-ship")


def test_classify_scoped_paths_control(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    scripts = tmp_path / "scripts" / "a.py"
    scripts.parent.mkdir(parents=True)
    scripts.write_text("a\n", encoding="utf-8")
    src = tmp_path / "src" / "b.py"
    src.parent.mkdir(parents=True)
    src.write_text("b\n", encoding="utf-8")

    scoped, outside = classify_scoped_paths(tmp_path, plane="control")
    assert "scripts/a.py" in scoped
    assert "src/b.py" in outside


def test_recover_branch_dry_run(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@test"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True, capture_output=True)
    f = tmp_path / "scripts" / "x.py"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("x\n", encoding="utf-8")

    report = recover_branch(
        tmp_path,
        plane="control",
        branch="control-plane/recovery-test",
        dry_run=True,
    )
    assert report["ok"] is True
    assert report["paths"] == ["scripts/x.py"]


def test_recovery_ship_command() -> None:
    cmd = recovery_ship_command(plane="control", branch="control-plane/foo")
    assert "ppe_branch_recovery.py" in cmd
    assert "--ship" in cmd
