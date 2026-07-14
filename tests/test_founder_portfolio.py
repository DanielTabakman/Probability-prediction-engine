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
    (tmp_path / "config").mkdir(parents=True)
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
    env.pop("MSOS_AUTOBUILDER_STATUS_ROOT", None)
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


def test_autobuilder_external_source_unavailable_does_not_read_ppe_artifact(tmp_path: Path, monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _minimal_repo(tmp_path)
    _write_json(
        repo / "artifacts/orchestrator/AUTOBUILDER_STATUS.json",
        {
            "version": 1,
            "as_of": "2099-01-01T00:00:00Z",
            "phase": "BUILD_IN_FLIGHT",
            "build": {"slice_id": "must-not-read-from-ppe"},
        },
    )
    snapshot = collect_portfolio(repo)
    autobuilder = next(item for item in snapshot["pipelines"] if item["pipeline_id"] == "autobuilder")
    assert autobuilder["state"] == "BLOCKED"
    assert autobuilder["native_state"] == "EXTERNAL_SOURCE_UNAVAILABLE"
    assert autobuilder["running_work"] == []
    assert any("PPE checkout is not a fallback" in item.get("message", "") for item in autobuilder["stale_evidence"])


def test_autobuilder_stale_external_runtime_is_not_counted_running(tmp_path: Path, monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    repo = _minimal_repo(tmp_path / "ppe")
    external = tmp_path / "msos-autobuilder"
    _write_json(
        external / "artifacts/orchestrator/AUTOBUILDER_STATUS.json",
        {
            "version": 1,
            "as_of": "2000-01-01T00:00:00Z",
            "phase": "BUILD_IN_FLIGHT",
            "build": {"slice_id": "old-build"},
        },
    )
    monkeypatch.setenv("MSOS_AUTOBUILDER_STATUS_ROOT", str(external))
    snapshot = collect_portfolio(repo)
    autobuilder = next(item for item in snapshot["pipelines"] if item["pipeline_id"] == "autobuilder")
    assert autobuilder["state"] == "BLOCKED"
    assert autobuilder["running_work"] == []
    assert any(item["kind"] == "stale" for item in autobuilder["stale_evidence"])


def test_ready_to_build_is_not_reported_as_queued(tmp_path: Path, monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _minimal_repo(tmp_path)
    _write_json(
        repo / "docs/SOP/PHASE_QUEUE.json",
        {
            "version": 1,
            "items": [
                {
                    "planPath": "docs/SOP/PHASE_PLANS/ppe_ready_relay.json",
                    "status": "READY",
                    "reason": "Ready but not dispatched",
                }
            ],
        },
    )
    snapshot = collect_portfolio(repo)
    ppe = next(item for item in snapshot["pipelines"] if item["pipeline_id"] == "ppe")
    assert [item["state"] for item in ppe["ready_work"]] == ["READY_TO_BUILD"]
    assert ppe["queued_work"] == []
    assert snapshot["capacity"]["ready"] == 1
    assert snapshot["capacity"]["queued"] == 0


def test_blocked_autobuilder_does_not_prevent_safe_ppe_recommendation(tmp_path: Path, monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _minimal_repo(tmp_path)
    _write_json(
        repo / "docs/SOP/PHASE_QUEUE.json",
        {
            "version": 1,
            "items": [
                {
                    "planPath": "docs/SOP/PHASE_PLANS/ppe_safe_relay.json",
                    "status": "READY",
                    "reason": "Safe PPE work",
                    "priority": "medium",
                }
            ],
        },
    )
    snapshot = collect_portfolio(repo)
    assert snapshot["recommended_next_action"]["pipeline_id"] == "ppe"
    assert snapshot["recommended_next_action"]["state"] == "READY_TO_BUILD"


def test_manual_frontier_files_are_not_native_runtime(tmp_path: Path, monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _minimal_repo(tmp_path)
    snapshot = collect_portfolio(repo)
    ppe = next(item for item in snapshot["pipelines"] if item["pipeline_id"] == "ppe")
    manifest_evidence = next(item for item in ppe["evidence"] if item["source"] == "docs/SOP/ACTIVE_PHASE_MANIFEST.json")
    assert manifest_evidence["kind"] == "manual"


def test_deterministic_selection_uses_priority_then_tie_break(tmp_path: Path, monkeypatch) -> None:
    from scripts.founder_portfolio import collect_portfolio

    monkeypatch.delenv("MSOS_AUTOBUILDER_STATUS_ROOT", raising=False)
    repo = _minimal_repo(tmp_path)
    _write_json(
        repo / "docs/SOP/PHASE_QUEUE.json",
        {
            "version": 1,
            "items": [
                {
                    "planPath": "docs/SOP/PHASE_PLANS/z_medium_relay.json",
                    "status": "READY",
                    "reason": "Medium work",
                    "priority": "medium",
                },
                {
                    "planPath": "docs/SOP/PHASE_PLANS/a_high_relay.json",
                    "status": "READY",
                    "reason": "High work",
                    "priority": "high",
                },
            ],
        },
    )
    snapshot = collect_portfolio(repo)
    rec = snapshot["recommended_next_action"]
    assert rec["work_item_id"] == "a_high"
    assert "selection_explanation" in rec

    _write_json(
        repo / "docs/SOP/PHASE_QUEUE.json",
        {
            "version": 1,
            "items": [
                {
                    "planPath": "docs/SOP/PHASE_PLANS/z_equal_relay.json",
                    "status": "READY",
                    "reason": "Equal Z",
                    "priority": "high",
                },
                {
                    "planPath": "docs/SOP/PHASE_PLANS/a_equal_relay.json",
                    "status": "READY",
                    "reason": "Equal A",
                    "priority": "high",
                },
            ],
        },
    )
    snapshot = collect_portfolio(repo)
    # Age within the same priority class wins before deterministic ID tie-break.
    assert snapshot["recommended_next_action"]["work_item_id"] == "z_equal"


def test_deterministic_tie_breaker_is_stable() -> None:
    from scripts.founder_portfolio import _recommend_next

    base_selection = {
        "founder_priority_rank": 1,
        "deadline_rank": "9999-12-31T00:00:00+00:00",
        "dependency_unblock_value": 0,
        "age_index": 0,
    }
    snapshot = [
        {
            "pipeline_id": "zpipe",
            "state": "READY_TO_BUILD",
            "evidence": [{"kind": "manual"}],
            "running_work": [],
            "queued_work": [],
            "ready_work": [
                {
                    "work_item_id": "work",
                    "title": "Z work",
                    "evidence": "manual",
                    "selection": base_selection,
                }
            ],
        },
        {
            "pipeline_id": "apipe",
            "state": "READY_TO_BUILD",
            "evidence": [{"kind": "manual"}],
            "running_work": [],
            "queued_work": [],
            "ready_work": [
                {
                    "work_item_id": "work",
                    "title": "A work",
                    "evidence": "manual",
                    "selection": base_selection,
                }
            ],
        },
    ]
    assert _recommend_next(snapshot)["pipeline_id"] == "apipe"


def test_selection_deadline_and_dependency_unblock_order() -> None:
    from scripts.founder_portfolio import _recommend_next

    def work(work_item_id: str, *, deadline: str, unblock: int) -> dict:
        return {
            "work_item_id": work_item_id,
            "title": work_item_id,
            "evidence": "manual",
            "selection": {
                "founder_priority_rank": 1,
                "deadline_rank": deadline,
                "dependency_unblock_value": unblock,
                "age_index": 0,
            },
        }

    deadline_snapshot = [
        {
            "pipeline_id": "ppe",
            "state": "READY_TO_BUILD",
            "evidence": [{"kind": "manual"}],
            "running_work": [],
            "queued_work": [],
            "ready_work": [
                work("later", deadline="2030-01-02T00:00:00+00:00", unblock=99),
                work("earlier", deadline="2030-01-01T00:00:00+00:00", unblock=1),
            ],
        }
    ]
    assert _recommend_next(deadline_snapshot)["work_item_id"] == "earlier"

    unblock_snapshot = [
        {
            "pipeline_id": "ppe",
            "state": "READY_TO_BUILD",
            "evidence": [{"kind": "manual"}],
            "running_work": [],
            "queued_work": [],
            "ready_work": [
                work("low-unblock", deadline="2030-01-01T00:00:00+00:00", unblock=1),
                work("high-unblock", deadline="2030-01-01T00:00:00+00:00", unblock=5),
            ],
        }
    ]
    assert _recommend_next(unblock_snapshot)["work_item_id"] == "high-unblock"


def test_selection_fairness_prefers_pipeline_without_active_work() -> None:
    from scripts.founder_portfolio import _recommend_next

    selection = {
        "founder_priority_rank": 1,
        "deadline_rank": "9999-12-31T00:00:00+00:00",
        "dependency_unblock_value": 0,
        "age_index": 0,
    }
    snapshot = [
        {
            "pipeline_id": "busy",
            "state": "READY_TO_BUILD",
            "evidence": [{"kind": "manual"}],
            "running_work": [{"work_item_id": "already-running"}],
            "queued_work": [],
            "ready_work": [{"work_item_id": "busy-next", "title": "busy", "evidence": "manual", "selection": selection}],
        },
        {
            "pipeline_id": "idle",
            "state": "READY_TO_BUILD",
            "evidence": [{"kind": "manual"}],
            "running_work": [],
            "queued_work": [],
            "ready_work": [{"work_item_id": "idle-next", "title": "idle", "evidence": "manual", "selection": selection}],
        },
    ]
    assert _recommend_next(snapshot)["pipeline_id"] == "idle"


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
