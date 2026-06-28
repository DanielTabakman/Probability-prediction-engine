"""Tests for VM remote publish helper."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scripts.ppe_vm_remote_ops import commit_staged_sop


def test_commit_staged_sop_refuses_non_sop_paths(tmp_path: Path) -> None:
    repo = tmp_path
    (repo / "src").mkdir()
    (repo / "src" / "x.py").write_text("x", encoding="utf-8")

    def fake_git(_repo: Path, *args: str):
        if args[:3] == ("diff", "--cached", "--name-only"):
            return type("P", (), {"returncode": 0, "stdout": "src/x.py\n", "stderr": ""})()
        return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    with patch("scripts.ppe_vm_remote_ops._git", side_effect=fake_git):
        out = commit_staged_sop(repo, message="ops: test")
    assert out["skipped"] is True
    assert "docs/SOP" in str(out.get("reason"))
