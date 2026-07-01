"""Tests for ppe_worker_lease multi-agent lease routing."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from scripts.ppe_worker_lease import (
    LANE_CODEX,
    LANE_CURSOR,
    LANE_VM,
    acquire_lease,
    assess_worker_lease,
    build_work_dispatch,
    infer_worker_events,
    path_matches_any,
    prefer_build_lane,
    release_lease,
    scoped_dirty_paths,
    ship_lease_work,
    suggest_lane,
)


def test_path_matches_glob() -> None:
    assert path_matches_any("scripts/foo.py", ["scripts/**"])
    assert not path_matches_any("src/foo.py", ["scripts/**"])


def test_suggest_lane_control_plane_branch() -> None:
    assert suggest_lane(verdict="IDE_BUILD", branch="control-plane/foo", closeout_only=False, loop_host_allowed=False) == LANE_CODEX


def test_prefer_build_lane_product_scope(tmp_path) -> None:
    with patch("scripts.ppe_worker_lease._cost_lane_counts", return_value={"codex-cli": 0, "acp": 5}):
        out = prefer_build_lane(
            tmp_path,
            verdict="IDE_BUILD",
            branch="main",
            closeout_only=False,
            path_globs=["src/**"],
        )
    assert out["preferred_lane"] == LANE_CURSOR
    assert out["reason"] == "product_path_scope"


def test_prefer_build_lane_cost_usd_codex(tmp_path) -> None:
    def _est_usd(_registry: object, worker_id: str, _est: object) -> float:
        return 2.0 if worker_id == LANE_CODEX else 2.5

    with (
        patch("scripts.ppe_worker_lease._cost_lane_counts", return_value={"codex-cli": 0, "cursor-cli": 0}),
        patch("scripts.ppe_worker_lease._worker_lane_est_usd", side_effect=_est_usd),
    ):
        out = prefer_build_lane(
            tmp_path,
            verdict="IDE_BUILD",
            branch="control-plane/foo",
            closeout_only=False,
            path_globs=["scripts/**"],
        )
    assert out["preferred_lane"] == LANE_CODEX
    assert out["reason"] == "cost_usd_prefer_codex"
    assert "cost_est_usd" in out


def test_prefer_build_lane_cost_codex(tmp_path) -> None:
    with patch("scripts.ppe_worker_lease._cost_lane_counts", return_value={"codex-cli": 2, "cursor-cli": 10, "acp": 5}):
        out = prefer_build_lane(
            tmp_path,
            verdict="IDE_BUILD",
            branch="control-plane/foo",
            closeout_only=False,
        )
    assert out["preferred_lane"] == LANE_CODEX
    assert out["reason"] in ("branch_heuristic", "cost_prefer_codex")


def test_assess_branch_mismatch_blocks(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    now = datetime.now(timezone.utc)
    lease = {
        "lease_id": "lease-test",
        "worker_id": LANE_CODEX,
        "branch": "control-plane/other",
        "exclusive": True,
        "path_globs": ["scripts/**"],
        "forbidden_globs": [],
        "expires_at": (now + timedelta(hours=1)).isoformat().replace("+00:00", "Z"),
    }
    path = tmp_path / "artifacts/control_plane/ACTIVE_LEASE.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(lease) + "\n", encoding="utf-8")

    status = {"verdict": "IDE_BUILD", "chapter_mode": {"mode": "IDE_BUILD"}}
    out = assess_worker_lease(tmp_path, status)
    assert out["blocks_dispatch"] is True


def test_acquire_and_release_lease(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    lease = acquire_lease(
        tmp_path,
        worker_id=LANE_CODEX,
        branch="control-plane/test",
        path_globs=["scripts/**"],
        forbidden_globs=["src/**"],
    )
    assert lease["worker_id"] == LANE_CODEX
    assert release_lease(tmp_path) is True


def test_closeout_only_dirty_src_blocks(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@test"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True, capture_output=True)
    src = tmp_path / "src" / "foo.py"
    src.parent.mkdir(parents=True)
    src.write_text("# dirty\n", encoding="utf-8")

    status = {"verdict": "RUN_LOCAL", "chapter_mode": {"mode": "CLOSEOUT_ONLY", "do_not_rebuild": True}}
    out = assess_worker_lease(tmp_path, status)
    assert out["blocks_dispatch"] is True


def test_infer_worker_events_dirty(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@test"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True, capture_output=True)
    f = tmp_path / "scripts" / "x.py"
    f.parent.mkdir(parents=True)
    f.write_text("x\n", encoding="utf-8")

    payload = infer_worker_events(tmp_path, {"verdict": "IDE_BUILD", "chapter_mode": {"mode": "IDE_BUILD"}})
    kinds = [e.get("event") for e in payload.get("events") or []]
    assert "dirty_tree" in kinds


def test_build_work_dispatch_shape(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    status = {
        "verdict": "IDE_BUILD",
        "chapter_mode": {"mode": "IDE_BUILD"},
        "guard": {"detail": "blocked [Slice-A]"},
    }
    dispatch = build_work_dispatch(tmp_path, status)
    assert dispatch["lane"]["worker_id"] == LANE_CURSOR
    assert dispatch["lane"].get("preference_reason")
    assert "ship" in dispatch["acceptance"]


def test_scoped_dirty_paths_respects_globs(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@test"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True, capture_output=True)
    scripts = tmp_path / "scripts" / "a.py"
    scripts.parent.mkdir(parents=True)
    scripts.write_text("a\n", encoding="utf-8")
    src = tmp_path / "src" / "b.py"
    src.parent.mkdir(parents=True)
    src.write_text("b\n", encoding="utf-8")

    scoped = scoped_dirty_paths(tmp_path, path_globs=["scripts/**"], forbidden_globs=["src/**"])
    assert "scripts/a.py" in scoped
    assert "src/b.py" not in scoped


def test_operator_ship_hint_with_active_lease(tmp_path, monkeypatch) -> None:
    from scripts.ppe_worker_lease import operator_ship_hint

    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@test"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True, capture_output=True)
    acquire_lease(
        tmp_path,
        worker_id=LANE_CODEX,
        branch="control-plane/test",
        path_globs=["scripts/**"],
    )
    f = tmp_path / "scripts" / "x.py"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("x\n", encoding="utf-8")

    hint = operator_ship_hint(tmp_path)
    assert hint == "python scripts/ppe_worker_lease.py --ship --release"


def test_ship_lease_work_dry_run(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@test"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True, capture_output=True)
    acquire_lease(
        tmp_path,
        worker_id=LANE_CODEX,
        branch="control-plane/test",
        path_globs=["scripts/**"],
    )
    f = tmp_path / "scripts" / "x.py"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("x\n", encoding="utf-8")

    report = ship_lease_work(tmp_path, dry_run=True)
    assert report["ok"] is True
    assert report["paths"] == ["scripts/x.py"]
    assert "lease ship" in report["message"]
