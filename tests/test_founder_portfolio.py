"""Tests for read-only founder portfolio commands."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CANON = [
    "docs/SOP/CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1.md",
    "docs/SOP/FOUNDER_PIPELINE_COMMANDS_V1.md",
    "docs/SOP/PIPELINE_CREATION_SOP_V1.md",
    "docs/SOP/SCHEDULED_AUTOBUILDER_LANE_POLICY_V1.md",
]


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _minimal_repo(tmp_path: Path) -> Path:
    (tmp_path / "config").mkdir()
    shutil.copyfile(REPO / "config/founder_pipeline_registry.json", tmp_path / "config/founder_pipeline_registry.json")
    for rel in CANON:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# canon\n", encoding="utf-8")
    _write_json(tmp_path / "docs/SOP/ACTIVE_PHASE_MANIFEST.json", {"version": 1, "status": "COMPLETE"})
    _write_json(tmp_path / "docs/SOP/PHASE_QUEUE.json", {"version": 1, "items": []})
    _write_json(tmp_path / "docs/SOP/PHASE_CHAPTER_BACKLOG.json", {"version": 1, "items": []})
    return tmp_path


def _hash_tree(root: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        hashes[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def test_commands_lists_only_founder_vocabulary() -> None:
    from scripts.founder_portfolio import format_commands

    body = format_commands()
    assert "what's next" in body
    assert "what's running" in body
    assert "create pipeline <name>" in body
    assert "scripts/ppe_" not in body
    assert "never dispatches, enqueues, approves, repairs, or writes" in body


def test_whats_next_is_read_only_for_repo_files(tmp_path: Path) -> None:
    repo = _minimal_repo(tmp_path)
    before = _hash_tree(repo)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    proc = subprocess.run(
        [sys.executable, str(REPO / "scripts/founder_portfolio.py"), "whats-next", "--json", "--repo-root", str(repo)],
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    after = _hash_tree(repo)
    assert proc.returncode == 0, proc.stderr
    assert before == after
    payload = json.loads(proc.stdout)
    assert payload["read_only"] is True


def test_ppe_manifest_running_without_active_run_is_stale(tmp_path: Path) -> None:
    from scripts.founder_portfolio import collect_portfolio

    repo = _minimal_repo(tmp_path)
    _write_json(
        repo / "docs/SOP/ACTIVE_PHASE_MANIFEST.json",
        {"version": 1, "status": "RUNNING", "phasePlanPath": "docs/SOP/PHASE_PLANS/demo_relay.json"},
    )
    snapshot = collect_portfolio(repo)
    ppe = next(item for item in snapshot["pipelines"] if item["pipeline_id"] == "ppe")
    assert ppe["state"] == "BLOCKED"
    assert any("ACTIVE_RUN.json is missing" in item["message"] for item in ppe["stale_evidence"])
    assert ppe["running_work"] == []


def test_autobuilder_stale_runtime_is_not_counted_running(tmp_path: Path) -> None:
    from scripts.founder_portfolio import collect_portfolio

    repo = _minimal_repo(tmp_path)
    _write_json(
        repo / "artifacts/orchestrator/AUTOBUILDER_STATUS.json",
        {
            "version": 1,
            "as_of": "2000-01-01T00:00:00Z",
            "phase": "BUILD_IN_FLIGHT",
            "build": {"slice_id": "old-build"},
        },
    )
    snapshot = collect_portfolio(repo)
    autobuilder = next(item for item in snapshot["pipelines"] if item["pipeline_id"] == "autobuilder")
    assert autobuilder["state"] == "BLOCKED"
    assert autobuilder["running_work"] == []
    assert any(item["kind"] == "stale" for item in autobuilder["stale_evidence"])


def test_unsupported_build_next_does_not_dispatch() -> None:
    proc = subprocess.run(
        [sys.executable, str(REPO / "scripts/founder_portfolio.py"), "build", "next"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert proc.returncode == 2
    assert "unsupported or non-read-only command" in proc.stderr
