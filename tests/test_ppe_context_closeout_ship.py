"""Tests for context closeout auto-ship sweep."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scripts.ppe_context_closeout_ship import (
    committable_dirty_paths,
    is_commit_excluded,
    run_operational_sweep,
)


def test_is_commit_excluded() -> None:
    assert is_commit_excluded("artifacts/orchestrator/x.json")
    assert is_commit_excluded(".env")
    assert not is_commit_excluded("docs/SOP/HANDOFF.md")
    assert not is_commit_excluded("scripts/foo.py")


def test_committable_dirty_paths_filters_exempt(tmp_path: Path) -> None:
    repo = tmp_path
    with patch(
        "scripts.repo_layer_paths.git_dirty_paths",
        return_value=["artifacts/x", "docs/SOP/a.md", ".env"],
    ):
        out = committable_dirty_paths(repo)
    assert out == ["docs/SOP/a.md"]


def test_sweep_clean_tree_publish_ahead(tmp_path: Path) -> None:
    repo = tmp_path
    pf = {"branch": "ops/foo", "working_tree": "clean", "blocker": None}
    with patch("scripts.ppe_context_closeout_ship._preflight", return_value=pf):
        with patch("scripts.ppe_context_closeout_ship.committable_dirty_paths", return_value=[]):
            with patch("scripts.ppe_operator_git_sync._current_branch", return_value="ops/foo"):
                with patch("scripts.ppe_operator_git_sync._ahead_count", return_value=2):
                    with patch(
                        "scripts.ppe_operator_git_sync.publish_ahead",
                        return_value={"action": "push", "ok": True, "pr_url": "https://example/pr/1"},
                    ):
                        with patch(
                            "scripts.ppe_context_closeout_ship._label_automerge",
                            return_value=(True, "labeled"),
                        ):
                            out = run_operational_sweep(repo)
    assert out["ok"] is True
    assert any(s.get("step") == "publish_ahead" for s in out["steps"])


def test_sweep_mixed_plane_parks(tmp_path: Path) -> None:
    repo = tmp_path
    pf = {
        "branch": "main",
        "working_tree": "dirty",
        "blocker": "mixed-plane dirty state",
        "mixed_plane_dirty": True,
    }
    with patch("scripts.ppe_context_closeout_ship._preflight", return_value=pf):
        with patch(
            "scripts.ppe_context_closeout_ship.committable_dirty_paths",
            return_value=["docs/SOP/a.md", "src/b.py"],
        ):
            with patch("scripts.ppe_context_closeout_ship._git", return_value=type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()):
                out = run_operational_sweep(repo)
    assert out["blocked"] is True
    assert out["parked"]


def test_sweep_dry_run_reports_paths(tmp_path: Path) -> None:
    repo = tmp_path
    pf = {"branch": "main", "working_tree": "dirty", "blocker": None, "mixed_plane_dirty": False}
    paths = ["docs/SOP/x.md"]
    with patch("scripts.ppe_context_closeout_ship._preflight", return_value=pf):
        with patch("scripts.ppe_context_closeout_ship.committable_dirty_paths", return_value=paths):
            with patch("scripts.ppe_context_closeout_ship._git", return_value=type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()):
                out = run_operational_sweep(repo, dry_run=True)
    assert out["ok"] is True
    ship = next(s for s in out["steps"] if s.get("step") == "ship")
    assert ship.get("paths") == paths
