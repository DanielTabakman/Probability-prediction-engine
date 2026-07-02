"""Tests for ppe_burst_plan adaptive burst sizing."""

from __future__ import annotations

import json
from unittest.mock import patch

from scripts.ppe_burst_plan import compute_burst_plan, write_burst_plan
from scripts.ppe_context_bands import max_burst_cycles
from scripts.ppe_operator_status import VERDICT_IDE_BUILD, VERDICT_RUN_AUTO


def test_max_burst_cycles_bands() -> None:
    assert max_burst_cycles("NORMAL", director=True) == 3
    assert max_burst_cycles("NORMAL", director=False) == 2
    assert max_burst_cycles("WATCH", director=True) == 1
    assert max_burst_cycles("ESCALATE", director=True) == 0


def _write_plan(repo, rel: str, slices: list[dict]) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "chapterId": "test_ch",
                "sprintSpecPath": "docs/SOP/SPRINT_TEST.md",
                "slices": slices,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    spec = repo / "docs/SOP/SPRINT_TEST.md"
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_text("\n".join(["# Test"] + ["line"] * 50) + "\n", encoding="utf-8")
    sop = repo / "docs/SOP"
    sop.mkdir(parents=True, exist_ok=True)
    (sop / "PHASE_QUEUE.json").write_text(json.dumps({"version": 1, "items": []}), encoding="utf-8")
    (sop / "AGENT_STEERING_V1.json").write_text(json.dumps({"version": 1}), encoding="utf-8")


def test_compute_burst_plan_normal_caps_by_remaining(tmp_path) -> None:
    plan_rel = "docs/SOP/PHASE_TEST.json"
    _write_plan(
        tmp_path,
        plan_rel,
        [
            {"sliceId": "Slice-A"},
            {"sliceId": "Slice-B"},
            {"sliceId": "Slice-C", "closeout": {"job": "x"}},
        ],
    )
    status = {
        "verdict": VERDICT_IDE_BUILD,
        "phase_plan_path": plan_rel,
        "guard": {"reason": "PRODUCT_BLOCKED", "detail": "blocked [Slice-A]"},
        "blocker": "PRODUCT_BLOCKED",
    }
    with patch(
        "scripts.ppe_loop_host_guard.loop_host_start_allowed",
        return_value=(False, "not_loop_host", ""),
    ):
        with patch("scripts.ppe_burst_plan.run_preflight") as mock_pf:
            mock_pf.return_value = {"overall_band": "NORMAL", "slice_count": 3}
            plan = compute_burst_plan(tmp_path, status)
    assert plan["remaining_count"] == 2
    assert plan["max_cycles"] == 2
    assert plan["use_director"] is True
    assert plan["burst_allowed"] is True
    assert "Adaptive burst" in plan["prompt"]


def test_compute_burst_plan_watch_limits_to_one(tmp_path) -> None:
    plan_rel = "docs/SOP/PHASE_TEST.json"
    _write_plan(tmp_path, plan_rel, [{"sliceId": "Slice-A"}, {"sliceId": "Slice-B"}])
    status = {
        "verdict": VERDICT_IDE_BUILD,
        "phase_plan_path": plan_rel,
        "guard": {"reason": "PRODUCT_BLOCKED", "detail": "[Slice-A]"},
    }
    with patch("scripts.ppe_burst_plan.run_preflight") as mock_pf:
        mock_pf.return_value = {"overall_band": "WATCH", "slice_count": 2}
        plan = compute_burst_plan(tmp_path, status)
    assert plan["max_cycles"] == 1


def test_compute_burst_plan_escalate_blocks_burst(tmp_path) -> None:
    plan_rel = "docs/SOP/PHASE_TEST.json"
    _write_plan(tmp_path, plan_rel, [{"sliceId": "Slice-A"}])
    status = {
        "verdict": VERDICT_IDE_BUILD,
        "phase_plan_path": plan_rel,
        "guard": {"reason": "PRODUCT_BLOCKED", "detail": "[Slice-A]"},
    }
    with patch("scripts.ppe_burst_plan.run_preflight") as mock_pf:
        mock_pf.return_value = {"overall_band": "ESCALATE", "slice_count": 1}
        plan = compute_burst_plan(tmp_path, status)
    assert plan["max_cycles"] == 0
    assert plan["burst_allowed"] is False


def test_compute_burst_plan_run_auto_not_allowed(tmp_path) -> None:
    status = {"verdict": VERDICT_RUN_AUTO, "phase_plan_path": None, "guard": {}}
    plan = compute_burst_plan(tmp_path, status)
    assert plan["burst_allowed"] is False


def test_compute_burst_plan_closeout_direct_skips_director(tmp_path) -> None:
    plan_rel = "docs/SOP/PHASE_TEST.json"
    _write_plan(tmp_path, plan_rel, [{"sliceId": "Slice-A", "closeout": {"job": "x"}}])
    status = {
        "verdict": "RUN_LOCAL",
        "phase_plan_path": plan_rel,
        "guard": {"reason": "IDE_MARKER_OK"},
        "chapter_mode": {"mode": "CLOSEOUT_ONLY", "do_not_rebuild": True},
        "vm_trust": {"wait_for_vm": False},
    }
    with patch("scripts.ppe_burst_plan.run_preflight") as mock_pf:
        mock_pf.return_value = {"overall_band": "NORMAL", "slice_count": 1}
        plan = compute_burst_plan(tmp_path, status)
    assert plan["use_director"] is False
    assert plan["direct_action"] == "DESKTOP_CONTINUE.cmd --no-pause"
    assert "skip @ppe-director" in plan["prompt"]


def test_compute_burst_plan_vm_in_flight_waits(tmp_path) -> None:
    status = {
        "verdict": "RUN_LOCAL",
        "phase_plan_path": None,
        "guard": {},
        "vm_trust": {"wait_for_vm": True, "vm_phase": "FINISH_IN_FLIGHT"},
    }
    plan = compute_burst_plan(tmp_path, status)
    assert plan["burst_allowed"] is False
    assert plan["direct_action"] == "wait_for_vm"
    assert "do NOT SSH probe" in plan["prompt"]


def test_compute_burst_plan_lease_conflict_blocks(tmp_path, monkeypatch) -> None:
    from datetime import datetime, timedelta, timezone

    monkeypatch.chdir(tmp_path)
    now = datetime.now(timezone.utc)
    lease = {
        "lease_id": "lease-test",
        "worker_id": "codex-app",
        "branch": "control-plane/other",
        "exclusive": True,
        "path_globs": ["scripts/**"],
        "forbidden_globs": [],
        "expires_at": (now + timedelta(hours=1)).isoformat().replace("+00:00", "Z"),
    }
    (tmp_path / "artifacts/control_plane").mkdir(parents=True)
    (tmp_path / "artifacts/control_plane/ACTIVE_LEASE.json").write_text(json.dumps(lease) + "\n")

    plan_rel = "docs/SOP/PHASE_TEST.json"
    _write_plan(tmp_path, plan_rel, [{"sliceId": "Slice-A"}])
    status = {
        "verdict": VERDICT_IDE_BUILD,
        "phase_plan_path": plan_rel,
        "guard": {"reason": "PRODUCT_BLOCKED", "detail": "[Slice-A]"},
        "chapter_mode": {"mode": "IDE_BUILD"},
    }
    with patch("scripts.ppe_burst_plan.run_preflight") as mock_pf:
        mock_pf.return_value = {"overall_band": "NORMAL", "slice_count": 1}
        plan = compute_burst_plan(tmp_path, status)
    assert plan["burst_allowed"] is False
    assert plan["direct_action"] == "resolve_lease"


def test_prepare_operator_status_applies_env_before_collect(tmp_path, monkeypatch) -> None:
    from scripts.ppe_operator_status import prepare_operator_status

    monkeypatch.chdir(tmp_path)
    fake_status = {"verdict": VERDICT_IDE_BUILD, "guard": {"reason": "PRODUCT_BLOCKED"}}
    with patch("scripts.ppe_operator_config.apply_operator_env") as mock_env:
        with patch("scripts.ppe_operator_status.collect_operator_status", return_value=fake_status) as mock_collect:
            out = prepare_operator_status(tmp_path)
    mock_env.assert_called_once_with(tmp_path)
    mock_collect.assert_called_once_with(tmp_path)
    assert out["verdict"] == VERDICT_IDE_BUILD


def test_write_burst_plan(tmp_path) -> None:
    plan = {"max_cycles": 2, "verdict": VERDICT_IDE_BUILD}
    path = write_burst_plan(tmp_path, plan)
    assert path.is_file()
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["max_cycles"] == 2
