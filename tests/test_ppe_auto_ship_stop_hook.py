"""Tests for Cursor stop hook auto-ship reminder."""

from __future__ import annotations

import json
import subprocess
from io import StringIO
from unittest.mock import patch

from scripts.ppe_auto_ship_stop_hook import build_stop_followup, main
from scripts.ppe_worker_lease import LANE_CODEX, acquire_lease


def test_build_stop_followup_skips_when_clean(tmp_path) -> None:
    payload = {"status": "completed", "loop_count": 0}
    assert build_stop_followup(payload, repo=tmp_path) is None


def test_build_stop_followup_with_lease(tmp_path, monkeypatch) -> None:
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

    payload = {"status": "completed", "loop_count": 0, "workspace_roots": [str(tmp_path)]}
    followup = build_stop_followup(payload, repo=tmp_path)
    assert followup is not None
    assert "--ship" in followup


def test_main_emits_json_followup(tmp_path, monkeypatch) -> None:
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

    stdin = json.dumps({"status": "completed", "loop_count": 0, "workspace_roots": [str(tmp_path)]})
    with patch("sys.stdin", StringIO(stdin)):
        with patch("sys.stdout", new_callable=StringIO) as out:
            rc = main()
    assert rc == 0
    data = json.loads(out.getvalue())
    assert "followup_message" in data


def test_main_skips_second_loop(tmp_path) -> None:
    stdin = json.dumps({"status": "completed", "loop_count": 1, "workspace_roots": [str(tmp_path)]})
    with patch("sys.stdin", StringIO(stdin)):
        with patch("sys.stdout", new_callable=StringIO) as out:
            rc = main()
    assert rc == 0
    assert out.getvalue().strip() == "{}"
