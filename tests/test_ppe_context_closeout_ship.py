"""Tests for bounded context closeout publication."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scripts.ppe_context_closeout_ship import (
    committable_dirty_paths,
    infer_chapter_id,
    is_commit_excluded,
    run_operational_sweep,
)


def test_is_commit_excluded() -> None:
    assert is_commit_excluded("artifacts/orchestrator/x.json")
    assert is_commit_excluded(".env")
    assert not is_commit_excluded("docs/SOP/HANDOFF.md")
    assert not is_commit_excluded("scripts/foo.py")


def test_committable_dirty_paths_filters_exempt(tmp_path: Path) -> None:
    with patch(
        "scripts.repo_layer_paths.git_dirty_paths",
        return_value=["artifacts/x", "docs/SOP/a.md", ".env"],
    ):
        out = committable_dirty_paths(tmp_path)
    assert out == ["docs/SOP/a.md"]


def test_infer_chapter_id_prefers_preflight(tmp_path: Path) -> None:
    assert infer_chapter_id(tmp_path, {"chapter_name": "MSOS Demo"}) == "MSOS Demo"


def test_sweep_clean_tree_updates_chapter_pr(tmp_path: Path) -> None:
    pf = {
        "branch": "chapter/demo",
        "working_tree": "clean",
        "blocker": None,
        "chapter_name": "demo",
    }
    with patch("scripts.ppe_context_closeout_ship._preflight", return_value=pf), patch(
        "scripts.ppe_context_closeout_ship.committable_dirty_paths", return_value=[]
    ), patch("scripts.ppe_context_closeout_ship._current_branch", return_value="chapter/demo"), patch(
        "scripts.ppe_context_closeout_ship._ahead_count", return_value=2
    ), patch(
        "scripts.ppe_context_closeout_ship._publish",
        return_value={"ok": True, "action": "updated", "pr_url": "https://example/pr/1"},
    ):
        out = run_operational_sweep(tmp_path)
    assert out["ok"] is True
    assert any(s.get("step") == "chapter_publish" for s in out["steps"])
    assert not any(s.get("step") == "publish_ahead" for s in out["steps"])


def test_sweep_mixed_plane_parks(tmp_path: Path) -> None:
    pf = {
        "branch": "main",
        "working_tree": "dirty",
        "blocker": "mixed-plane dirty state",
        "mixed_plane_dirty": True,
    }
    with patch("scripts.ppe_context_closeout_ship._preflight", return_value=pf), patch(
        "scripts.ppe_context_closeout_ship.committable_dirty_paths",
        return_value=["docs/SOP/a.md", "src/b.py"],
    ):
        out = run_operational_sweep(tmp_path)
    assert out["blocked"] is True
    assert out["parked"]


def test_sweep_dry_run_reports_paths(tmp_path: Path) -> None:
    pf = {
        "branch": "main",
        "working_tree": "dirty",
        "blocker": None,
        "mixed_plane_dirty": False,
        "chapter_name": "demo",
    }
    paths = ["docs/SOP/x.md"]
    with patch("scripts.ppe_context_closeout_ship._preflight", return_value=pf), patch(
        "scripts.ppe_context_closeout_ship.committable_dirty_paths", return_value=paths
    ):
        out = run_operational_sweep(tmp_path, dry_run=True)
    assert out["ok"] is True
    ship = next(s for s in out["steps"] if s.get("step") == "ship")
    assert ship.get("paths") == paths
    assert ship.get("chapter_id") == "demo"
