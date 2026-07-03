"""Tests for operator dispatch and parked work."""

from __future__ import annotations

import subprocess
from pathlib import Path

from scripts.ppe_operator_dispatch import dispatch_allowed, dispatch_direct_action
from scripts.ppe_parked_work import clear_parked_work, load_parked_work, write_parked_work


def test_dispatch_skipped_without_env(tmp_path: Path) -> None:
    assert not dispatch_allowed()
    report = dispatch_direct_action(tmp_path, "branch_recovery", force=False)
    assert report.get("skipped") is True


def test_dispatch_force_unknown_action(tmp_path: Path) -> None:
    report = dispatch_direct_action(tmp_path, "unknown_action", force=True)
    assert report.get("ok") is False


def test_parked_work_roundtrip(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    path = write_parked_work(tmp_path, reason="mixed_plane", thread_role="charter")
    assert path.is_file()
    data = load_parked_work(tmp_path)
    assert data and data.get("reason") == "mixed_plane"
    assert clear_parked_work(tmp_path)
    assert load_parked_work(tmp_path) is None
