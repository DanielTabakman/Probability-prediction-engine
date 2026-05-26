"""Tests for slice touch-set artifact and gate integration."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def touch_plan(tmp_path: Path) -> Path:
    plan = {
        "name": "test_plan",
        "slices": [
            {
                "sliceId": "Test-Product-Slice001",
                "declaredPlane": "PRODUCT-PLANE",
                "touchSet": ["src/viz/app_panels.py", "tests/"],
                "forbiddenTouch": ["src/viz/app.py"],
            }
        ],
    }
    p = tmp_path / "plan.json"
    p.write_text(json.dumps(plan), encoding="utf-8")
    return p


def test_write_slice_touch_set_product(tmp_path: Path, touch_plan: Path):
    from scripts.relay.slice_touch_set import active_touch_set_path, write_active_slice_touch_set

    out = write_active_slice_touch_set(
        tmp_path,
        phase_plan_path=touch_plan,
        slice_id="Test-Product-Slice001",
    )
    assert out == active_touch_set_path(tmp_path)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["touchSet"] == ["src/viz/app_panels.py", "tests"]


def test_write_fails_without_touch_set(tmp_path: Path):
    plan = {
        "slices": [
            {
                "sliceId": "Bad",
                "declaredPlane": "PRODUCT-PLANE",
            }
        ]
    }
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(plan), encoding="utf-8")
    from scripts.relay.slice_touch_set import write_active_slice_touch_set

    with pytest.raises(ValueError, match="touchSet"):
        write_active_slice_touch_set(tmp_path, phase_plan_path=p, slice_id="Bad")


def test_verify_touch_set_outside_fails(tmp_path: Path, touch_plan: Path):
    from scripts.relay.slice_touch_set import write_active_slice_touch_set, verify_active_touch_set

    write_active_slice_touch_set(
        tmp_path,
        phase_plan_path=touch_plan,
        slice_id="Test-Product-Slice001",
    )
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init", "--no-gpg-sign"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        env={**dict(__import__("os").environ), "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"},
    )
    violator = tmp_path / "src" / "other.py"
    violator.parent.mkdir(parents=True, exist_ok=True)
    violator.write_text("x", encoding="utf-8")

    ok, errors = verify_active_touch_set(tmp_path, use_worktree=True)
    assert not ok
    assert errors


def test_pushable_gate_includes_touch_set_when_artifact(tmp_path: Path, touch_plan: Path, monkeypatch):
    from scripts import run_pushable_gate as gate
    from scripts.relay.slice_touch_set import write_active_slice_touch_set

    monkeypatch.setattr(gate, "REPO_ROOT", tmp_path)
    write_active_slice_touch_set(
        tmp_path,
        phase_plan_path=touch_plan,
        slice_id="Test-Product-Slice001",
    )

    plan = gate.classify_paths(("src/viz/app_panels.py",))
    cmds = gate.plan_commands(plan)
    assert any("check_touch_set" in " ".join(c) for c in cmds)


def test_write_slice_touch_set_cli(tmp_path: Path, touch_plan: Path):
    import os

    proc = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "relay" / "write_slice_touch_set.py"),
            "--repo-root",
            str(tmp_path),
            "--phase-plan",
            str(touch_plan),
            "--slice-id",
            "Test-Product-Slice001",
        ],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
    )
    assert proc.returncode == 0, proc.stderr
