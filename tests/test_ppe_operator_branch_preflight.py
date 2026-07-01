"""Tests for operator branch preflight."""

from __future__ import annotations

from unittest.mock import patch

from scripts.ppe_operator_branch_preflight import assess_operator_branch_preflight


def test_blocks_dirty_src(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        "scripts.ppe_operator_branch_preflight._current_branch",
        lambda repo: "main",
    )
    monkeypatch.setattr(
        "scripts.ppe_operator_branch_preflight._dirty_paths",
        lambda repo: ["src/foo.py"],
    )
    pf = assess_operator_branch_preflight(tmp_path, verdict="RUN_LOCAL", loop_host_allowed=False)
    assert pf["blocks_relay"] is True
    assert any("src/" in r for r in pf["reasons"])
